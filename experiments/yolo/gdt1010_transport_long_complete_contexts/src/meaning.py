from common import *
import itertools

def meanings(witness,s,g,independent=False):
    out=[]
    for vi,values in enumerate(itertools.product(*g['variants'].values())):
        variant=dict(zip(g['variants'],values));details=[replay(p,variant,s,independent) for p in witness['parses']]
        original=details[0]
        content=original.get('status')=='COHERENT' and len(original['cargo'])==3 and len(original['hazards'])==2 and any(p['consistent'] and len(p['trace'])==8 for p in original['paths'])
        coherent=content and all(p['status']=='COHERENT' for p in details[1:])
        out.append(dict(variant_index=vi,variant=variant,status='COHERENT_COMMON_READING' if coherent else 'SAMPLE_CONTRADICTION',original_full_content=bool(content),paragraphs=details))
    return out
