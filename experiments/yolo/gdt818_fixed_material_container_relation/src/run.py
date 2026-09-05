#!/usr/bin/env python3
"""Fixed 2x2 word trials and full contexts; source checks are not translation."""
import argparse
import csv
import importlib.util
import io
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
EXP = Path(__file__).resolve().parent.parent
ROOT = EXP.parents[2]
READERS = ['zl3b_clean','it2a_clean','rf1b_clean']
loader = importlib.util.spec_from_file_location('guard', ROOT /
    'experiments/yolo/gdt812_additional_page_semantic_bridge/src/family_probe.py')
guard = importlib.util.module_from_spec(loader)
loader.loader.exec_module(guard)


def enc(x):
    return json.dumps(x, ensure_ascii=False)


def table(rows):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def build():
    spec = json.loads((EXP/'src/SPEC.json').read_text())
    old = json.loads((ROOT/spec['scope_spec']).read_text())
    inherited = json.loads((ROOT/spec['inherited_spec']).read_text())
    scope = old['source_selectors']
    guard.require(len(scope)==len(set(scope))==39 and spec['sealed_data']==['f84','f84r'], 'Scope/seals')
    rows,g1 = guard.query('transcription/voynich_zl3b_lines.tsv',
        ['page','locus','kind','paragraph_start','paragraph_end','eva_clean'], scope)
    cross,g2 = guard.query('transcription/voynich_cross_transcription_lines.tsv', ['page','locus',*READERS],scope)
    by = {r['locus']:r for r in rows}
    guard.require(set(by)=={r['locus'] for r in cross}, 'Reader coverage')
    for c in cross:
        r=by[c['locus']]
        guard.require(r['page']==c['page'] and r['eva_clean']==c[READERS[0]], 'Reader join')
        r.update({rd:c[rd] for rd in READERS})
    blocks, current = [], []
    for r in rows:
        if r['kind']=='P':
            if current and (r['paragraph_start']=='1' or current[0]['page']!=r['page']):
                blocks.append(current)
                current=[]
            current.append(r)
            if r['paragraph_end']=='1':
                blocks.append(current)
                current=[]
        else:
            blocks.append([r])
    if current:
        blocks.append(current)
    position={r['locus']:i for i,r in enumerate(rows)}
    blocks.sort(key=lambda b:position[b[0]['locus']])
    block_for = {r['locus']: b for b in blocks for r in b}
    focal = []
    for page,start,end in spec['focal_paragraphs']:
        b=block_for[f'{page}.{start}']
        guard.require([r['locus'] for r in b]==[f'{page}.{n}' for n in range(start,end+1)], 'Complete focal P')
        focal += [r['locus'] for r in b]
    hits, tails = [], []
    tail_pairs=list(zip(spec['tail'],spec['tail'][1:]))
    for r in rows:
        for rd in READERS:
            words=r[rd].split()
            for i,w in enumerate(words):
                for distance in spec['contact_distances']:
                    j=i+distance
                    if j<len(words) and {w,words[j]}==set(spec['contact_words']):
                        hits.append(dict(page=r['page'],locus=r['locus'],reader=rd,
                            pattern=f'CONTACT_DISTANCE_{distance}',first_ordinal=i+1,last_ordinal=j+1,
                            words_json=enc(words[i:j+1])))
                if i+1<len(words) and w==words[i+1]==spec['duplicate_whole']:
                    hits.append(dict(page=r['page'],locus=r['locus'],reader=rd,pattern='EXACT_CHEDY_DUPLICATE',
                        first_ordinal=i+1,last_ordinal=i+2,words_json=enc(words[i:i+2])))
                if i+1<len(words) and (w,words[i+1]) in tail_pairs:
                    tails.append(dict(page=r['page'],locus=r['locus'],reader=rd,first_ordinal=i+1,
                        last_ordinal=i+2,words_json=enc(words[i:i+2])))
    trigger={r['locus'] for r in hits}
    selected=[b for b in blocks if any(r['locus'] in trigger or r['locus'] in focal for r in b)]
    guard.require(all(b[0]['kind']!='P' or (b[0]['paragraph_start']=='1' and
        b[-1]['paragraph_end']=='1') for b in selected), 'Selected P must have both source boundaries')
    metadata, contexts, trials, document=[],[],[],['# GDT818 complete comparison reader','',
        'Exact source paragraphs / entire non-P records; no decoded sentence boundaries.',
        'R wholes fixed; ol unknown. Four trial worlds are alternatives, not four votes.','']
    base=old['shared_hypotheses'] | inherited['models']['R_JOINT']
    guard.require('ol' not in base and not (set(spec['tail']) & set(base)), 'Unknown tails and ol')
    for b in selected:
        bid=b[0]['locus']+'--'+b[-1]['locus']
        metadata.append(dict(block_id=bid,page=b[0]['page'],kind=b[0]['kind'],first=b[0]['locus'],
            last=b[-1]['locus'],loci=len(b),focal=int(b[0]['locus'] in focal),
            triggers_json=enc([r['locus'] for r in b if r['locus'] in trigger]),
            tokens_json=enc({rd:sum(len(r[rd].split()) for r in b) for rd in READERS})))
        document += ['## '+bid,'']
        for r in b:
            contexts.append(dict(block_id=bid,**{k:r[k] for k in ['page','locus','kind','paragraph_start','paragraph_end']},
                readings_json=enc({rd:r[rd] for rd in READERS})))
            document += [r['locus']+' ZL: `'+r[READERS[0]]+'`']
            document += [rd+': `'+r[rd]+'`' for rd in READERS[1:] if r[rd]!=r[READERS[0]]]
            document += ['']
            if r['locus'] in focal:
                for rd in READERS:
                    for world,delta in spec['worlds'].items():
                        mapping=base|delta
                        trials.append(dict(page=r['page'],locus=r['locus'],reader=rd,world=world,
                            source_text=r[rd],literal_json=enc([mapping.get(w,'['+w+']') for w in r[rd].split()]),
                            confidence=spec['confidence']))
    tail_loci={r['locus'] for r in tails}
    tail_rows=[dict(page=r['page'],locus=r['locus'],kind=r['kind'],paragraph_start=r['paragraph_start'],
        paragraph_end=r['paragraph_end'],readings_json=enc({rd:r[rd] for rd in READERS})) for r in rows if r['locus'] in tail_loci]
    result=dict(experiment_id='GDT818',status='FIXED_FOUR_WORLDS_NOT_TRANSLATION',source_selectors=scope,
        source_loci=len(rows),focal_loci=len(focal),literal_rows=len(trials),context_blocks=len(selected),
        context_loci=len(contexts),contact_rows=len(hits),contact_loci=len(trigger),
        tail_pair_rows=len(tails),tail_loci=len(tail_rows),guarded_queries=[g1,g2],
        fixed_senses=spec['fixed_senses'],sealed_data=spec['sealed_data'],new_admissions=0,
        dictionary_changed=False,confirmed_lexemes=0,confirmed_plaintext_clauses=0,meanings_validated=False,
        selection_limit='SAME_RECORD_FIXED_DISTANCE_CONTACTS; NOT_ALL_CHEDY_OR_TAIL_SINGLETONS',
        literal_limit='FOCAL_35_LOCI_ONLY; CONTEXTS_AND_TAIL_ROWS_RETAIN_SOURCE_ALL_READERS')
    return {'BLOCKS.tsv':table(metadata),'CONTEXTS.tsv':table(contexts),'HITS.tsv':table(hits),
        'TAIL_HITS.tsv':table(tails),'TAIL_ROWS.tsv':table(tail_rows),'LITERAL_TRIALS.tsv':table(trials),
        'FULL_READER.md':'\n'.join(document).rstrip()+'\n','RESULT.json':json.dumps(result,indent=2,sort_keys=True)+'\n'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check',action='store_true')
    args=p.parse_args()
    outputs=build()
    for name,content in outputs.items():
        path=EXP/'artifacts'/name
        if args.check:
            guard.require(path.read_text()==content,'Replay differs: '+name)
        else:
            path.write_text(content)
    r=json.loads(outputs['RESULT.json'])
    print(enc({k:r[k] for k in ['status','context_blocks','context_loci','contact_loci','tail_loci','literal_rows']}))


if __name__=='__main__':
    main()
