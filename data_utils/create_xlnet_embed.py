import os
import sys
import numpy as np
from tqdm import tqdm

import torch
from transformers import *

def generate_embeddings(src_dir, tgt_dir, pretrained_weights='xlnet-base-cased'):
    model_class, tokenizer_class = XLNetModel, XLNetTokenizer

    os.makedirs(tgt_dir, exist_ok=True)

    # Load pretrained model/tokenizer
    tokenizer = tokenizer_class.from_pretrained(pretrained_weights)
    model = model_class.from_pretrained(pretrained_weights)

    # Encode text
    print("Converting Directory : ", src_dir)
    try:
        txt_files = os.listdir(src_dir)
    except Exception as e:
        print("Error in opening directory with error : " + str(e))
        sys.exit()
    for cnt, txt_file in tqdm(enumerate(txt_files), 'Converting...'):
        vid_id, _ = os.path.splitext(txt_file)
        fname = vid_id + '.npy'
        with open(os.path.join(src_dir, txt_file), 'r') as f:
            txt = f.read()
        input_ids = torch.tensor([tokenizer.encode(txt, add_special_tokens=True)])  # Add special tokens takes care of adding [CLS], [SEP], <s>... tokens in the right way for each model.
        with torch.no_grad():
            last_hidden_states = model(input_ids)[0]  # Models outputs are now tuples
        embed = last_hidden_states.squeeze(0)
        embed = embed.numpy()
        np.save(os.path.join(tgt_dir, fname), embed)
    print("Completed generating Embedding")

source_text_path = '/home/alexandrtchk/VSCode/multimodal/data-1000-items/not_split/text'
source_folders = ['desc', 'tran']
tgt_path = '/home/alexandrtchk/VSCode/multimodal/data-1000-items/not_split/text_npy'

for folder in source_folders:
    src_dir = os.path.join(source_text_path, folder)
    tgt_dir = os.path.join(tgt_path, folder)
    generate_embeddings(src_dir, tgt_dir, pretrained_weights='xlnet-base-cased')