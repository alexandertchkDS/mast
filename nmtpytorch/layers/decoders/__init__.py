from .conditional import ConditionalDecoder
from .simplegru import SimpleGRUDecoder
from .conditionalmm import ConditionalMMDecoder
from .multisourceconditional import MultiSourceConditionalDecoder
from .conditionalmm3_coverage import ConditionalMM3DecoderCoverage
from .xu import XuDecoder
from .switchinggru import SwitchingGRUDecoder
from .vector import VectorDecoder


def get_decoder(type_):
    """Only expose ones with compatible __init__() arguments for now."""
    return {
        'cond': ConditionalDecoder,
        'simplegru': SimpleGRUDecoder,
        'condmm': ConditionalMMDecoder,
        'vector': VectorDecoder,
        'condmm3cov':ConditionalMM3DecoderCoverage,
    }[type_]
