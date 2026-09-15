#!/usr/bin/env python3
"""Independent GDT961 substring-incidence validator; no runner import."""
from pathlib import Path
from collections import defaultdict,Counter
import csv,gzip,hashlib,json
EXP=Path(__file__).resolve().parents[1];ROOT=EXP.parents[2];ART=EXP/'artifacts';PRED=ART/'PREDICTIONS.tsv'
def load(p):return json.load(p) if hasattr(p,'read') else json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
 if hasattr(p,'read'):return list(csv.DictReader(p,delimiter='\t'))
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 spec=load(EXP/'src/SPEC.json'); checks={}
 for rel,h in load(EXP/'PREREG_LOCK.json').items():
  a=sha(ROOT/rel);checks[rel]={'expected':h,'actual':a,'ok':a==h}
 windows=load(gzip.open(ROOT/spec['windows'],'rt',encoding='utf-8'))
 source=load(ROOT/spec['source'])
 masks={};mask_rows=[]
 for w in windows:
  pieces=defaultdict(int)
  for pidx,p in enumerate(w['paragraphs']):
   for g in p['groups']:
    if not g['known']:continue
    word=g['ivtff_group_raw'];m=1<<pidx
    for i in range(len(word)):
     for j in range(i+1,len(word)+1):pieces[word[i:j]]|=m
  masks[w['window_id']]=dict(sorted(pieces.items()))
  for piece,m in sorted(pieces.items()):mask_rows.append({'window_id':w['window_id'],'component':piece,'mask':str(m),'observed_rows':','.join(str(i+1) for i in range(15) if m&(1<<i))})
 got_masks=rows(gzip.open(ART/'COMPONENT_MASKS.tsv.gz','rt',encoding='utf-8'));mask_ok=mask_rows==got_masks
 # Rebuild the complete prediction table from the independently locked SOURCE
 # model.  The frozen TSV is a comparison target, never an input to domains.
 pred=[]
 for w in windows:
  for model in spec['models']:
   for direction in spec['directions']:
    for plant, source_rows in source['models'][model]['incidence'].items():
     positions=sorted((16-r if direction=='REVERSED' else r) for r in source_rows)
     mask=sum(1 << (p-1) for p in positions)
     pred.append({'case_id':f"{w['window_id']}|{model}|{direction}",
      'window_id':w['window_id'],'edition':w['edition'],'page':w['page'],
      'physical_leaf':str(w['physical_leaf']),'model':model,'direction':direction,
      'plant':plant,'required_rows':','.join(map(str,positions)),
      'required_mask':str(mask),'independent_confirmation_leaves':'0'})
 frozen_pred=rows(PRED);predictions_ok=pred==frozen_pred
 domains=[]; case_domains=defaultdict(list); window_by={w['window_id']:w for w in windows}
 for r in pred:
  wm=masks[r['window_id']];req=int(r['required_mask']);w=window_by[r['window_id']];avail=sum(1<<i for i,n in enumerate(w['unknown_slots']) if n)
  known=sorted(c for c,m in wm.items() if m==req)
  upper=[{'component':c,'known_mask':m,'missing_mask':req&~m} for c,m in sorted(wm.items()) if m&~req==0 and (req&~m)&~avail==0]
  fresh=(req&~avail)==0
  status='KNOWN_MASK_MATCH' if known else 'UNKNOWN_ONLY' if upper or fresh else 'CONTRADICTED'
  d={'case_id':r['case_id'],'window_id':r['window_id'],'edition':r['edition'],'page':r['page'],'physical_leaf':r['physical_leaf'],'model':r['model'],'direction':r['direction'],'plant':r['plant'],'required_rows':r['required_rows'],'required_mask':r['required_mask'],'independent_confirmation_leaves':r['independent_confirmation_leaves'],'known_mask_components':known,'upper_components':upper,'fresh_unseen_component_possible':fresh,'status':status};domains.append(d);case_domains[r['case_id']].append(d)
 got_domains=load(gzip.open(ART/'PLANT_COMPONENT_DOMAINS.json.gz','rt',encoding='utf-8'));domains_ok=domains==got_domains
 cases=[]
 for cid,ds in case_domains.items():
  first=ds[0];known=[d['plant'] for d in ds if not d['known_mask_components']];upper=[d['plant'] for d in ds if not d['upper_components'] and not d['fresh_unseen_component_possible']]
  cases.append({'case_id':cid,'edition':first['edition'],'page':first['page'],'physical_leaf':int(first['physical_leaf']),'model':first['model'],'direction':first['direction'],'source_names':len(ds),'plants_without_known_mask':known,'plants_without_upper_component':upper,'status':'CONTRADICTED' if upper else 'ALL_NECESSARY_UPPER_DOMAINS_NONEMPTY','joint_lexicon_assessed':False,'independent_confirmation_leaves':0})
 got_cases=load(gzip.open(ART/'ALL_CASES.json.gz','rt',encoding='utf-8'));cases_ok=cases==got_cases
 # Identical prediction classes are exact mask classes within each window.
 groups=[]
 for w in windows:
  inv=defaultdict(list)
  for c,m in masks[w['window_id']].items():inv[m].append(c)
  for m in sorted(inv):groups.append({'window_id':w['window_id'],'mask':m,'components':sorted(inv[m])})
 groups_ok=groups==load(gzip.open(ART/'IDENTICAL_COMPONENT_PREDICTIONS.json.gz','rt',encoding='utf-8'))
 # Compact Mugwort report is independently regenerated from the corresponding domain rows.
 mug=[]
 for cid,ds in case_domains.items():
  d=next(x for x in ds if x['plant']=='Mugwort');reqrows=d['required_rows'];req=int(d['required_mask']);maxcov=max([((x['known_mask']&req).bit_count()) for x in d['upper_components']] or [0]);miss=[x['missing_mask'].bit_count() for x in d['upper_components']]; mug.append({'case_id':cid,'edition':d['edition'],'page':d['page'],'direction':d['direction'],'required_rows':reqrows,'status':d['status'],'known_mask_components':' | '.join(d['known_mask_components']),'upper_components':' | '.join(x['component'] for x in d['upper_components']),'fresh_unseen_component_possible':str(d['fresh_unseen_component_possible']),'maximum_known_required_rows':str(maxcov),'minimum_required_rows_from_unknown':str(min(miss) if miss else ('0' if d['fresh_unseen_component_possible'] else 'NO_COMPLETION'))})
 mug_ok=mug==rows(ART/'MUGWORT_ALL_CASES.tsv')
 mug_domains=[d for d in domains if d['plant']=='Mugwort']
 # Replay the supplementary raw-group audit from the registered exact Mugwort
 # hits.  It deliberately includes the uncertain-boundary group: this is a
 # provenance diagnostic, not an additional known occurrence.
 raw_expected=[]
 exact_by_window=defaultdict(set)
 for d in mug_domains:
  if d['known_mask_components']:
   exact_by_window[d['window_id']].update(d['known_mask_components'])
 for w in windows:
  wanted=exact_by_window.get(w['window_id'],set())
  if not wanted: continue
  for comp in sorted(wanted):
   for pidx,p in enumerate(w['paragraphs'],1):
    for g in p['groups']:
     raw=g['ivtff_group_raw']
     if comp in raw:
      raw_expected.append({'window_id':w['window_id'],'component':comp,
       'relative_paragraph':str(pidx),'expected_source_row':str(bool(g['known'])),
       'locus':g['locus'],'source_group_id':g['source_group_id'],'raw':raw,
       'known_in_registered_projection':str(bool(g['known'])),
       'left_separator':g['left_separator'],'right_separator':g['right_separator']})
 raw_path=ART/'OBSERVED_MATCH_RAW_AUDIT.tsv'
 raw_audit_ok=raw_path.exists() and raw_expected==rows(raw_path)
 # Candidate TSV is a second independently reproducible presentation of cases.
 candidate_rows=[]
 for c in cases:
  candidate_rows.append({'case_id':c['case_id'],'edition':c['edition'],'page':c['page'],
   'physical_leaf':str(c['physical_leaf']),'model':c['model'],'direction':c['direction'],
   'source_names':str(c['source_names']),
   'plants_without_known_mask':' | '.join(c['plants_without_known_mask']),
   'plants_without_upper_component':' | '.join(c['plants_without_upper_component']),
   'status':c['status'],'joint_lexicon_assessed':'False',
   'independent_confirmation_leaves':'0'})
 candidate_ok=candidate_rows==rows(ART/'CANDIDATE_TABLE.tsv')
 # Recompute the published outcome counters from regenerated domains/cases.
 case_outcomes=dict(Counter(c['status'] for c in cases))
 plant_outcomes=dict(Counter(d['status'] for d in domains))
 mug_outcomes=dict(Counter(d['status'] for d in mug_domains))
 mug_pieces=sorted({p for d in mug_domains for p in d['known_mask_components']})
 res=load(ART/'RESULT.json');result_ok=(res.get('windows')==len(windows) and
  res.get('component_window_pairs')==len(mask_rows) and
  res.get('distinct_observed_components')==len({r['component'] for r in mask_rows}) and
  res.get('identical_prediction_classes')==len(groups) and
  res.get('plant_predictions')==len(pred) and res.get('cases')==len(cases) and
  res.get('case_outcomes')==case_outcomes and res.get('plant_outcomes')==plant_outcomes and
  res.get('mugwort_outcomes')==mug_outcomes and res.get('mugwort_known_pieces')==mug_pieces and
  res.get('confirmed_words')==0 and res.get('joint_lexicon_assessed') is False and
  res.get('independent_confirmation_leaves')==0 and res.get('no_new_data_or_decoder') is True and
  res.get('significance')=='NOT_ASSESSED_POST_EXPOSURE_NECESSARY_BOUND')
 report={'experiment':'GDT961','validator':'independent_contiguous_substring_union_without_run_import','status':'PASS' if all(x['ok'] for x in checks.values()) and mask_ok and predictions_ok and domains_ok and cases_ok and groups_ok and mug_ok and candidate_ok and result_ok and raw_audit_ok else 'FAIL','lock':{'all_hashes_match':all(x['ok'] for x in checks.values()),'checks':checks},'components':{'windows':len(windows),'component_window_rows':len(mask_rows),'component_masks_match':mask_ok,'distinct_observed_components':len({r['component'] for r in mask_rows})},'predictions':{'count':len(pred),'source_reconstruction_matches_frozen_tsv':predictions_ok},'domains':{'predictions':len(pred),'domains_match':domains_ok,'cases':len(cases),'cases_match':cases_ok,'identical_prediction_classes_match':groups_ok,'mugwort_report_match':mug_ok,'candidate_table_match':candidate_ok,'case_outcomes':case_outcomes,'plant_outcomes':plant_outcomes,'mugwort_outcomes':mug_outcomes,'mugwort_known_pieces':mug_pieces},'raw_audit':{'rows':len(raw_expected),'replay_matches_artifact':raw_audit_ok,'uncertain_boundary_rows':sum(r['expected_source_row']=='False' for r in raw_expected)},'result_contract_match':result_ok,'claim_ceiling':{'meaning_validated':False,'confirmed_words':0,'joint_lexicon_assessed':False,'independent_confirmation_leaves':0,'significance_assessed':False,'no_new_decoder':True}}
 (ART/'VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':report['status'],'component_rows':len(mask_rows),'predictions':len(pred),'cases':len(cases),'groups':len(groups),'meaning_validated':False}));return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
