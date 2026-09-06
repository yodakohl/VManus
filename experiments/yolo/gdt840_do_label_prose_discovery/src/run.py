import argparse,hashlib,importlib.util,json
from collections import defaultdict
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
s=importlib.util.spec_from_file_location('h829',ROOT/'experiments/yolo/gdt829_repeated_passage_reflow_capacity/src/run.py');h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
def dump(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def census(occ):
 out=[]
 for ed in ['ZL3b','IT2a','RF1b']:
  rows=[r for r in occ if r['edition']==ed];by=defaultdict(list)
  for r in rows:by[r['word']].append(r)
  for w in sorted(by):
   a=h.atoms(w)
   if len(a)<4 or [x[0] for x in a[-2:]]!=['d','o']:continue
   base=''.join(x[0] for x in a[:-2]);ext=by[w];bare=by.get(base,[])
   parts={'extended_labels':[r for r in ext if r['label']], 'bare_labels':[r for r in bare if r['label']], 'extended_prose':[r for r in ext if r['prose']], 'bare_prose':[r for r in bare if r['prose']]}
   if not(parts['extended_labels'] or parts['bare_labels']):continue
   out.append(dict(edition=ed,base=base,extended=w,**{k:[r['id'] for r in v] for k,v in parts.items()},same_page_forward=sorted({x['page'] for x in parts['extended_labels'] for y in parts['bare_prose'] if x['page']==y['page']})))
 return out
def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
 for n,v in json.loads((E/'src/PREREG_LOCK.json').read_text()).items():assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==v,n
 rows,guard=h.query(json.loads((E/'src/SPEC.json').read_text()));recs=h.records(rows)
 occ=[dict(id=g['source_group_id'],edition=g['edition'],page=g['page'],locus=g['locus'],index=int(g['source_group_index']),word=g['ivtff_group_raw'],label=r['kind']=='L' and len(r['groups'])==1,prose=r['kind']=='P') for r in recs.values() for g in r['groups'] if r['kind']=='P' or (r['kind']=='L' and len(r['groups'])==1)]
 allcards=census(occ);wanted={c['base'] for c in allcards}|{c['extended'] for c in allcards};selected=[r for r in occ if r['word'] in wanted]
 summary={ed:dict(candidates=sum(c['edition']==ed for c in allcards),forward_bases=[c['base'] for c in allcards if c['edition']==ed and c['extended_labels'] and c['bare_prose']],reverse_bases=[c['base'] for c in allcards if c['edition']==ed and c['bare_labels'] and c['extended_prose']]) for ed in ['ZL3b','IT2a','RF1b']}
 novel=[b for b in summary['ZL3b']['forward_bases'] if b!='ofal'];result=dict(status='REPLICATION_CAPACITY' if novel else 'NO_ADDITIONAL_FORWARD_BASE',summary=summary,guard=guard,source_occurrences=len(occ),saved_occurrences=len(selected))
 for name,x in [('OCCURRENCES.json',selected),('CARDS.json',allcards),('RESULT.json',result)]:
  path=E/'artifacts'/name;data=dump(x)
  if a.check:assert path.read_text()==data,name
  else:path.write_text(data)
 print(json.dumps({k:v for k,v in result.items() if k!='guard'},indent=2))
if __name__=='__main__':main()
