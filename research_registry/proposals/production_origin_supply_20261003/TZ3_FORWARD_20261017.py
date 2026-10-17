#!/usr/bin/env python3
"""RAW partial source-writing example. No inverse decoder or word meanings."""
from pathlib import Path
import json
D=Path(__file__).resolve().parent

def forward(text):
    word=text.lower().replace('ḳ','k').replace('ı','i')
    out=[]
    for j,c in enumerate(word):
        if c=='k':out.append('q' if j==0 else 'k')
        elif c=='o':out.append('o')
        elif c=='s':out.append('e')
        elif c in 'dt':out.append('d')
        elif c in 'ui':out.append('y' if j==len(word)-1 else 'e')
        else:raise ValueError('Unassigned source character: '+repr(c))
    return ''.join(out)

if __name__=='__main__':
    raw=json.loads((D/'TZ3_PARTIAL_WRITER_RAW_20261017.json').read_text())['design']
    print(json.dumps({'status':'RAW_SOURCE_FORWARD_OUTPUTS_NOT_A_READING','fitted':[{'source':r['source'],'output':forward(r['source']),'support':r['support']} for r in raw['fitted_inputs']],'additional_constructed_strings':[{'source':r['source'],'output':forward(r['source']),'support':r['support']} for r in raw['additional_inputs']],'native_meanings_assigned':0},ensure_ascii=False,indent=2))
