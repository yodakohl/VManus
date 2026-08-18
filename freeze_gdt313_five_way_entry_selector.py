#!/usr/bin/env python3
"""Freeze two complete five-way wrapper cells before GDT313 scoring."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;SOURCE=R/'gdt278_native_event_inventory.tsv';PAIRS=R/'gdt303_pair_deltas.tsv';METHOD=R/'GDT313_FIVE_WAY_ENTRY_SELECTOR_METHOD.md';PANEL=R/'gdt313_frozen_panel.tsv';CAP=R/'gdt313_capacity.tsv';DESIGN=R/'gdt313_design.json';CHOICES=('NONE','ch','d','s','q')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def test(f):return int(hashlib.sha256(f'GDT311_SPLIT_V1|{f}'.encode()).hexdigest()[:8],16)%3==0
def main():
 events=[x for x in read(SOURCE) if x['control_id']=='VOYNICH_REFERENCE'];assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in events);rep={}
 for x in events:rep.setdefault(x['source_surface_sha256'],x)
 ops={}
 for op in ('wrapper:ch>s','wrapper:d>s','wrapper:NONE>q'):
  cells={}
  for p in read(PAIRS):
   if p['operation']!=op:continue
   e=rep[p['source_surface_sha256']];key=(p['page_host'],e['local_frame'],e['inner_d'],e['right_family'],e['dy_closure'],e['b3']);cells[key]=p
  ops[op]=cells
 shared=sorted(set(ops['wrapper:ch>s'])&set(ops['wrapper:d>s'])&set(ops['wrapper:NONE>q']));assert len(shared)==2;surface={};cell_names={}
 for key in shared:
  a=ops['wrapper:ch>s'][key];d=ops['wrapper:d>s'][key];q=ops['wrapper:NONE>q'][key];assert a['target_surface_sha256']==d['target_surface_sha256'];cid=hashlib.sha256(('CELL|'+'|'.join(key)).encode()).hexdigest()[:20];cell_names[cid]=key[0]
  for value,s in [('NONE',q['source_surface_sha256']),('q',q['target_surface_sha256']),('ch',a['source_surface_sha256']),('d',d['source_surface_sha256']),('s',a['target_surface_sha256'])]:assert s not in surface;surface[s]=(cid,value)
 pos={(x['locus'],int(x['group_index'])):x for x in events};out=[];truth={}
 for x in events:
  if x['source_surface_sha256'] not in surface:continue
  cid,choice=surface[x['source_surface_sha256']];prev=pos.get((x['locus'],int(x['group_index'])-1));eid=hashlib.sha256(x['observation_id'].encode()).hexdigest()[:20];truth[eid]=choice;out.append({'event_id_sha256':eid,'cell_id':cid,'opaque_host_id_sha256':hashlib.sha256(cell_names[cid].encode()).hexdigest()[:20],'split':'TEST' if test(x['physical_folio']) else 'TRAIN','physical_folio':x['physical_folio'],'page':x['page'],'locus':x['locus'],'register':x['register'],'line_first':int(x['group_index']=='1'),'prev_dy':int(prev is not None and prev['dy_closure']=='1'),'choice_withheld':'WITHHELD_UNTIL_SCORING'})
 out.sort(key=lambda x:(x['cell_id'],x['physical_folio'],x['locus'],x['event_id_sha256']));write(PANEL,out);caps=[]
 for cid in sorted(cell_names):
  rows=[x for x in out if x['cell_id']==cid];tr=[x for x in rows if x['split']=='TRAIN'];te=[x for x in rows if x['split']=='TEST'];caps.append({'cell_id':cid,'opaque_host_id_sha256':hashlib.sha256(cell_names[cid].encode()).hexdigest()[:20],'training_events':len(tr),'test_events':len(te),'training_choice_counts':json.dumps({c:sum(truth[x['event_id_sha256']]==c for x in tr) for c in CHOICES},sort_keys=True,separators=(',',':')),'test_choice_counts':json.dumps({c:sum(truth[x['event_id_sha256']]==c for x in te) for c in CHOICES},sort_keys=True,separators=(',',':'))})
 write(CAP,caps);d={'schema':'GDT313_FIVE_WAY_ENTRY_SELECTOR_DESIGN_V1','status':'FROZEN_BEFORE_FIVE_WAY_SCORING','choices':list(CHOICES),'split':'INHERIT_GDT311_SHA_FOLIO_SPLIT','ridge':10.0,'models':{'CELL':[],'LINE_START':['line_first'],'PREV_DY':['prev_dy'],'ENTRY_STATE':['line_first','prev_dy']},'null':{'worlds':8192,'seed':31320260818,'strata':'CELL_X_REGISTER','max_family':3},'decision':{'entry_gain_positive':True,'null_centered_positive':True,'max3_p_le':.05,'s_line_start_training_coefficient_positive':True,'s_line_start_held_matched_delta_positive':True,'q_prev_dy_training_coefficient_positive':True,'q_prev_dy_held_matched_delta_positive':True},'forbidden':['same_group_renderer_coordinates_as_predictors','host_glyphs','host_substrings','surface_identity_beyond_anonymous_cell'],'claim_ceiling':'Five-way stochastic formal selector in two known exact opaque cells only; no unseen cell morphology category meaning sound language plaintext or translation.','f84':{'authorized':False,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'inputs':{p.name:sha(p) for p in (SOURCE,PAIRS,METHOD)},'outputs':{p.name:sha(p) for p in (PANEL,CAP)},'implementation':{Path(__file__).name:sha(Path(__file__))}};d['content_sha256']=can(d);DESIGN.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':d['status'],'cells':len(caps),'events':len(out),'training':sum(int(x['training_events']) for x in caps),'test':sum(int(x['test_events']) for x in caps)},sort_keys=True))
if __name__=='__main__':main()
