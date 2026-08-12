#!/usr/bin/env python3
"""Filler-blind capacity for owned root-only versus leaf-bearing fragments."""
from __future__ import annotations
import argparse,csv,hashlib,itertools,json,re
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];B=ROOT/'experiments/semantic_assumptions';R=B/'results'
METHOD=B/'PLC001_PHARMA_ROOT_ONLY_LEAF_BEARING_CAPACITY_METHOD.md';ANN=R/'existing_human_exact_locus_annotations.tsv';SRC=R/'source_sta_family_consensus_groups.tsv';OUT=R/'plc001_pharma_root_leaf_capacity.json';REPORT=R/'plc001_pharma_root_leaf_capacity_report.md'
DIRE=r'(?=\s+(?:East|West|Above|Below|Near|Within|Against|On top|Under|Between)\b)';ED=('zl_sta_codes','it_sta_codes','rf_sta_codes')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x):return (json.dumps(x,indent=2,sort_keys=True)+'\n').encode()
def fam(s):return ''.join(re.sub(r'\d+$','',x) for x in s.split())
def extract(r):
 c=r['local_comment'];defs={m.group(1):m.group(2).strip().lower() for m in re.finditer(r'plant\s+(<f[^>]+>\[[^]]+\])\s*-\s*(.*?)(?:'+DIRE+r'|[.;]|$)',c,re.I)};ms=list(re.finditer(r'\b(?:East|West|Above|Below|Near|Within|Against|On top|Under|Between)\b',c,re.I));rel=c[ms[-1].start():] if ms else '';refs=list(dict.fromkeys(re.findall(r'plant\s+(<f[^>]+>\[[^]]+\])',rel,re.I)))
 if len(refs)!=1 or refs[0] not in defs or re.search(r'\bbetween\b',rel,re.I):return None
 d=defs[refs[0]];root=bool(re.search(r'\b(?:root|roots|tuber|tubers|bulb|bulbous)\b',d));leaf=bool(re.search(r'\b(?:leaf|leaves)\b',d));other=bool(re.search(r'\b(?:flower|flowers|stem|stems|twig|twigs|sprout|sprouts|berries|infloresc)',d))
 state='ROOT_ONLY' if root and not leaf and not other else ('LEAF_BEARING' if leaf else None)
 return (state,refs[0],d) if state else None
def build():
 by=defaultdict(list)
 for r in csv.DictReader(SRC.open(encoding='utf-8'),delimiter='\t'):by[r['locus']].append(r)
 for v in by.values():v.sort(key=lambda x:int(x['consensus_group_index']))
 candidates=[]
 for r in csv.DictReader(ANN.open(encoding='utf-8'),delimiter='\t'):
  if (r['normalized_code'],r['certainty'],r['relation_scope'])!=('@Lf','UNHEDGED','EXACT_LOCAL_COMMENT'):continue
  e=extract(r)
  if e:candidates.append((r,e))
 stable=[];ex=Counter()
 for r,(state,owner,desc) in candidates:
  groups=by.get(r['locus'],[])
  if not groups:ex['NO_SOURCE_NATIVE_MAPPING']+=1;continue
  if not all(g['strict_zero_alternative']=='1' and all(fam(g[k])==g['family_surface'] for k in ED) for g in groups):ex['NOT_STRICT_ALL_READING_STABLE']+=1;continue
  stable.append({'state':state,'folio':re.match(r'f\d+',r['page']).group(),'page':r['page'],'locus':r['locus'],'lengths':tuple(int(g['symbol_count']) for g in groups)})
 states=Counter(x['state'] for x in stable);folios={s:sorted({x['folio'] for x in stable if x['state']==s}) for s in states};mixed_folios=sorted(f for f in {x['folio'] for x in stable} if {x['state'] for x in stable if x['folio']==f}==set(states));mixed_pages=sorted(p for p in {x['page'] for x in stable} if {x['state'] for x in stable if x['page']==p}==set(states));pairs=[]
 for a,b in itertools.combinations(stable,2):
  if a['folio']==b['folio'] and a['state']!=b['state'] and a['lengths']==b['lengths']:pairs.append((a['locus'],b['locus']))
 gates={'at_least_six_root_only':states['ROOT_ONLY']>=6,'at_least_twelve_leaf_bearing':states['LEAF_BEARING']>=12,'each_state_spans_three_folios':all(len(folios[s])>=3 for s in states),'at_least_three_mixed_folios':len(mixed_folios)>=3,'at_least_two_mixed_pages':len(mixed_pages)>=2,'at_least_twelve_within_folio_exact_length_pairs':len(pairs)>=12,'zero_label_identity_association_or_score_access':True}
 result={'experiment':'PLC001_PHARMA_ROOT_ONLY_LEAF_BEARING_CAPACITY','schema':'PLC001_CAPACITY_V1','status':'STOP_FILLER_BLIND_NO_LENGTH_MATCHED_CROSS_FOLIO_CONTRAST','decision':'DO_NOT_OPEN_LABEL_IDENTITIES_OR_SCORE_ROOT_LEAF_STATE','counts':{'parsed_owned_candidates':len(candidates),'stable_retained':len(stable),'states':dict(states),'excluded':dict(ex),'folios_by_state':folios,'mixed_folios':mixed_folios,'mixed_pages':mixed_pages,'within_folio_exact_length_pairs':len(pairs)},'gates':gates,'access':{'label_surface_or_family_accessed':False,'root_or_role_accessed':False,'association_scores_computed':False,'null_worlds_run':0},'inputs':{str(p.relative_to(ROOT)):sha(p) for p in (METHOD,ANN,SRC)},'claim_ceiling':'Human comments expose a small root-only versus leaf-bearing object-state panel, but no matched transferable text contrast. No ROOT, LEAF, plant-part word, sound, language, cipher, plaintext, meaning, or translation follows.'}
 report=f"# PLC001 pharmaceutical root-only versus leaf-bearing capacity\n\nStatus: **STOP — NO LENGTH-MATCHED CROSS-FOLIO CONTRAST**.\n\nThe conservative human-comment parser finds **{len(candidates)}** owned candidates. Current strict all-reading source mapping retains **{len(stable)}**: **{states['ROOT_ONLY']} ROOT_ONLY** and **{states['LEAF_BEARING']} LEAF_BEARING**. Root-only spans {', '.join(folios['ROOT_ONLY'])}; leaf-bearing spans {', '.join(folios['LEAF_BEARING'])}. Only {', '.join(mixed_folios)} contain both states, and only {', '.join(mixed_pages)} is a mixed page.\n\nThere are **{len(pairs)}** within-folio opposite-state pairs with the same ordered source-group length vector. Any association would therefore confound object state with page/folio and label geometry. No label identity, family/member association, root/role, effect, or null was opened.\n\nThis supplies no ROOT or LEAF word, sound, language, cipher, plaintext, meaning, or translation.\n"
 return result,report
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();r,m=build()
 if a.write:OUT.write_bytes(canon(r));REPORT.write_text(m,encoding='utf-8')
 else:print(canon(r).decode(),end='')
if __name__=='__main__':main()
