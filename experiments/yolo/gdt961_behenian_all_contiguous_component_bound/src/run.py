#!/usr/bin/env python3
"""Exhaustive necessary incidence bound, never a decoder or lexicon fit."""
from pathlib import Path
from collections import defaultdict,Counter
import csv,gzip,hashlib,io,json,re
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def zipped(name,obj):
 data=json.dumps(obj,ensure_ascii=False,separators=(',',':')).encode()+b'\n'
 (A/name).write_bytes(gzip.compress(data,mtime=0))
def table(name,rows,compressed=False):
 s=io.StringIO();w=csv.DictWriter(s,list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
 b=s.getvalue().encode();(A/name).write_bytes(gzip.compress(b,mtime=0) if compressed else b)
def main():
 for path,h in read(E/'PREREG_LOCK.json').items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==h,path
 spec=read(E/'src/SPEC.json');wins=json.load(gzip.open(R/spec['windows'],'rt'));pred=list(csv.DictReader((A/'PREDICTIONS.tsv').open(),delimiter='\t'))
 inventories={};mask_rows=[];classes=[]
 for w in wins:
  masks={}
  for word,word_mask in w['word_masks'].items():
   for i in range(len(word)):
    for j in range(i+1,len(word)+1):
     c=word[i:j];masks[c]=masks.get(c,0)|word_mask
  inventories[w['window_id']]=dict(sorted(masks.items()))
  eq=defaultdict(list)
  for c,m in sorted(masks.items()):
   mask_rows.append({'window_id':w['window_id'],'component':c,'mask':m,'observed_rows':','.join(str(i+1) for i in range(15) if m&(1<<i))});eq[m].append(c)
  for m,cs in sorted(eq.items()):classes.append({'window_id':w['window_id'],'mask':m,'components':cs})
 wm={w['window_id']:w for w in wins};domains=[]
 for p in pred:
  req=int(p['required_mask']);w=wm[p['window_id']];masks=inventories[w['window_id']]
  unknown_mask=sum(1<<i for i,n in enumerate(w['unknown_slots']) if n)
  lower=[c for c,m in masks.items() if m==req]
  upper=[{'component':c,'known_mask':m,'missing_mask':req&~m} for c,m in masks.items() if not(m&~req) and not((req&~m)&~unknown_mask)]
  fresh=not(req&~unknown_mask)
  status='KNOWN_MASK_MATCH' if lower else 'UNKNOWN_ONLY' if upper or fresh else 'CONTRADICTED'
  domains.append(dict(p,known_mask_components=lower,upper_components=upper,fresh_unseen_component_possible=fresh,status=status))
 cases=[];by=defaultdict(list)
 for d in domains:by[d['case_id']].append(d)
 for cid,ds in by.items():
  missing_lower=[d['plant'] for d in ds if not d['known_mask_components']]
  missing_upper=[d['plant'] for d in ds if not d['upper_components'] and not d['fresh_unseen_component_possible']]
  cases.append({'case_id':cid,'edition':ds[0]['edition'],'page':ds[0]['page'],'physical_leaf':int(ds[0]['physical_leaf']),'model':ds[0]['model'],'direction':ds[0]['direction'],'source_names':len(ds),'plants_without_known_mask':missing_lower,'plants_without_upper_component':missing_upper,'status':'ALL_NECESSARY_KNOWN_DOMAINS_NONEMPTY' if not missing_lower else 'ALL_NECESSARY_UPPER_DOMAINS_NONEMPTY' if not missing_upper else 'CONTRADICTED','joint_lexicon_assessed':False,'independent_confirmation_leaves':0})
 mugwort=[d for d in domains if d['plant']=='Mugwort'];mugrows=[]
 for d in mugwort:
  maxknown=max([x['known_mask'].bit_count() for x in d['upper_components']] or [0]);req=int(d['required_mask'])
  mugrows.append({k:d[k] for k in ['case_id','edition','page','direction','required_rows','status']}|{'known_mask_components':' | '.join(d['known_mask_components']),'upper_components':' | '.join(x['component'] for x in d['upper_components']),'fresh_unseen_component_possible':d['fresh_unseen_component_possible'],'maximum_known_required_rows':maxknown,'minimum_required_rows_from_unknown':req.bit_count()-maxknown if d['upper_components'] or d['fresh_unseen_component_possible'] else 'NO_COMPLETION'})
 # Post-result raw diagnostic, separate from the registered known-mask score.
 # Exhaust ALL observed Mugwort matches; inspect every group of their window.
 audit=[];seen=set()
 for d in mugwort:
  for component in d['known_mask_components']:
   identity=(d['window_id'],component,int(d['required_mask']))
   if identity in seen:continue
   seen.add(identity)
   for i,pa in enumerate(wm[d['window_id']]['paragraphs'],1):
    for g in pa['groups']:
     raw=g['ivtff_group_raw']
     if re.fullmatch('[a-z]+',raw) and component in raw:
      audit.append({'window_id':d['window_id'],'component':component,'relative_paragraph':i,'expected_source_row':bool(int(d['required_mask'])&(1<<(i-1))),'locus':g['locus'],'source_group_id':g['source_group_id'],'raw':raw,'known_in_registered_projection':g['known'],'left_separator':g['left_separator'],'right_separator':g['right_separator']})
 if audit:table('OBSERVED_MATCH_RAW_AUDIT.tsv',audit)
 table('COMPONENT_MASKS.tsv.gz',mask_rows,True);zipped('IDENTICAL_COMPONENT_PREDICTIONS.json.gz',classes);zipped('PLANT_COMPONENT_DOMAINS.json.gz',domains);zipped('ALL_CASES.json.gz',cases);table('MUGWORT_ALL_CASES.tsv',mugrows)
 flat=[{k:(' | '.join(v) if isinstance(v,list) else v) for k,v in c.items()} for c in cases];table('CANDIDATE_TABLE.tsv',flat)
 result={'experiment_id':'GDT961','status':'COMPLETE_NECESSARY_COMPONENT_INCIDENCE_BOUND','windows':len(wins),'component_window_pairs':len(mask_rows),'distinct_observed_components':len({r['component'] for r in mask_rows}),'identical_prediction_classes':len(classes),'plant_predictions':len(domains),'cases':len(cases),'case_outcomes':dict(Counter(c['status'] for c in cases)),'plant_outcomes':dict(Counter(d['status'] for d in domains)),'mugwort_outcomes':dict(Counter(d['status'] for d in mugwort)),'mugwort_known_pieces':sorted({s for d in mugwort for s in d['known_mask_components']}),'confirmed_words':0,'joint_lexicon_assessed':False,'independent_confirmation_leaves':0,'no_new_data_or_decoder':True,'significance':'NOT_ASSESSED_POST_EXPOSURE_NECESSARY_BOUND'}
 (A/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
