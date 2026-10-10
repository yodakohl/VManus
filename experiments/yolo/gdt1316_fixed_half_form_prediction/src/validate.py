import collections,csv,gzip,hashlib,json,math,re,statistics
from fractions import Fraction
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2];A='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
def read(p):
 v=p.read_bytes();return json.loads(gzip.decompress(v) if p.suffix=='.gz' else v)
def close(a,b):
 if a is None or b is None:assert a==b
 else:assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-11),(a,b)
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 allowed={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};strict=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');old=R/'experiments/yolo/gdt1308_whole_form_prediction/artifacts';oldmodel=read(old/'MODEL.json');old_events=read(old/'EVENTS.json.gz');new=read(B/'artifacts/EVENTS.json.gz');output=read(B/'artifacts/RESULT.json');saved_models=read(B/'artifacts/MODEL_H.json');joins=0;checked=0;table_cells=0
 assert [e['id'] for e in new]==[e['id'] for e in old_events]
 for ed,summary in output['readers'].items():
  sources={}
  for phase in ['DISCOVERY','EVALUATION']:
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{ed}.json')['lines']:
    for g in line['groups']:sources[g[0]]=(line['metadata'],g)
  train=[];held={};m1=collections.defaultdict(collections.Counter);whole=collections.defaultdict(collections.Counter);left=collections.defaultdict(collections.Counter);right=collections.defaultdict(collections.Counter);end=collections.Counter();Ns=collections.Counter()
  for row in strict[ed]:
   assert row['page'] in allowed and not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v');meta,g=sources[row['id']];assert row['page']==meta['page'] and row['locus']==meta['locus'] and row['kind']==meta['kind']=='P' and meta['edition']==ed;assert row['ivtff_group_raw']==g[2] and g[3]==g[4]=='DEFINITE_SPACE';u=tuple(row['units']);assert ''.join(u)==g[2] and set(u)<=set(A);joins+=1
   if len(u)<4:continue
   leaf=int(re.match(r'f(\d+)',row['page'])[1]);c=meta['currier'];cell=(c,len(u))
   if leaf%2:
    train.append(u);whole[cell][u]+=1;Ns[cell]+=1;k=len(u)//2;l=u[:k];r=u[k:];left[cell][l]+=1;right[cell,l[-1]][r]+=1;end[cell,l[-1]]+=1
    for i,s in enumerate(u):m1[c,len(u),i,u[i-1] if i else '^'][s]+=1
   else:held[row['id']]=(u,c,leaf)
  assert {tuple(x['cell']):{tuple(v['units']):v['count'] for v in x['counts']} for x in oldmodel[ed]['whole']}==dict(whole)
  assert {tuple(x['context']):x['counts'] for x in oldmodel[ed]['m1']}==dict(m1)
  assert len(saved_models[ed])==len(Ns)
  for table in saved_models[ed]:
   cell=tuple(table['cell']);N=Ns[cell];assert table['N']==N and {tuple(x['units']):x['count'] for x in table['left']}==dict(left[cell]);assert {(x['last_left'],tuple(x['units'])):x['count'] for x in table['right']}=={(a,r):cnt for (cl,a),rs in right.items() if cl==cell for r,cnt in rs.items()};assert table['end']=={a:v for (cl,a),v in end.items() if cl==cell}
   mass=Fraction(0)
   for l,count in left[cell].items():
    for r,rc in right[cell,l[-1]].items():mass+=Fraction(count*rc,N*end[cell,l[-1]])
   assert mass==1;table_cells+=1
  assert summary['train_cells']==len(Ns) and summary['left_entries']==sum(map(len,left.values())) and summary['right_seam_entries']==sum(map(len,right.values())) and summary['whole_cell_entries']==sum(map(len,whole.values()))
  known=set(train);events=[e for e in new if e['reader']==ed];assert set(held)=={e['id'] for e in events}
  for e in events:
   u,c,leaf=held[e['id']];assert tuple(e['units'])==u and e['leaf']==leaf and e['c']==c and e['global_unseen']==(u not in known);cell=(c,len(u));N=Ns[cell];lp=0
   for i,s in enumerate(u):counts=m1.get((c,len(u),i,u[i-1] if i else '^'),{});lp+=math.log((counts.get(s,0)+.5)/(sum(counts.values())+11))
   p=math.exp(lp);q=whole[cell][u]/N if N else 0;k=len(u)//2;l=u[:k];r=u[k:];den=end[cell,l[-1]];h=float(Fraction(left[cell][l]*right[cell,l[-1]][r],N*den)) if N and den else 0;mh=(p+h)/2 if N else p;mq=(p+q)/2 if N else p
   for a,b in [(e['p'],p),(e['q'],q),(e['mix'],mq),(e['h'],h),(e['mix_h'],mh),(e['gain_m1'],math.log(mh)-lp),(e['gain_whole'],math.log(mh)-math.log(mq))]:close(a,b)
   assert e['cell_train_N']==N
   if N and h==0:close(e['gain_m1'],-math.log(2))
   checked+=1
  for cohort,report in summary['cohorts'].items():
   es=[e for e in events if cohort=='ALL' or cohort=='GLOBAL_UNSEEN' and e['global_unseen'] or cohort=='GLOBAL_KNOWN' and not e['global_unseen'] or cohort=='Q_ZERO' and e['q']==0 or cohort=='H_POSITIVE' and e['h']>0 or cohort=='H_ZERO' and e['h']==0];leaves=sorted({e['leaf'] for e in es});per={str(l):statistics.fmean(e['gain_m1'] for e in es if e['leaf']==l) for l in leaves};pw={str(l):statistics.fmean(e['gain_whole'] for e in es if e['leaf']==l) for l in leaves};N=len(es);L=len(leaves);pos=sum(x>0 for x in per.values());mean=statistics.fmean(per.values()) if L else None
   assert report['words']==N and report['leaves']==L and report['positive_leaves']==pos
   close(report['equal_leaf_gain_m1'],mean);close(report['token_gain_m1'],statistics.fmean(e['gain_m1'] for e in es) if N else None);close(report['equal_leaf_gain_whole'],statistics.fmean(pw.values()) if L else None);close(report['mean_mix_h_loss'],-statistics.fmean(math.log(e['mix_h']) for e in es) if N else None)
   assert set(per)==set(report['per_leaf_gain_m1'])==set(report['per_leaf_gain_whole'])
   for l in per:close(per[l],report['per_leaf_gain_m1'][l]);close(pw[l],report['per_leaf_gain_whole'][l])
   assert report['material_gate']==bool(N>=100 and L>=10 and mean>=.01 and pos*3>=2*L)
  assert summary['lead']==(summary['cohorts']['ALL']['material_gate'] and summary['cohorts']['GLOBAL_UNSEEN']['material_gate'])
 assert output['status']==('PRODUCTIVE_HALF_FORM_LEAD' if output['readers']['ZL3b']['lead'] else 'NO_PRODUCTIVE_HALF_FORM_LEAD')
 receipt={'status':'PASS','source_joins':joins,'native_word_scores':checked,'exactly_normalized_fragment_tables':table_cells,'method':'Independent source reconstruction, occurrence-level chunk counts, exact rational H and log-domain M1; all original baseline and new scores/gates checked. Not independent manuscript or language confirmation.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
