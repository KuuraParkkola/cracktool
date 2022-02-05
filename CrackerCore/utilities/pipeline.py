from typing import Dict
from CrackerCore.Hasher import Hasher
from CrackerCore.WordSource import WordSource
from CrackerCore.variators.symbol import build_sym_variator
from CrackerCore.variators.substitution import build_subs_variator
from CrackerCore.variators.number import build_numr_variator
from CrackerCore.variators.number import build_numd_variator
#from CrackerCore.variators.capital import build_caps_variator


def build_pipeline(word_source: WordSource, pipeline_args: Dict, hasher: Hasher):
    vari_map = {
        'sym': build_sym_variator,
        'subs': build_subs_variator,
        'numr': build_numr_variator,
        'numd': build_numd_variator,
    }

    pipeline = [word_source]
    pipeline.extend([vari_map[vari[0]](vari[1:]) for vari in pipeline_args['variators']])

    for idx in range(len(pipeline) - 1):
        pipeline[idx].use_variator(pipeline[idx+1])

    hash_sources = pipeline_args['hash_sources']
    for idx in range(len(pipeline)):
        if idx in hash_sources:
            pipeline[idx].use_hasher(hasher)

    return word_source
