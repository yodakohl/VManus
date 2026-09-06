import argparse,csv,hashlib,importlib.util,io,json,subprocess
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
p=ROOT/'experiments/yolo/gdt829_repeated_passage_reflow_capacity/src/run.py';s=importlib.util.spec_from_file_location('h829',p);h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
def dump(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
 for n,v in json.loads((E/'src/PREREG_LOCK.json').read_text()).items():assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==v,n
 s=json.loads((E/'src/SPEC.json').read_text());cols=['blind_id','selector','locus','a_member','crop_source_id','crop_x','crop_y','crop_width','crop_height']
 cmd=['./vmanus-exp','query-tsv',s['crop_key'],'--selector','selector','--allow','f70v1','--columns',','.join(cols),'--forbid-prefix','f84','--forbid-prefix','f84r'];p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True);boxes=list(csv.DictReader(io.StringIO(p.stdout),delimiter='\t'));assert len(boxes)==9 and all(b['crop_source_id']=='YALE_1006201_F70' for b in boxes)
 prior=json.loads((ROOT/'experiments/yolo/gdt842_star_outer_ring_extension/artifacts/RESULT.json').read_text());states={p['id']:p for p in prior['pairs']};joins=[]
 for t in s['targets']:
  x=t['x']*s['native_width']/s['width'];y=t['y']*s['native_height']/s['height'];hits=[b for b in boxes if int(b['crop_x'])<=x<=int(b['crop_x'])+int(b['crop_width']) and int(b['crop_y'])<=y<=int(b['crop_y'])+int(b['crop_height'])]
  state=states[t['id']];joins.append(dict(id=t['id'],x_native=x,y_native=y,crop_ids=[b['blind_id'] for b in hits],locus=hits[0]['locus'] if len(hits)==1 else None,legacy_a_member=hits[0]['a_member'] if len(hits)==1 else None,clear=state['agree'] and state['A']!='UNCERTAIN',appearance=state['A'] if state['agree'] else 'DISAGREE',ownership='LEGACY_CROP_CONTEXT_ONLY'))
 rows,guard=h.query(s);recs=h.records(rows);loci={j['locus'] for j in joins if j['locus']};raw=[g for (ed,locus),r in recs.items() if locus in loci for g in r['groups']];assert all((ed,locus) in recs for ed in ['ZL3b','IT2a','RF1b'] for locus in loci)
 result=dict(status='PROVENANCE_INTAKE_ONLY_NO_AUTHORIAL_EDGE',targets=len(joins),unique_links=sum(j['locus'] is not None for j in joins),clear_targets=sum(j['clear'] for j in joins),clear_linked=sum(j['clear'] and j['locus'] is not None for j in joins),unmatched=[j['id'] for j in joins if not j['crop_ids']],ambiguous=[j['id'] for j in joins if len(j['crop_ids'])>1],raw_groups=len(raw),authorial_edges=0,guard=guard)
 for name,obj in [('CROPS.json',boxes),('JOINS.json',joins),('RAW_GROUPS.json',raw),('RESULT.json',result)]:
  path=E/'artifacts'/name;data=dump(obj)
  if a.check:assert path.read_text()==data,name
  else:path.write_text(data)
 print(json.dumps({k:v for k,v in result.items() if k!='guard'},indent=2))
if __name__=='__main__':main()
