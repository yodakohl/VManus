from pathlib import Path
import argparse,collections,csv,datetime,hashlib,json,time
E=Path(__file__).resolve().parents[1];R=E.parents[2]
D=R/'research_registry/work_batches/ten_hours_20260915'
P=R/'experiments/yolo/gdt970_rota_whole_part_conjugacy/artifacts/PARAGRAPHS.json'
RULES=['MIN_GROUPS','HEADER_WIDTH','HEADER_ISOLATION','ALL_GROUP_MIN','GLOBAL_INITIAL','HEADER_ENTRY','HEADER_END']
BOUNDS={'R1':[(12,144),(5,56),(5,56),(3,24)],'R2':[(10,128),(3,40),(3,40),(1,8)]}
def write(n,x):(E/'artifacts'/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def inspect(words,model):
 flags={k:None for k in RULES};flags['MIN_GROUPS']=len(words)>=5;conflicts=[]
 if len(words)>=4:
  flags['HEADER_WIDTH']=all(lo<=len(w)<=hi for w,(lo,hi) in zip(words[:4],BOUNDS[model]))
  conflicts=[[i,j,w] for i,h in enumerate(words[:4]) for j,w in enumerate(words) if i!=j and (h.startswith(w) or w.startswith(h))]
  flags['HEADER_ISOLATION']=not conflicts
  if model=='R1':
   flags['ALL_GROUP_MIN']=min(map(len,words))>=3
   flags['GLOBAL_INITIAL']=len({w[0] for w in words})<=2
   flags['HEADER_ENTRY']=len({w[0] for w in words[1:4]})==1
   flags['HEADER_END']=len({w[-1] for w in words[:4]})==1
 bad=[k for k in RULES if flags[k] is False]
 return dict(header=words[:4],header_lengths=list(map(len,words[:4])),min_group_length=min(map(len,words)) if words else None,initials=sorted({w[0] for w in words}),conditions=flags,prefix_conflicts=conflicts,contradictions=bad,decision=bad[0] if bad else 'NECESSARY_FORM_ONLY')
def preflight():
 out={}
 for model,slug in [('R1','raw_alloy_r1_compositional_group_code'),('R2','raw_alloy_r2_operator_allomorph_code')]:
  d=json.loads((R/f'research_registry/proposals/{slug}.json').read_text())['design'];atoms=d['writing_family']['atoms']
  key={a:chr(97+i//26)+chr(97+i%26) for i,a in enumerate(atoms)} if model=='R1' else d['code_existence_witness']['dictionary']
  rows={};examples=[]
  for name,x in d['source_example_streams'].items():
   words=[''.join(key[a] for a in group) for group in x['groups']];v=inspect(words,model);assert v['decision']=='NECESSARY_FORM_ONLY',(model,name,v);rows[name]=dict(groups=len(words),header=words[:4],decision=v['decision']);examples.append(words)
  base=examples[0];bad={'MIN_GROUPS':base[:4]};q=base.copy();q[0]='z';bad['HEADER_WIDTH']=q;q=base.copy();q[-1]=base[3];bad['HEADER_ISOLATION']=q
  if model=='R1':
   q=base.copy();q[-1]='z';bad['ALL_GROUP_MIN']=q
   q=base.copy();q[-3:]=['xxx','yyy','zzz'];bad['GLOBAL_INITIAL']=q
   q=base.copy();q[1]='z'+q[1];bad['HEADER_ENTRY']=q
   q=base.copy();q[0]+='z';bad['HEADER_END']=q
  checks={}
  for rule,w in bad.items():v=inspect(w,model);assert v['conditions'][rule] is False;checks[rule]=v['contradictions']
  out[model]=dict(accounts=rows,corruptions=checks,key=key)
 write('PREFLIGHT.json',dict(status='PASS_SOURCE_ONLY',models=out,target_access=False));print('PASS eight full source/generated cases and ten fixed corruptions')
def summarize(rows):
 out={}
 for model in ['R1','R2']:
  out[model]={}
  for ed in ['ZL3b','IT2a','RF1b']:
   rr=[x for x in rows if x['model']==model and x['edition']==ed];eligible=[x for x in rr if x['eligible']];sv=[x for x in eligible if x['decision']=='NECESSARY_FORM_ONLY']
   out[model][ed]=dict(complete=len(rr),eligible=len(eligible),unknown=len(rr)-len(eligible),literal_leaves=len({x['leaf'] for x in eligible}),first=dict(collections.Counter(x['decision'] for x in eligible)),all_failures=dict(collections.Counter(k for x in eligible for k in x['contradictions'])),survivors=[x['id'] for x in sv],survivor_leaves=sorted({x['leaf'] for x in sv}))
 return out
def table(rows):
 with (E/'artifacts/CANDIDATE_PREDICTIONS.tsv').open('w') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['model','edition','id','page','leaf','eligible','defects','groups','header',*RULES,'prefix_conflicts','contradictions','decision'])
  j=lambda x:json.dumps(x,separators=(',',':'))
  for x in rows:w.writerow([x['model'],x['edition'],x['id'],x['page'],x['leaf'],str(x['eligible']),j(x['defects']),x['groups'],j(x['header']),*[str(x['conditions'][k]) for k in RULES],j(x['prefix_conflicts']),j(x['contradictions']),x['decision']])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--preflight',action='store_true');a=ap.parse_args()
 if a.preflight:return preflight()
 for n,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
 allowed=set(json.loads((R/'experiments/yolo/gdt915_terminal_lr_phrase_transfer/src/SPEC.json').read_text())['allowed_selectors']);assert len(allowed)==179 and not any(x.startswith('f84') or x=='f116v' for x in allowed)
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic();payload=json.loads(P.read_text());rows=[]
 for model in ['R1','R2']:
  for ed,pp in payload.items():
   for p in pp:
    assert p['page'] in allowed
    words=[w for line in p['lines'] for w in line['words']];assert ' '.join(words)==p['full_text']
    x=dict(model=model,edition=ed,id=p['id'],page=p['page'],leaf=p['leaf'],eligible=p['literal_eligible'],defects=p['defects'],groups=len(words))
    if x['eligible']:assert words and all(w and all('a'<=c<='z' for c in w) for w in words);x.update(inspect(words,model))
    else:x.update(header=None,header_lengths=None,min_group_length=None,initials=None,conditions={k:None for k in RULES},prefix_conflicts=[],contradictions=[],decision='UNKNOWN_NONLITERAL_COMPLETE')
    rows.append(x)
 panels=summarize(rows);survivors={m:sum(len(v['survivors']) for v in panels[m].values()) for m in panels}
 result=dict(status={m:'ALL_LITERAL_FORMS_CONTRADICTED' if n==0 else 'NECESSARY_FORM_SURVIVORS_NO_FULL_READING' for m,n in survivors.items()},panels=panels,survivors=survivors,rows=len(rows),started_utc=start,elapsed_seconds=time.monotonic()-t,translated_words=0,independent_confirmation_capacity=0,reserve_access=False,full_code_or_arithmetic_tested=False)
 write('PREDICTIONS.json',rows);write('RESULT.json',result);table(rows);print(json.dumps(result))
if __name__=='__main__':main()
