#!/usr/bin/env python3
"""Join existing source-position and word-profile facts for the visual dossier."""
import collections
import csv
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parents[1]


def rows(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f,delimiter='\t'))


def main():
    p=ROOT/'experiments/yolo/gdt1062_schechter_plant_label_source_alignment/artifacts/LABEL_RESULTS.tsv'
    comparison=rows(p)
    four={page:[r for r in comparison if r['page']==page]
          for page in ('f2v','f9v','f11r','f24v')}
    assert all(len(v)==3 for v in four.values())
    heads=rows(ROOT/'experiments/yolo/gdt1059_kooiin_header_quality_base_rate/artifacts/HEAD_CONTACTS.tsv')
    counts=collections.Counter(r['head_surface'] for r in heads)
    assert len(heads)==89
    assert {r['page'] for r in heads if r['head_surface']=='kooiin'}=={'f2v','f29v'}
    cmd=[str(ROOT/'vmanus-work'),'words','profile','fochor','--json','--limit','1']
    prof=json.loads(subprocess.run(cmd,cwd=ROOT,check=True,text=True,
                                   stdout=subprocess.PIPE).stdout)['profiles'][0]
    payload={'source_position':{page:{r['reader']:{'head':r['first_p_group'],
                                   'exact':bool(int(r['first_p_exact']))} for r in rr}
                                for page,rr in four.items()},
             'fochor_admitted_corpus_counts':{reader:d['count']
                   for reader,d in prof['editions'].items()},
             'herbal_a_head_baseline':{'pages':len(heads),'distinct_forms':len(counts),
                                        'singleton_forms':sum(v==1 for v in counts.values())},
             'kooiin_exact_head_pages':['f2v','f29v'],
             'visual_record':'src/VISUAL_RECORD.tsv; informed human assessment, not machine-validated',
             'claim_ceiling':'replaceable f9v Viola C0 hypothesis conditional on head-as-name; no confirmed lexeme'}
    (HERE/'artifacts/RESULT.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(payload,indent=2,ensure_ascii=False))


if __name__=='__main__':main()
