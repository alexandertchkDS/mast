# -*- coding: utf-8 -*-
import random

import torch.nn.functional as F
import torch.nn

from ...utils.nn import get_rnn_hidden_state
from ..attention import HierarchicalAttention, HierarchicalAttentionCoverage, UniformAttention, get_attention
from .. import Fusion
from . import ConditionalDecoder
import sys

class ConditionalMM3DecoderCoverage(ConditionalDecoder):
    """A conditional multimodal decoder with 3-level multimodal attention."""
    def __init__(self, fusion_type='concat', fusion_activ=None,
                 aux_ctx_name='image', ter_ctx_name='audio', mm_att_type='md-dd',
                 persistent_dump=False, **kwargs):
        super().__init__(**kwargs)
        self.aux_ctx_name = aux_ctx_name
        self.ter_ctx_name = ter_ctx_name
        self.mm_att_type = mm_att_type
        self.persistent_dump = persistent_dump
        self.visualize = False   # Set this to True during testing time

        if self.mm_att_type == 'uniform':
            # Dummy uniform attention
            self.shared_dec_state = False
            self.shared_att_mlp = False
        else:
            # Parse attention type
            att_str = sorted(self.mm_att_type.lower().split('-'))
            assert len(att_str) == 2 and att_str[0][0] == 'd' and att_str[1][0] == 'm', \
                "att_type should be m[d|i]-d[d-i]"
            # Independent <d>ecoder state means shared dec state
            self.shared_dec_state = att_str[0][1] == 'i'

            # Independent <m>odality means sharing the mlp in the MLP attention
            self.shared_att_mlp = att_str[1][1] == 'i'

            # Sanity check
            if self.shared_att_mlp and self.att_type != 'mlp':
                raise Exception("Shared attention requires MLP attention.")

        # Define (context) fusion operator
        self.fusion_type = fusion_type
        if fusion_type == "hierarchical":
            self.fusion_img = HierarchicalAttention(
                [self.hidden_size, self.hidden_size],
                self.hidden_size, self.hidden_size)

            self.fusion_aud = HierarchicalAttention(
                [self.hidden_size, self.hidden_size],
                self.hidden_size, self.hidden_size)

            self.fusion = HierarchicalAttentionCoverage(
                [self.hidden_size, self.hidden_size],
                self.hidden_size, self.hidden_size)
        else:   # TODO: Add two fusions here (for non-hierarchial)
            if self.att_ctx2hid:
                # Old behaviour
                fusion_inp_size = 2 * self.hidden_size
            else:
                fusion_inp_sizes = list(self.ctx_size_dict.values())
                if fusion_type == 'concat':
                    fusion_inp_size = sum(fusion_inp_sizes)
                else:
                    fusion_inp_size = fusion_inp_sizes[0]
            self.fusion = Fusion(
                fusion_type, fusion_inp_size, self.hidden_size,
                fusion_activ=fusion_activ)

        # Rename textual attention layer
        self.txt_att = self.att
        del self.att

        # Auxilary modality
        if self.mm_att_type == 'uniform':
            self.img_att = UniformAttention()
        else:
            # Visual attention over convolutional feature maps
            Attention = get_attention(self.att_type)
            #self.img_att = Attention(
            #    self.ctx_size_dict[self.aux_ctx_name], self.hidden_size,
            #    transform_ctx=self.transform_ctx, mlp_bias=self.mlp_bias,
            #    ctx2hid=self.att_ctx2hid,
            #    att_activ=self.att_activ,
            #    att_bottleneck=self.att_bottleneck)

            self.img_att = Attention(
                512, self.hidden_size,
                transform_ctx=self.transform_ctx, mlp_bias=self.mlp_bias,
                ctx2hid=self.att_ctx2hid,
                att_activ=self.att_activ,
                att_bottleneck=self.att_bottleneck)

        # Tertiary modality
        if self.mm_att_type == 'uniform':
            self.aud_att = UniformAttention()
        else:
            # Visual attention over audio features
            Attention = get_attention(self.att_type)
            #self.aud_att = Attention(
            #    self.ctx_size_dict[self.ter_ctx_name], self.hidden_size,
            #    transform_ctx=self.transform_ctx, mlp_bias=self.mlp_bias,
            #    ctx2hid=self.att_ctx2hid,
            #    att_activ=self.att_activ,
            #    att_bottleneck=self.att_bottleneck)

            self.aud_att = Attention(
                512, self.hidden_size,
                transform_ctx=self.transform_ctx, mlp_bias=self.mlp_bias,
                ctx2hid=self.att_ctx2hid,
                att_activ=self.att_activ,
                att_bottleneck=self.att_bottleneck)    

        # Tune multimodal attention type
        # TODO: Handle audio in case of independant
        if self.shared_att_mlp:
            # Modality independent
            self.txt_att.mlp.weight = self.img_att.mlp.weight
            self.txt_att.ctx2ctx.weight = self.img_att.ctx2ctx.weight

        if self.shared_dec_state:
            # Decoder independent
            self.txt_att.hid2ctx.weight = self.img_att.hid2ctx.weight

    def forward(self, ctx_dict, y, txt_input):
        """Computes the softmax outputs given source annotations `ctx_dict[self.ctx_name]`
        and ground-truth target token indices `y`. Only called during training.
        Applies coverage mechanism as well.

        Arguments:
            ctx_dict(dict): A dictionary of tensors that should at least contain
                the key `ctx_name` as the main source representation of shape
                S*B*ctx_dim`.
            y(Tensor): A tensor of `T*B` containing ground-truth target
                token indices for the given batch.
        """

        loss = 0.0

        # Get initial hidden state
        h = self.f_init(ctx_dict)

        # Initialize coverage
        coverage = None

        # are we doing scheduled sampling?
        sched = self.training and (random.random() > (1 - self.sched_sample))

        # Convert token indices to embeddings -> T*B*E
        # Skip <bos> now
        bos = self.get_emb(y[0], 0)
        log_p, h, coverage, coverage_loss = self.f_next(ctx_dict, bos, h, txt_input, coverage)
        loss += self.nll_loss(log_p, y[1])
        y_emb = self.get_emb(y[1:])

        for t in range(y_emb.shape[0] - 1):
            emb = self.emb(log_p.argmax(1)) if sched else y_emb[t]
            log_p, h, coverage, coverage_loss = self.f_next(ctx_dict, emb, h, txt_input, coverage)
            loss += self.nll_loss(log_p, y[t + 2]) + coverage_loss

        return {'loss': loss}

    def f_next(self, ctx_dict, y, h, txt_input, coverage):
        # Get hidden states from the first decoder (purely cond. on LM)
        h1_c1 = self.dec0(y, self._rnn_unpack_states(h))
        h1 = get_rnn_hidden_state(h1_c1)

        # Apply attention
        self.txt_alpha_t, txt_z_t = self.txt_att(
            h1.unsqueeze(0), *ctx_dict[self.ctx_name])
        self.img_alpha_t, img_z_t = self.img_att(
            h1.unsqueeze(0), *ctx_dict[self.aux_ctx_name])
        self.aud_alpha_t, aud_z_t = self.aud_att(
            h1.unsqueeze(0), *ctx_dict[self.ter_ctx_name])

        # Save for reg loss terms
        self.history['alpha_img'].append(self.img_alpha_t.unsqueeze(0))
        self.history['alpha_aud'].append(self.aud_alpha_t.unsqueeze(0))

        # Context will double dimensionality if fusion_type is concat
        # z_t should be compatible with hidden_size
        if self.fusion_type == "hierarchical":
            img_txt_h_att, img_txt_z_t = self.fusion_img([txt_z_t, img_z_t], h1.unsqueeze(0))
            aud_txt_h_att, aud_txt_z_t = self.fusion_aud([txt_z_t, aud_z_t], h1.unsqueeze(0))
            self.h_att, z_t, coverage = self.fusion([img_txt_z_t, aud_txt_z_t], h1.unsqueeze(0), coverage)
            coverage_loss = torch.sum(torch.min(self.h_att.reshape(-1,1), coverage.reshape(-1,1)), 1) 
            coverage_loss = torch.sum(coverage_loss)
        else:   #TODO: Handle this case for audio
            z_t = self.fusion(txt_z_t, img_z_t)

        if not self.training and self.persistent_dump:
            # For test-time activation debugging
            self.persistence['z_t'].append(z_t.t().cpu().numpy())
            self.persistence['txt_z_t'].append(txt_z_t.t().cpu().numpy())
            self.persistence['img_z_t'].append(img_z_t.t().cpu().numpy())
            self.persistence['aud_z_t'].append(aud_z_t.t().cpu().numpy())

        # Run second decoder (h1 is compatible now as it was returned by GRU)
        h2_c2 = self.dec1(z_t, h1_c1)
        h2 = get_rnn_hidden_state(h2_c2)

        # This is a bottleneck to avoid going from H to V directly
        logit = self.hid2out(self.out_merge_fn(h2, y, z_t))

        # Apply dropout if any
        if self.dropout_out > 0:
            logit = self.do_out(logit)

        # Transform logit to T*B*V (V: vocab_size)
        # Compute log_softmax over token dim
        log_p = F.log_softmax(self.out2prob(logit), dim=-1)

        if self.visualize:
            # Return log probs and new hidden states
            return log_p, self._rnn_pack_states(h2_c2), self.h_att, img_txt_h_att, aud_txt_h_att, self.txt_alpha_t, self.img_alpha_t, self.aud_alpha_t
        else:
            return log_p, self._rnn_pack_states(h2_c2)
