#!/usr/bin/env python3
"""Post-reading concrete tail proposals; bounded exact-whole contexts only."""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
EXP=Path(__file__).resolve().parent.parent
ROOT=EXP.parents[2]
loader=importlib.util.spec_from_file_location('local_source_tools',EXP/'src/run.py')
m=importlib.util.module_from_spec(loader)
loader.loader.exec_module(m)
FOCUS=['sheedy','chedaiin','chealy']
PROPOSALS={'IF_AIR_IS_COLD':{'sheedy':'wenn?','qokaiin':'Luft?','chedaiin':'ist?','chealy':'kalt?'},
           'WITH_UNNAMED_CONTENT':{'sheedy':'mit?'}}


def build():
    scope=json.loads((ROOT/'experiments/yolo/gdt813_f17_content_word_transfer/src/SPEC.json').read_text())['source_selectors']
    rows,g1=m.guard.query('transcription/voynich_zl3b_lines.tsv',
        ['page','locus','kind','paragraph_start','paragraph_end','eva_clean'],scope)
    cross,g2=m.guard.query('transcription/voynich_cross_transcription_lines.tsv',['page','locus',*m.READERS],scope)
    by={r['locus']:r for r in rows}
    contexts, trials=[],[]
    for c in cross:
        r=by[c['locus']]
        m.guard.require(r['page']==c['page'] and r['eva_clean']==c[m.READERS[0]],'Source join')
        if not any(set(c[rd].split()) & set(FOCUS) for rd in m.READERS):
            continue
        contexts.append({k:r[k] for k in ['page','locus','kind','paragraph_start','paragraph_end']} |
            {'readings_json':m.enc({rd:c[rd] for rd in m.READERS})})
        for rd in m.READERS:
            for proposal, mapping in PROPOSALS.items():
                trials.append(dict(page=r['page'],locus=r['locus'],reader=rd,proposal=proposal,
                    source_text=c[rd],literal_json=m.enc([mapping.get(w,'['+w+']') for w in c[rd].split()]),
                    confidence='C0_COMPLETION_MOTIVATED_NOT_WORD_EVIDENCE'))
    result=dict(experiment_id='GDT818',status='POST_READING_CONTINUATION_TRIALS',focus_wholes=FOCUS,
        proposals=PROPOSALS,context_loci=len(contexts),literal_rows=len(trials),guarded_queries=[g1,g2],
        scope_limit='WHOLE_ROWS_NOT_ALL_PARAGRAPHS_OR_QOKAIIN_SINGLETONS',meanings_validated=False,
        new_admissions=0,dictionary_changed=False,confirmed_lexemes=0,sealed_data=['f84','f84r'])
    return {'CONTINUATION_CONTEXTS.tsv':m.table(contexts),'CONTINUATION_TRIALS.tsv':m.table(trials),
        'CONTINUATION_RESULT.json':json.dumps(result,indent=2,sort_keys=True)+'\n'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check',action='store_true')
    args=p.parse_args()
    outputs=build()
    for name,content in outputs.items():
        path=EXP/'artifacts'/name
        if args.check:
            m.guard.require(path.read_text()==content,'Continuation replay: '+name)
        else:
            path.write_text(content)
    r=json.loads(outputs['CONTINUATION_RESULT.json'])
    print(m.enc({k:r[k] for k in ['status','context_loci','literal_rows']}))


if __name__=='__main__':
    main()
