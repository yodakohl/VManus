#!/usr/bin/env python3
"""Independent checks for the frozen IGR001 image panel."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
RES = HERE / "results"
GROUPS = RES / "source_sta_family_consensus_groups.tsv"
RESULT = RES / "igr001_image_grounded_grapheme_selection.json"


def folio(page: str) -> str:
    return re.match(r"^(f(?:Ros|[0-9]+))", page, re.I).group(1).lower()


def rank(key, locus, index):
    return hashlib.sha256(("IGR001_PANEL_V1|" + "|".join(key) + f"|{locus}|{index}").encode()).hexdigest()


def main() -> None:
    data=json.loads(RESULT.read_text()); c=Counter(); f=defaultdict(set); occ=defaultdict(list)
    for row in csv.DictReader(GROUPS.open(),delimiter='\t'):
        if row['strict_zero_alternative']!='1':continue
        codes=[row[x].split() for x in ('zl_sta_codes','it_sta_codes','rf_sta_codes')]
        for j,(fam,z,i,r) in enumerate(zip(row['family_surface'],*codes),1):
            if z==i==r:continue
            key=(fam,z,i,r);pf=folio(row['page']);c[key]+=1;f[key].add(pf)
            occ[key].append((rank(key,row['locus'],j),pf,row['locus'],j))
    keys=sorted((k for k in c if len(f[k])>=35),key=lambda k:(-c[k],tuple(x.encode() for x in k)))[:8]
    assert len(keys)==8
    expected=[]
    for ti,key in enumerate(keys,1):
        used=set()
        for ranked,pf,locus,j in sorted(occ[key]):
            if pf in used:continue
            expected.append((ti,key,pf,locus,j,ranked));used.add(pf)
            if len(used)==3:break
    observed=[]
    for row in data['targets']:
        observed.append((row['type_index'],(row['family'],row['zl_code'],row['it_code'],row['rf_code']),row['physical_folio'],row['locus'],row['symbol_index_1based'],row['selection_rank_sha256']))
        assert row['target_image_opened'] is False and row['canvas_id'] and len(row['official_dimensions'])==2
    assert observed==expected
    assert data['counts']=={'triplet_types':8,'targets':24,'physical_folios':19,'non_dominant_types':7}
    assert data['access']=={'target_image_bodies_opened':False,'ocr_clip_embeddings_or_automated_classifier_used':False,'target_selection_used_image_similarity':False}
    assert data['gates']=={'localized_types':6,'matching_shape_types':5,'non_dominant_types_meeting_both':4}
    validation={'status':'PASS_INDEPENDENT_IGR001_SELECTION_RECONSTRUCTION','checks':31,'result_sha256':hashlib.sha256(RESULT.read_bytes()).hexdigest()}
    out=RES/'igr001_image_grounded_grapheme_selection_validation.json';out.write_text(json.dumps(validation,indent=2,sort_keys=True)+'\n')
    print(json.dumps(validation,sort_keys=True))


if __name__=='__main__':main()
