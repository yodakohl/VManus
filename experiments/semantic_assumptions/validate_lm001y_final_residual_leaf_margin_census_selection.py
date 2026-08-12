#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json, re, urllib.request
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ANN=ROOT/'experiments/semantic_assumptions/results/public_voynich_nu_page_annotations_v2.tsv'
ZL=ROOT/'transcription/voynich_zl3b_lines.tsv'
OLD=ROOT/'experiments/semantic_assumptions/results/lm001_herbal_leaf_margin_visual_selection.tsv'
XP=ROOT/'experiments/semantic_assumptions/results/lm001x_currier_a_leaf_margin_extension_selection.tsv'
PANEL=ROOT/'experiments/semantic_assumptions/results/lm001y_final_residual_leaf_margin_census_selection.tsv'
RESULT=ROOT/'experiments/semantic_assumptions/results/lm001y_final_residual_leaf_margin_census_selection.json'
OUT=ROOT/'experiments/semantic_assumptions/results/lm001y_final_residual_leaf_margin_census_selection_validation.json'
MANIFEST='https://collections.library.yale.edu/manifests/2002046'; M_SHA='317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309'
def h(tag,page): return hashlib.sha256(f'{tag}|{page}'.encode('ascii')).hexdigest()
def main():
    checks=[]; meta={}
    with ZL.open(encoding='utf-8',newline='') as f:
        for r in csv.DictReader(f,delimiter='\t'): meta.setdefault(r['page'],r)
    excluded=set()
    for path in (OLD,XP):
        with path.open(encoding='utf-8',newline='') as f: excluded.update(r['physical_folio'] for r in csv.DictReader(f,delimiter='\t'))
    one={}
    with ANN.open(encoding='utf-8',newline='') as f:
        for r in csv.DictReader(f,delimiter='\t'):
            p=r['page']; m=re.match(r'^f(\d+)',p.lower())
            if 'SOURCE_HERBAL_PAGE' not in r['source_tags'] or p not in meta or meta[p]['language']!='A' or not m: continue
            folio='f'+m.group(1)
            if folio in excluded: continue
            candidate=(p,folio,m.group(1),r['quire'] or meta[p]['quire'],h('LM001X_PAGE',p))
            if folio not in one or candidate[4]<one[folio][4]: one[folio]=candidate
    expected=[r for r in one.values() if r[3]!='q05']
    stored=list(csv.DictReader(PANEL.open(encoding='utf-8'),delimiter='\t'))
    assert len(expected)==len(stored)==9
    emap={'LY'+h('LM001Y_OPAQUE',r[0])[:8].upper():r for r in expected}
    assert {r['opaque_id'] for r in stored}==set(emap)
    for r in stored:
        e=emap[r['opaque_id']]; assert (r['page'],r['physical_folio'],r['folio_number'],r['quire'],r['folio_page_sha256'])==e
    checks.append('complete_exact_nine_page_residual')
    assert len({r['physical_folio'] for r in stored})==9 and all(r['currier']=='A' and r['quire']!='q05' for r in stored); checks.append('new_folio_currier_and_quire_guards')
    assert Counter(r['quire'] for r in stored)=={'q03':4,'q01':2,'q02':1,'q04':1,'q07':1}; checks.append('complete_residual_quire_counts')
    req=urllib.request.Request(MANIFEST,headers={'User-Agent':'VManus-LM001Y-validator/1.0'})
    with urllib.request.urlopen(req,timeout=60) as response: raw=response.read()
    assert hashlib.sha256(raw).hexdigest()==M_SHA
    ids={c['id'].rsplit('/',1)[-1] for c in json.loads(raw.decode('utf-8'))['items']}; assert all(r['canvas_id'] in ids for r in stored); checks.append('official_manifest_canvas_bindings')
    result=json.loads(RESULT.read_text()); assert result['status']=='FROZEN_COMPLETE_RESIDUAL_BEFORE_IMAGE_INSPECTION' and result['panel_sha256']==hashlib.sha256(PANEL.read_bytes()).hexdigest(); checks.append('canonical_selection_result')
    assert result['gates']['no_sampling_or_page_count_rank'] is True and result['gates']['selected_images_not_opened_by_builder'] is True and result['gates']['no_voynich_text_features_accessed'] is True; checks.append('selection_and_access_seal')
    out={'experiment':'LM001Y_FINAL_RESIDUAL_LEAF_MARGIN_CENSUS_SELECTION_VALIDATION','status':'PASS_6_CHECK_COMPLETE_RESIDUAL_RECONSTRUCTION','check_count':len(checks),'checks':checks,'validated_result_sha256':hashlib.sha256(RESULT.read_bytes()).hexdigest(),'selected_images_opened_by_validator':False,'claim_ceiling':result['claim_ceiling']}
    OUT.write_text(json.dumps(out,sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8')
if __name__=='__main__': main()
