#!/usr/bin/env python3
"""GDT1079: fixed complete-ring exact-form comparison; no meaning inference."""
import csv
import hashlib
import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parents[1]
F85 = ROOT / 'experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/native_groups.tsv'
F68 = ROOT / 'research_registry/proposals/laufenberg_f85r2_20260926/F68R_PAIRED_OPENINGS_SOURCE_20260927.json'
CACHE = ROOT / 'experiments/semantic_assumptions/cache/word_profiles.sqlite'
SOURCE = ROOT / 'experiments/semantic_assumptions/results/source_separator_transcription.tsv'
ALLOW = ROOT / 'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv'
EXPECTED = {
    F85: 'e50307f834b04ff2ce17a97f14fd2c7b3f24b4818bc7fda3f57c372afc6b9d3c',
    F68: '31b07594e91dff42cb407549e6102e4bb18109b981683ab2e1dbd3c55ba4a7dc',
    SOURCE: '4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0',
    ALLOW: 'f0def5a04bd91443cf4770c78f1b67e62cac2060627d8de38faba27899188483',
}
ED = ('ZL3b', 'IT2a', 'RF1b')
LOCI = ('f85r2.24', 'f68r2.31', 'f68r2.6')
BOUND = {'DEFINITE_SPACE', 'LINE_START', 'LINE_END'}
KEYS = ('edition','locus','source_group_index','left_separator','right_separator','ivtff_group_raw')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load():
    for path, wanted in EXPECTED.items():
        if sha(path) != wanted:
            raise ValueError('frozen source hash changed: ' + path.name)
    with F85.open(newline='', encoding='utf-8') as f:
        rows85 = list(csv.DictReader(f, delimiter='\t'))
    d68 = json.loads(F68.read_text())
    rows68 = next(q['rows'] for q in d68['queries'] if q['id'] == 'groups')
    rows = [{k:x[k] for k in KEYS} for x in rows85 if x['locus'].startswith('f85r2.')]
    rows.extend({k:x[k] for k in KEYS} for x in rows68)
    if {r['edition'] for r in rows} != set(ED):
        raise ValueError('reader coverage')
    con = sqlite3.connect('file:' + str(CACHE) + '?mode=ro', uri=True)
    receipt = json.loads(con.execute("select value from metadata where key='receipt'").fetchone()[0])
    inputs = receipt['inputs']
    if inputs['source_sha256'] != EXPECTED[SOURCE] or inputs['allowlist_sha256'] != EXPECTED[ALLOW] or inputs['selector_count'] != 179:
        raise ValueError('cache receipt mismatch')
    return rows, con


def eligible(x):
    return bool(re.fullmatch('[a-z]{4,}', x['ivtff_group_raw'])) and x['left_separator'] in BOUND and x['right_separator'] in BOUND


def main():
    rows, con = load()
    by = defaultdict(list)
    for x in rows:
        by[(x['edition'],x['locus'])].append(x)
    for ed in ED:
        for loc in LOCI:
            if not by[(ed,loc)]: raise ValueError('missing ring')
    names_all = {x['ivtff_group_raw'] for x in rows}
    freq = {(ed,name): (con.execute('select n from vocabulary where edition=? and form=?',(ed,name)).fetchone() or (0,))[0] for ed in ED for name in names_all}
    out = {'status':'', 'source_hashes':{p.relative_to(ROOT).as_posix():v for p,v in EXPECTED.items()},'reader_policy':'alternate readings of one manuscript', 'rings':{}, 'intersections':{}, 'same_page_controls':{}, 'rare_sun_only':[]}
    sun_sets = []
    for ed in ED:
        out['rings'][ed] = {}
        for loc in LOCI:
            these = sorted(by[(ed,loc)], key=lambda x:int(x['source_group_index']))
            out['rings'][ed][loc] = [{**x,'eligible':eligible(x),'corpus_count':freq[(ed,x['ivtff_group_raw'])]} for x in these]
        names = {loc:{x['ivtff_group_raw'] for x in by[(ed,loc)] if eligible(x)} for loc in LOCI}
        raw = {loc:{x['ivtff_group_raw'] for x in by[(ed,loc)]} for loc in LOCI}
        sun = names['f85r2.24'] & names['f68r2.31']
        moon = names['f85r2.24'] & names['f68r2.6']
        sun_sets.append({x for x in sun if x not in names['f68r2.6'] and freq[(ed,x)] <= 10})
        out['intersections'][ed] = {'sun_eligible':sorted(sun),'moon_eligible':sorted(moon),'sun_raw_ineligible':sorted((raw['f85r2.24'] & raw['f68r2.31']) - sun),'moon_raw_ineligible':sorted((raw['f85r2.24'] & raw['f68r2.6']) - moon)}
        out['same_page_controls'][ed] = {x:sorted({r['locus'] for r in rows if r['edition']==ed and r['locus'].startswith('f85r2.') and r['locus']!='f85r2.24' and r['ivtff_group_raw']==x}) for x in sun}
    out['rare_sun_only'] = sorted(set.intersection(*sun_sets))
    out['status'] = 'RARE_SUN_ONLY_LEAD' if out['rare_sun_only'] else 'NO_RARE_SUN_ONLY_EXACT_BRIDGE'
    target = HERE / 'artifacts/RESULT.json'
    target.write_text(json.dumps(out,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
    print(out['status'])

if __name__ == '__main__': main()
