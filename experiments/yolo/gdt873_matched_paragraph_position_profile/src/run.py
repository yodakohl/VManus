#!/usr/bin/env python3
"""One retrospective exact-mask paragraph-position comparison."""
import csv,json,hashlib,re,sys
from pathlib import Path
from collections import defaultdict,Counter
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2];A=B/'artifacts'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def source(s):
 p=ROOT/s['source_receipt'];assert sha(p)==s['source_receipt_sha256'];receipt=json.loads(p.read_text());paths={}
 for k,v in receipt['runtime_projections'].items():
  f=ROOT/v['path'];assert f.is_file()and sha(f)==v['sha256'];paths[k]=f
 assert receipt['atlas_source']['selector']=='page'and set(receipt['atlas_source']['forbidden_prefixes'])=={'f84','f84r'}
 with paths['atlas_tsv'].open(newline='')as f:atlas=list(csv.DictReader(f,delimiter='\t'))
 lines=json.loads(paths['line_records_json'].read_text())['records'];assert all(not g['page'].startswith('f84')for g in atlas)
 return atlas,lines,receipt

def edge_bin(first,last,middle):return 'BOTH_EDGE'if first and last else 'FIRST_ONLY'if first else 'LAST_ONLY'if last else middle

def compute(s,atlas,lines):
 anchor={r[z]for r in s['anchors']for z in ['CH','SH']};response={r[z]:(1 if z=='CH'else-1)for r in s['responses']for z in ['CH','SH']};assert not anchor&response.keys()
 meta={(r['page'],r['locus']):r for r in lines};byline=defaultdict(list);pages=defaultdict(list)
 for g in atlas:
  byline[g['edition'],g['page'],g['locus']].append(g)
  if g['edition']==s['primary_edition']:pages[g['page']].append(g)
 for gs in byline.values():gs.sort(key=lambda g:int(g['source_group_index']))
 stable={}
 for page,locus in meta:
  sequences=[[g['ivtff_group_raw']for g in byline.get((ed,page,locus),[])]for ed in s['diagnostic_editions']]
  stable[page,locus]=bool(all(sequences)and all(x==sequences[0]for x in sequences))
 paralines=defaultdict(list)
 for m in lines:
  if m['strict_paragraph_id']:paralines[m['strict_paragraph_id']].append(m)
 linebin={}
 for pid,ls in paralines.items():
  ls.sort(key=lambda m:m['line_number'])
  for n,m in enumerate(ls):linebin[m['page'],m['locus']]=edge_bin(n==0,n==len(ls)-1,'INTERIOR')
 centers=[]
 for page,gs in pages.items():
  gs.sort(key=lambda g:(int(g['source_row_index']),int(g['source_group_index'])))
  for i,g in enumerate(gs):
   m=meta.get((page,g['locus']),{});pid=m.get('strict_paragraph_id');raw=g['ivtff_group_raw']
   if not pid or int(g['clean_ascii_fragment_count'])!=1 or g['clean_ascii_fragments']!=raw:continue
   pos=int(g['source_group_index']);n=int(g['source_group_count']);lb=edge_bin(pos<=2,pos>n-2,'MIDDLE').replace('FIRST_ONLY','FIRST2_ONLY').replace('LAST_ONLY','LAST2_ONLY');pb=linebin[page,g['locus']]
   for view in ['PRIMARY','DIAGNOSTIC']:
    offsets={};counts={};metrics={}
    for direction,sign in [('F',1),('B',-1)]:
     allowed=[];sides=[]
     for lag in s['lags']:
      j=i+sign*lag
      if not 0<=j<len(gs):continue
      path=gs[min(i,j):max(i,j)+1]
      if any(meta.get((page,x['locus']),{}).get('strict_paragraph_id')!=pid for x in path):continue
      if any(l['right_separator']=='UNCERTAIN_SMALL_SPACE'or l['right_separator'].startswith('DRAWING_')or r['left_separator']=='UNCERTAIN_SMALL_SPACE'or r['left_separator'].startswith('DRAWING_')for l,r in zip(path,path[1:])):continue
      if view=='DIAGNOSTIC'and not all(stable.get((page,x['locus']),False)for x in path):continue
      e=gs[j];side=response.get(e['ivtff_group_raw'],0)if int(e['clean_ascii_fragment_count'])==1 and e['clean_ascii_fragments']==e['ivtff_group_raw']else 0
      allowed.append(lag);sides.append(side)
     offsets[direction]=allowed;counts[direction]={'opportunities':len(sides),'CH':sides.count(1),'SH':sides.count(-1)}
     for tag,value in [('CH',1),('SH',-1)]:metrics[direction+'_'+tag]=sides.count(value)/len(sides)if sides else None
    if not offsets['F']or not offsets['B']:continue
    metrics['D']=metrics['F_CH']-metrics['F_SH']-metrics['B_CH']+metrics['B_SH']
    cell='|'.join([view,pid,lb,pb,','.join(map(str,offsets['F'])),','.join(map(str,offsets['B']))])
    centers.append({'id':g['source_group_id'],'view':view,'page':page,'folio':re.match(r'f\d+',page).group(),'locus':g['locus'],'surface':raw,'raw_index':pos,'cell':cell,'is_anchor':raw in anchor,'counts':counts,'metrics':metrics,'masks':offsets})
 pools=defaultdict(list)
 for c in centers:
  if not c['is_anchor']:pools[c['cell']].append(c)
 matches=[];used={}
 for c in centers:
  if not c['is_anchor']:continue
  pool=pools[c['cell']];row=dict(c,control_count=len(pool),matched=bool(pool))
  if pool:
   means={k:sum(x['metrics'][k]for x in pool)/len(pool)for k in c['metrics']};row['control_mean']=means;row['residual']={k:c['metrics'][k]-means[k]for k in means};used[c['cell']]=pool
  matches.append(row)
 summary={}
 for view in ['PRIMARY','DIAGNOSTIC']:
  allrows=[r for r in matches if r['view']==view];rs=[r for r in allrows if r['matched']];folios={r['folio']for r in rs};frac=len(rs)/len(allrows)if allrows else 0
  mean=lambda xs,key:{k:sum(x[key][k]for x in xs)/len(xs)for k in ['F_CH','F_SH','B_CH','B_SH','D']}if xs else None
  per={f:{'anchors':sum(r['folio']==f for r in rs),'mean_residual_D':sum(r['residual']['D']for r in rs if r['folio']==f)/sum(r['folio']==f for r in rs)}for f in sorted(folios)}
  summary[view]={'eligible_anchors':len(allrows),'matched_anchors':len(rs),'matched_folios':len(folios),'matched_fraction':frac,'unique_control_centers':len({x['id']for r in rs for x in used[r['cell']]}),'coverage_pass':len(rs)>=s['minimum_matched_anchors']and len(folios)>=s['minimum_matched_folios']and frac>=s['minimum_matched_fraction'],'all_eligible_anchor_mean':mean(allrows,'metrics'),'matched_anchor_mean':mean(rs,'metrics'),'matched_control_mean':mean(rs,'control_mean'),'mean_residual':mean(rs,'residual'),'per_folio':per}
 return matches,used,summary

def main():
 s=json.loads((B/'src/SPEC.json').read_text())
 for p,h in json.loads((B/'src/PREREG_LOCK.json').read_text()).items():assert sha(ROOT/p)==h,p
 atlas,lines,receipt=source(s);matches,cells,summary=compute(s,atlas,lines)
 write(A/'ANCHOR_MATCHES.json',matches);write(A/'CONTROL_CELLS.json',cells);write(A/'RESULT.json',{'status':'COMPLETE_RETROSPECTIVE_POSITION_PROFILE','claim_ceiling':'Descriptive matched-position specificity only; no causal/state/meaning or significance claim','views':summary});write(A/'SOURCE_RECEIPT.json',{'source_receipt':s['source_receipt'],'source_receipt_sha256':s['source_receipt_sha256'],'guarded_runtime_projections':receipt['runtime_projections']});print(json.dumps({v:{k:x[k]for k in ['eligible_anchors','matched_anchors','matched_folios','coverage_pass','mean_residual']}for v,x in summary.items()},sort_keys=True))
if __name__=='__main__':main()
