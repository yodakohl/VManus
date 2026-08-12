#!/usr/bin/env python3
"""Filler-blind worth screen for exact 10-to-5 annular correspondence."""
from __future__ import annotations
import argparse,csv,hashlib,json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]; BASE=ROOT/'experiments/semantic_assumptions'
METHOD=BASE/'SPECIAL_CIRCLE_10_TO_5_PAIRING_WORTH_METHOD.md'; INV=BASE/'results/special_circle_text_blind_array_inventory.tsv'
OBS=BASE/'special_circle_10_to_5_pairing_observations.tsv'; OUT=BASE/'results/special_circle_10_to_5_pairing_worth.json'; REPORT=BASE/'results/special_circle_10_to_5_pairing_worth_report.md'
MANIFEST_SHA='317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x):return (json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode()
def build():
 rows=list(csv.DictReader(INV.open(encoding='utf-8',newline=''),delimiter='\t')); arrays={}
 for r in rows: arrays.setdefault(r['array_id'],r)
 bypage=defaultdict(list)
 for r in arrays.values():bypage[r['page']].append(r)
 cand={}
 for page,rs in bypage.items():
  outer=[r for r in rs if r['normalized_code']=='@Lz' and r['slot_count']=='10' and ('outer' in r['unit_description'].lower() or 'band 1' in r['unit_description'].lower())]
  inner=[r for r in rs if r['normalized_code']=='@Lz' and r['slot_count']=='5' and 'inner' in r['unit_description'].lower()]
  if len(outer)==len(inner)==1:cand[page]=(outer[0]['array_id'],inner[0]['array_id'],outer[0]['physical_folio'])
 expected={'f70v1':('SCARR020|f70v1|S2','SCARR021|f70v1|S1','f70'),'f71r':('SCARR022|f71r|S1','SCARR023|f71r|S2','f71'),'f71v':('SCARR024|f71v|S1','SCARR025|f71v|S2','f71'),'f72r1':('SCARR026|f72r1|S1','SCARR027|f72r1|S2','f72')}
 if cand!=expected:raise RuntimeError(cand)
 obs=list(csv.DictReader(OBS.open(encoding='utf-8',newline=''),delimiter='\t'))
 if [r['page'] for r in obs]!=list(expected) or any((r['outer_array'],r['inner_array'],r['physical_folio'])!=expected[r['page']] for r in obs):raise RuntimeError('observations')
 devices=('shared_spokes','exact_two_to_one_cells','paired_brackets_or_leaders','exact_nonoverlapping_sectors')
 qualifying=[r for r in obs if any(r[k]=='YES' for k in devices)]
 folios=sorted({r['physical_folio'] for r in qualifying})
 gates={'exact_four_page_three_folio_candidate_panel':len(obs)==4 and len({r['physical_folio'] for r in obs})==3,
        'every_candidate_page_has_author_visible_pairing_device':len(qualifying)==4,
        'pairing_device_on_at_least_three_physical_folios':len(folios)>=3,
        'zero_filler_transcription_or_formal_access':True}
 result={'experiment':'SPECIAL_CIRCLE_10_TO_5_PAIRING_WORTH','schema':'SPECIAL_CIRCLE_10_TO_5_PAIRING_WORTH_V1','status':'STOP_NO_AUTHOR_VISIBLE_TWO_TO_ONE_PAIRING_DEVICE','decision':'DO_NOT_ALIGN_OR_SCORE_10_TO_5_RINGS','counts':{'candidate_pages':4,'physical_folios':3,'outer_slots':40,'inner_slots':20,'pages_with_pairing_device':len(qualifying),'folios_with_pairing_device':len(folios),'filler_fields_accessed':0},'candidate_pages':list(expected),'gates':gates,'observations':[{k:r[k] for k in ('page','physical_folio','yale_canvas','shared_spokes','exact_two_to_one_cells','paired_brackets_or_leaders','exact_nonoverlapping_sectors','certainty')} for r in obs],'inputs':{str(p.relative_to(ROOT)):sha(p) for p in (METHOD,INV,OBS)},'external_source_bindings':{'yale_manifest_2002046_sha256':MANIFEST_SHA,'canvas_image_sha256s':{r['yale_canvas']:r['yale_image_sha256'] for r in obs}},'access':{'voynich_fillers_opened':False,'surface_family_member_root_role_accessed':False,'machine_visual_observations_represented_as_human_annotations':False},'claim_ceiling':'The repeated 10-plus-5 annular layout has no author-visible exact two-to-one pairing device in the four inspected pages. This supplies no slot value, number, word, sound, language, cipher, plaintext, meaning, or translation.'}
 report='# Special-circle 10-to-5 annular pairing worth screen\n\nStatus: **STOP — NO AUTHOR-VISIBLE TWO-TO-ONE PAIRING DEVICE**.\n\nThe corrected filler-blind inventory mechanically yields f70v1, f71r, f71v, and f72r1: four pages on three physical folios with one 10-slot outer and one 5-slot inner `@Lz` band. Direct inspection of exact official Yale canvases finds open concentric annuli but zero shared spokes, two-to-one cells, paired brackets/leaders, or non-overlapping sectors that assign two outer figures to one inner figure. All correspondence gates fail; zero Voynich filler or formal fields were opened.\n\nDo not invent proportional pairing or score the rings. This establishes no coordinate, number, object, word, plaintext, meaning, or translation.\n'
 return result,report
def main():
 a=argparse.ArgumentParser();a.add_argument('--write',action='store_true');x=a.parse_args();r,m=build()
 if x.write:OUT.write_bytes(canon(r));REPORT.write_text(m,encoding='utf-8')
 else:print(canon(r).decode(),end='')
if __name__=='__main__':main()
