"""Readable projections of preregistered descriptive cells; no new test."""
import json,hashlib
from pathlib import Path
from collections import Counter
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2];A=B/'artifacts'
receipt=json.loads((A/'GDT872_QUERY_RECEIPTS.json').read_text());binding=receipt['runtime_projections']['opportunities_json'];p=ROOT/binding['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==binding['sha256'];rows=json.loads(p.read_text())['records']
def cell(rs,labels):
 h=[r for r in rs if r['response_hit']];per={}
 for r in rs:per.setdefault((r['page'],r['anchor_page_group_index']),[]).append(r)
 return {**labels,'opportunities':len(rs),'hits':len(h),'same_side':sum(r['agreement']for r in h),'opposite_side':sum(r['disagreement']for r in h),'hit_folios':len({r['physical_folio']for r in h}),'eligible_anchors':len(per),'hit_rate':len(h)/len(rs) if rs else None,'macro_anchor_hit_rate':sum(sum(r['response_hit']for r in v)/len(v)for v in per.values())/len(per) if per else None}
out=[];byanchor=[];bypair=[]
for view in ['PRIMARY','DIAGNOSTIC']:
 for band in ['NEAR','DISTAL']:
  for rel in ['within_para','cross_para']:
   for direction in ['forward','backward']:
    labels={'view':view,'band':band,'boundary':rel,'direction':direction};rs=[r for r in rows if (r['view'],r['lag_band'],r['paragraph_relation'],r['direction'])==(view,band,rel,direction)];out.append(cell(rs,labels))
    for anchor in ['cheor','sheor','cheo','sheo']:byanchor.append(cell([r for r in rs if r['anchor_surface']==anchor],dict(labels,anchor=anchor)))
    for pair in [f'SP{x:02d}'for x in range(1,10)]:
     h=[r for r in rs if r['response_hit']and r['response_pair_id']==pair]
     bypair.append(dict(labels,response_pair=pair,shared_opportunities=len(rs),hits=len(h),same_side=sum(r['agreement']for r in h),opposite_side=sum(r['disagreement']for r in h),hit_folios=len({r['physical_folio']for r in h})))
for name,data in [('DIRECTION_SUMMARY.json',out),('ANCHOR_SUMMARY.json',byanchor),('RESPONSE_PAIR_SUMMARY.json',bypair)]: (A/name).write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
print('Three descriptive projections written; denominator reused, not summed across pairs.')
