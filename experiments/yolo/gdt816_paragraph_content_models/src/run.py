#!/usr/bin/env python3
"""Whole-paragraph noun trials and exact external concordance; no decoder."""
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


def tsv(rows):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def build():
    spec = json.loads((EXP / 'src/SPEC.json').read_text())
    prior = json.loads((ROOT / 'experiments/yolo/gdt813_f17_content_word_transfer/src/SPEC.json').read_text())
    pages = prior['source_selectors']
    guard.require(len(set(pages)) == 39 and spec['sealed_data'] == ['f84', 'f84r']
                  and not any(p.startswith('f84') for p in pages), 'Scope/seals')
    rows, g1 = guard.query('transcription/voynich_zl3b_lines.tsv',
        ['page','locus','kind','paragraph_start','paragraph_end','eva_clean'], pages)
    alt, g2 = guard.query('transcription/voynich_cross_transcription_lines.tsv',
                         ['page','locus',*READERS], pages)
    cross = {r['locus']: r for r in alt}
    guard.require(set(cross) == {r['locus'] for r in rows}, 'Reader coverage')
    for row in rows:
        other = cross[row['locus']]
        guard.require(other['page'] == row['page'] and other['zl3b_clean'] == row['eva_clean'], 'Reader join')
        row.update({r: other[r] for r in READERS})
    by = {r['locus']: r for r in rows}
    focal, paragraph_counts, reader = [], [], ['# GDT816 complete focal reader', '',
        'Every source line in four paragraphs and two labels; no fluent translation.', '']
    for page, start, end in spec['paragraphs']:
        block = [by[f'{page}.{n}'] for n in range(start, end + 1)]
        guard.require(all(r['kind'] == 'P' for r in block) and block[0]['paragraph_start'] == '1'
                      and block[-1]['paragraph_end'] == '1' and not any(r['paragraph_start'] == '1'
                      or r['paragraph_end'] == '1' for r in block[1:-1]), 'Complete source P block')
        focal.extend(block)
        counts = {r: sum(len(row[r].split()) for row in block) for r in READERS}
        paragraph_counts.append({'page':page,'first':block[0]['locus'],'last':block[-1]['locus'],
                                 'loci':len(block),'tokens':counts})
        reader.extend(['## ' + block[0]['locus'] + '--' + block[-1]['locus'], ''])
        for r in block:
            reader.append(r['locus'] + ' ZL: `' + r[READERS[0]] + '`')
            reader.extend(k + ': `' + r[k] + '`' for k in READERS[1:] if r[k] != r[READERS[0]])
            reader.append('')
    for locus in spec['labels']:
        guard.require(by[locus]['kind'] == 'L', 'Label kind')
        focal.append(by[locus])
        reader.extend(['## ' + locus + ' [separate L]', '', by[locus][READERS[0]], ''])
    focal_ids = {r['locus'] for r in focal}
    external = [r for r in rows if r['locus'] not in focal_ids and any(
                set(r[k].split()) & set(spec['new_wholes']) for k in READERS)]
    literal = []
    for row in focal:
        for rd in READERS:
            words = row[rd].split()
            for model, delta in spec['models'].items():
                mapping = prior['shared_hypotheses'] | delta
                literal.append({'page':row['page'],'locus':row['locus'],'kind':row['kind'],
                    'reader':rd,'model':model,'source_text':row[rd],
                    'literal_json':json.dumps([mapping.get(w,'['+w+']') for w in words],ensure_ascii=False),
                    'confidence':spec['confidence']})
    def record(row):
        # JSON fields preserve genuinely empty alternate readings without trailing TSV blanks.
        return {'page':row['page'],'locus':row['locus'],'kind':row['kind'],
                'paragraph_start':row['paragraph_start'],'paragraph_end':row['paragraph_end'],
                'readings_json':json.dumps({k:row[k] for k in READERS},ensure_ascii=False)}
    result = {'experiment_id':'GDT816','status':'FIXED_NOUN_TRIALS_NOT_TRANSLATION',
              'source_selectors':pages,'visual_page_keys':34,'source_loci':len(rows),
              'paragraphs':paragraph_counts,'focal_loci':len(focal),'literal_rows':len(literal),
              'external_loci':len(external),'external_nonP_loci':[r['locus'] for r in external if r['kind']!='P'],
              'new_wholes':spec['new_wholes'],'guarded_queries':[g1,g2],
              'joint_quality_frame':spec['joint_quality_frame'],
              'frame_declaration_timing':spec['frame_declaration_timing'],
              'agent_Q_frames_agree':spec['agent_Q_frames_agree'],
              'sealed_data':['f84','f84r'],'new_admissions':0,'dictionary_changed':False,
              'meanings_validated':False,'confirmed_lexemes':0,'confirmed_plaintext_clauses':0}
    return {'FOCAL.tsv':tsv([record(r) for r in focal]),
            'EXTERNAL.tsv':tsv([record(r) for r in external]),'LITERAL_TRIALS.tsv':tsv(literal),
            'FULL_READER.md':'\n'.join(reader).rstrip()+'\n',
            'RESULT.json':json.dumps(result,indent=2,sort_keys=True)+'\n'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check',action='store_true')
    args = p.parse_args()
    values = build()
    for name, content in values.items():
        path = EXP/'artifacts'/name
        if args.check:
            guard.require(path.read_text() == content,'Replay differs: '+name)
        else:
            path.write_text(content)
    result = json.loads(values['RESULT.json'])
    print(json.dumps({k:result[k] for k in ['status','focal_loci','literal_rows','external_loci']}))


if __name__ == '__main__':
    main()
