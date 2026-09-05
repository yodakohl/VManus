#!/usr/bin/env python3
"""Compact projection of the already frozen, independently validated evaluation."""
import argparse
import json
from pathlib import Path

EXP=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    e=json.loads((EXP/'artifacts/EVALUATION.json').read_text())
    rows=[]
    for r in e['results']:
        m=r['recovery']
        rows.append({'world_id':r['world_id'],'condition':r['condition'],'arm':r['arm'],
                     'word_accuracy':m['all_words']['word_accuracy'],
                     'character_accuracy':m['all_words']['character_accuracy'],
                     'novel_form_accuracy':m['novel_composed_forms']['word_accuracy'],
                     'novel_lemma_accuracy':m['novel_composed_lemmas']['word_accuracy'],
                     'macro_or_novel_accuracy':m['macro_or_novel_composed']['word_accuracy'],
                     'exact_paragraphs':m['exact_paragraphs'],'paragraphs':len(m['paragraphs']),
                     'key':m['key'],'order_p':r.get('context_test',{}).get('upper_p'),
                     'selected_minus_oracle':r['selected_minus_oracle']})
    result={'schema':'GDT832_COMPACT_RESULT_V1','status':e['status'],
            'preregistration_commit':'8beefeec1db6a17e1e3e816159d622d617782d48',
            'fit_lock_sha256':e['fit_lock_sha256'],'recovery_pass':e['recovery_pass'],
            'joint_gain_pass':e['joint_gain_pass'],'context_discrimination_pass':e['context_discrimination_pass'],
            'gains':e['gains'],'rows':rows,
            'claim_ceiling':'Known historical control architecture only. No Voynich fit or translation; three keys share content; partial attested-family factor only.'}
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    output=EXP/'artifacts/RESULT.json'
    if args.check:
        assert output.read_text()==text,'Compact result differs from frozen evaluation'
    else:
        output.write_text(text)
    print(json.dumps({'status':result['status'],'rows':len(rows),'checked':args.check}))


if __name__=='__main__':
    main()
