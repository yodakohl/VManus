#!/usr/bin/env python3
"""Separate exhaustive center/mask audit plus an analytically counted fixture."""
import json,sys,importlib.util,math,re
from collections import defaultdict
from pathlib import Path
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2];A=B/'artifacts'
def module():
 sp=importlib.util.spec_from_file_location('g873builder',B/'src/run.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def fixture(m):
 s=json.loads((B/'src/SPEC.json').read_text());s['anchors']=[{'pair_id':'A','CH':'a','SH':'b'}];s['responses']=[{'pair_id':'R','CH':'x','SH':'y'}]
 values=['z']*30;values[10]='a';values[13]='x';values[6]='y';lines=[{'page':'f1r','locus':'f1r.1','line_number':1,'strict_paragraph_id':'P'}];atlas=[]
 for ed in s['diagnostic_editions']:
  for i,v in enumerate(values,1):atlas.append({'edition':ed,'page':'f1r','locus':'f1r.1','source_group_id':ed+str(i),'source_row_index':'1','source_group_index':str(i),'source_group_count':'30','ivtff_group_raw':v,'clean_ascii_fragments':v,'clean_ascii_fragment_count':'1','left_separator':'SPACE','right_separator':'SPACE'})
 anchors,cells,result=m.compute(s,atlas,lines);assert len(anchors)==2
 for a in anchors:
  assert a['control_count']==13 and math.isclose(a['metrics']['D'],1/3)
  assert a['masks']=={'F':[3,4,5,6,7,8],'B':[3,4,5,6,7,8]}
 assert all(not v['coverage_pass'] for v in result.values())
 # A reading mismatch removes only the diagnostic matched anchor.
 next(g for g in atlas if g['edition']=='RF1b'and g['source_group_index']=='1')['ivtff_group_raw']='other'
 anchors,_,_=m.compute(s,atlas,lines);assert len(anchors)==1 and anchors[0]['view']=='PRIMARY'
 print('PASS_SYNTHETIC_EXHAUSTIVE_13_CONTROLS_SIGNED_DENSITY_AND_READING_MASK')

def independent(s,atlas,lines):
 meta={(r['page'],r['locus']):r for r in lines};paragraphs=defaultdict(list)
 for x in lines:
  if x['strict_paragraph_id']:paragraphs[x['strict_paragraph_id']].append(x)
 plbin={}
 for pid,ls in paragraphs.items():
  ordered=sorted(ls,key=lambda x:x['line_number'])
  for i,x in enumerate(ordered):plbin[x['page'],x['locus']]=['BOTH_EDGE'if len(ls)==1 else 'FIRST_ONLY'if i==0 else 'LAST_ONLY'if i==len(ls)-1 else 'INTERIOR'][0]
 groups=defaultdict(list)
 for g in atlas:groups[g['edition'],g['page'],g['locus']].append(g)
 for gs in groups.values():gs.sort(key=lambda g:int(g['source_group_index']))
 stable={}
 for key in meta:
  seq=[[g['ivtff_group_raw']for g in groups.get((ed,)+key,[])]for ed in s['diagnostic_editions']];stable[key]=bool(all(seq)and len({tuple(v)for v in seq})==1)
 pages=defaultdict(list)
 for g in atlas:
  if g['edition']==s['primary_edition']:pages[g['page']].append(g)
 anchors={x[k]for x in s['anchors']for k in ['CH','SH']};responses={x[k]:k for x in s['responses']for k in ['CH','SH']};out={}
 for page,gs in pages.items():
  gs.sort(key=lambda g:(int(g['source_row_index']),int(g['source_group_index'])))
  for c,g in enumerate(gs):
   mm=meta.get((page,g['locus']),{});pid=mm.get('strict_paragraph_id');raw=g['ivtff_group_raw']
   if not pid or g['clean_ascii_fragment_count']!='1'or g['clean_ascii_fragments']!=raw:continue
   i=int(g['source_group_index']);n=int(g['source_group_count']);first=i<3;last=n-i<2;lb='BOTH_EDGE'if first and last else 'FIRST2_ONLY'if first else 'LAST2_ONLY'if last else 'MIDDLE'
   for view in ['PRIMARY','DIAGNOSTIC']:
    masks={'F':[],'B':[]};count={d:{'opportunities':0,'CH':0,'SH':0}for d in ['F','B']}
    for e in range(max(0,c-8),min(len(gs),c+9)):
     lag=abs(e-c)
     if lag not in s['lags']:continue
     low,high=sorted([c,e]);path=gs[low:high+1]
     if any(meta.get((page,h['locus']),{}).get('strict_paragraph_id')!=pid for h in path):continue
     if view=='DIAGNOSTIC'and any(not stable.get((page,h['locus']))for h in path):continue
     separators=[v for l,r in zip(path,path[1:])for v in [l['right_separator'],r['left_separator']]]
     if any(v=='UNCERTAIN_SMALL_SPACE'or v.startswith('DRAWING_')for v in separators):continue
     d='F'if e>c else 'B';masks[d].append(lag);count[d]['opportunities']+=1;t=gs[e]
     if t['clean_ascii_fragment_count']=='1'and t['ivtff_group_raw']==t['clean_ascii_fragments']and t['ivtff_group_raw']in responses:count[d][responses[t['ivtff_group_raw']]]+=1
    if any(not masks[d]for d in masks):continue
    for v in masks.values():v.sort()
    metric={d+'_'+k:count[d][k]/count[d]['opportunities']for d in ['F','B']for k in ['CH','SH']};metric['D']=metric['F_CH']-metric['F_SH']-metric['B_CH']+metric['B_SH']
    cell='|'.join([view,pid,lb,plbin[page,g['locus']],','.join(map(str,masks['F'])),','.join(map(str,masks['B']))])
    out[view,g['source_group_id']]={'cell':cell,'counts':count,'metrics':metric,'is_anchor':raw in anchors,'folio':re.match(r'f\d+',page).group()}
 return out

def main():
 m=module();fixture(m)
 if '--self-test'in sys.argv:return
 s=json.loads((B/'src/SPEC.json').read_text());atlas,lines,_=m.source(s);centers=independent(s,atlas,lines)
 matches=json.loads((A/'ANCHOR_MATCHES.json').read_text());pools=json.loads((A/'CONTROL_CELLS.json').read_text());result=json.loads((A/'RESULT.json').read_text())['views']
 expectedanchors={k for k,v in centers.items()if v['is_anchor']};assert {(r['view'],r['id'])for r in matches}==expectedanchors
 for r in matches:
  v=centers[r['view'],r['id']];assert r['cell']==v['cell']and r['counts']==v['counts']and r['metrics']==v['metrics']and r['folio']==v['folio']
  candidates={k for k,x in centers.items()if not x['is_anchor']and x['cell']==v['cell']};assert r['control_count']==len(candidates)and r['matched']==bool(candidates)
  if candidates:
   ps=pools[v['cell']];assert {(p['view'],p['id'])for p in ps}==candidates
   for p in ps:assert p['counts']==centers[p['view'],p['id']]['counts']and p['metrics']==centers[p['view'],p['id']]['metrics']
   for metric in v['metrics']:
    expected=sum(centers[k]['metrics'][metric]for k in sorted(candidates))/len(candidates)
    assert math.isclose(r['control_mean'][metric],expected,abs_tol=1e-12)
    assert math.isclose(r['residual'][metric],v['metrics'][metric]-expected,abs_tol=1e-12)
 for view,x in result.items():
  rs=[r for r in matches if r['view']==view];matched=[r for r in rs if r['matched']];nf=len({r['folio']for r in matched});fraction=len(matched)/len(rs)if rs else 0
  assert (x['eligible_anchors'],x['matched_anchors'],x['matched_folios'],x['matched_fraction'])==(len(rs),len(matched),nf,fraction)
  assert x['coverage_pass']==(len(matched)>=s['minimum_matched_anchors']and nf>=s['minimum_matched_folios']and fraction>=s['minimum_matched_fraction'])
  for field,key,rr in [('all_eligible_anchor_mean','metrics',rs),('matched_anchor_mean','metrics',matched),('matched_control_mean','control_mean',matched),('mean_residual','residual',matched)]:
   if not rr:assert x[field]is None
   else:
    for metric in rr[0][key]:assert math.isclose(x[field][metric],sum(r[key][metric]for r in rr)/len(rr),abs_tol=1e-12)
  for f,item in x['per_folio'].items():
   rr=[r for r in matched if r['folio']==f];assert item['anchors']==len(rr)and math.isclose(item['mean_residual_D'],sum(r['residual']['D']for r in rr)/len(rr),abs_tol=1e-12)
 validation={'status':'PASS','scope':'independent exhaustive center/mask/pool and metric audit; synthetic13control fixture; no significance or meaning','center_profiles':len(centers),'anchor_profiles':len(matches),'input_hashes':{p.name:m.sha(p)for p in [B/'src/SPEC.json',B/'src/run.py',B/'src/validate.py',A/'RESULT.json']}}
 (A/'VALIDATION.json').write_text(json.dumps(validation,indent=2,sort_keys=True)+'\n');print(json.dumps(validation,sort_keys=True))
if __name__=='__main__':main()
