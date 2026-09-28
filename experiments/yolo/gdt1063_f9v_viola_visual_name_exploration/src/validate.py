#!/usr/bin/env python3
"""Check structural source joins and the four-page manual-record scope."""
import collections
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parents[1]


def rows(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f,delimiter='\t'))


def main():
    result=json.loads((HERE/'artifacts/RESULT.json').read_text())
    source=rows(ROOT/'experiments/yolo/gdt1062_schechter_plant_label_source_alignment/artifacts/LABEL_RESULTS.tsv')
    for page in ('f2v','f9v','f11r','f24v'):
        rr=[r for r in source if r['page']==page]
        assert len(rr)==3
        for r in rr:
            assert result['source_position'][page][r['reader']]=={
                'head':r['first_p_group'],'exact':bool(int(r['first_p_exact']))}
    assert all(result['source_position']['f9v'][r]['head']=='fochor'
               for r in ('zl3b','it2a','rf1b'))
    assert result['fochor_admitted_corpus_counts']=={'ZL3b':1,'IT2a':1,'RF1b':1}
    heads=rows(ROOT/'experiments/yolo/gdt1059_kooiin_header_quality_base_rate/artifacts/HEAD_CONTACTS.tsv')
    count=collections.Counter(r['head_surface'] for r in heads)
    assert result['herbal_a_head_baseline']=={
        'pages':len(heads),'distinct_forms':len(count),
        'singleton_forms':sum(v==1 for v in count.values())}
    assert sorted(r['page'] for r in heads if r['head_surface']=='kooiin')==['f29v','f2v']
    visual=rows(HERE/'src/VISUAL_RECORD.tsv')
    assert len(visual)==4 and {r['page'] for r in visual}=={'f2v','f9v','f11r','f24v'}
    assert all(r['visible_features'] and r['botanical_comparator'] and r['assessment'] for r in visual)
    print('PASS: four-page source joins, head baseline and visual-record completeness; image semantics unvalidated')


if __name__=='__main__':main()
