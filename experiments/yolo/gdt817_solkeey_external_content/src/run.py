#!/usr/bin/env python3
"""Complete vapour paragraphs and bounded challenges; no decoder."""
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
READERS = ['zl3b_clean', 'it2a_clean', 'rf1b_clean']
loader = importlib.util.spec_from_file_location('source_guard', ROOT /
    'experiments/yolo/gdt812_additional_page_semantic_bridge/src/family_probe.py')
guard = importlib.util.module_from_spec(loader)
loader.loader.exec_module(guard)


def table(rows):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def encoded(obj):
    return json.dumps(obj, ensure_ascii=False)


def build():
    spec = json.loads((EXP / 'src/SPEC.json').read_text())
    previous = json.loads((ROOT / spec['inherited_model_spec']).read_text())
    older = json.loads((ROOT / 'experiments/yolo/gdt813_f17_content_word_transfer/src/SPEC.json').read_text())
    scope = older['source_selectors']
    guard.require(len(scope) == len(set(scope)) == 39 and set(spec['pages']) <= set(scope)
                  and spec['sealed_data'] == ['f84','f84r'], 'Admission and seals')
    rows, g1 = guard.query('transcription/voynich_zl3b_lines.tsv',
        ['page','locus','kind','paragraph_start','paragraph_end','eva_clean'], scope)
    cross, g2 = guard.query('transcription/voynich_cross_transcription_lines.tsv',
                           ['page','locus',*READERS], scope)
    by = {r['locus']:r for r in rows}
    guard.require(set(by) == {r['locus'] for r in cross}, 'Reader coverage')
    for alt in cross:
        row = by[alt['locus']]
        guard.require(row['page'] == alt['page'] and row['eva_clean'] == alt[READERS[0]], 'Reader join')
        row.update({rd:alt[rd] for rd in READERS})

    def record(row):
        return {key:row[key] for key in ['page','locus','kind','paragraph_start','paragraph_end']} | {
            'readings_json':encoded({rd:row[rd] for rd in READERS})}

    focal, counts, trials = [], [], []
    for page, start, end in spec['paragraphs']:
        block = [by[f'{page}.{n}'] for n in range(start,end+1)]
        guard.require(all(r['kind']=='P' for r in block) and block[0]['paragraph_start']=='1'
                      and block[-1]['paragraph_end']=='1' and all(r['paragraph_start']=='0' for r in block[1:])
                      and all(r['paragraph_end']=='0' for r in block[:-1]), 'Complete P')
        focal += block
        counts.append({'page':page,'first':block[0]['locus'],'last':block[-1]['locus'], 'loci':len(block),
            'tokens':{rd:sum(len(r[rd].split()) for r in block) for rd in READERS}})
        for r in block:
            for rd in READERS:
                for name, delta in previous['models'].items():
                    base = older['shared_hypotheses'] | delta
                    extended = base | spec['additions']
                    words = r[rd].split()
                    trials.append({'page':page,'locus':r['locus'],'reader':rd,'world':name,
                        'source_text':r[rd], 'base_json':encoded([base.get(w,'['+w+']') for w in words]),
                        'extended_json':encoded([extended.get(w,'['+w+']') for w in words]),
                        'confidence':'C0_UNCONFIRMED'})
    page_rows = [r for r in rows if r['page'] in spec['pages']]
    document = ['# GDT817 complete three-page source reader','',
                'All P/L records and differing alternate readings; no decoded sentence boundaries.','']
    for r in page_rows:
        document.append(f"{r['locus']} [{r['kind']}; start={r['paragraph_start']}; end={r['paragraph_end']}] ZL: `{r[READERS[0]]}`")
        document.extend(rd+': `'+r[rd]+'`' for rd in READERS[1:] if r[rd]!=r[READERS[0]])
        document.append('')
    challenges, inventory = [], []
    nouns = set(previous['new_wholes'])
    for r in rows:
        for rd in READERS:
            words = r[rd].split()
            for word in spec['additions']:
                if word in words:
                    inventory.append({'page':r['page'],'locus':r['locus'],'kind':r['kind'],
                        'reader':rd,'whole':word,'ordinals_json':encoded([i+1 for i,w in enumerate(words) if w==word])})
            hits = []
            for i, word in enumerate(words):
                if i+1<len(words) and word in spec['additions'] and words[i+1]==word:
                    hits.append({'pattern':'EXACT_'+word.upper()+'_DUPLICATE','first_ordinal':i+1,'words':words[i:i+2]})
                if i+2<len(words) and word in nouns and words[i+1]=='chedy' and words[i+2] in nouns:
                    hits.append({'pattern':'KNOWN_NOUN_CHEDY_KNOWN_NOUN','first_ordinal':i+1,'words':words[i:i+3]})
                if r['kind']!='P' and word in spec['additions']:
                    hits.append({'pattern':'NON_P_ADDITION','first_ordinal':i+1,'words':[word]})
            if hits:
                challenges.append({'page':r['page'],'locus':r['locus'],'kind':r['kind'],'reader':rd,
                    'source_text':r[rd],'hits_json':encoded(hits)})
    result = {'experiment_id':'GDT817','status':'CONCRETE_BECOMES_OR_TRIALS_NOT_TRANSLATION',
        'source_selectors':scope,'source_loci':len(rows),'page_reader_loci':len(page_rows),
        'focal_loci':len(focal),'literal_rows':len(trials),'paragraphs':counts,
        'challenge_rows':len(challenges),'challenge_loci':len({r['locus'] for r in challenges}),
        'addition_inventory_rows':len(inventory),'guarded_queries':[g1,g2],
        'joint_quality_frame':previous['joint_quality_frame'],'fixed_senses':spec['fixed_senses'],
        'challenge_coverage':'PREDECLARED_PATTERNS_NOT_ALL_OCCURRENCES_SEMANTICALLY_READ',
        'sealed_data':['f84','f84r'],'new_admissions':0,'dictionary_changed':False,
        'confirmed_lexemes':0,'confirmed_plaintext_clauses':0,'meanings_validated':False}
    return {'PAGES.tsv':table([record(r) for r in page_rows]), 'FOCAL.tsv':table([record(r) for r in focal]),
            'LITERAL_TRIALS.tsv':table(trials), 'CHALLENGES.tsv':table(challenges),
            'ADDITION_INVENTORY.tsv':table(inventory),
            'FULL_READER.md':'\n'.join(document).rstrip()+'\n',
            'RESULT.json':json.dumps(result,indent=2,sort_keys=True)+'\n'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check',action='store_true')
    args = p.parse_args()
    artifacts = build()
    for name, content in artifacts.items():
        path = EXP/'artifacts'/name
        if args.check:
            guard.require(path.read_text()==content,'Replay differs: '+name)
        else:
            path.write_text(content)
    result = json.loads(artifacts['RESULT.json'])
    print(json.dumps({k:result[k] for k in ['status','focal_loci','page_reader_loci','literal_rows','challenge_loci']}))


if __name__ == '__main__':
    main()
