from pathlib import Path
import gzip,hashlib,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def nominate(u):
 if u[-2:]!=['d','y']:return None
 c=[];n=[]
 for x in u[:-2]:
  if x in ('e','i') and c and c[-1]==x:n[-1]+=1
  else:c.append(x);n.append(1)
 if not c or len(c)%2:return None
 h=len(c)//2
 if c[:h]!=c[h:]:return None
 slots=[j for j in range(1,h-1) if c[j] in ('e','i')]
 pairs=[{'slot':j,'unit':c[j],'left':n[j],'right':n[j+h]} for j in slots]
 return {'skeleton':c[:h],'collapsed_run_lengths':n,'inner_pairs':pairs,'eligible':bool(slots),'mismatch':any(p['left']!=p['right'] for p in pairs)}
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 assert nominate(['a','e','l','a','e','e','l','d','y'])['mismatch']
 assert not nominate(['a','e','l','a','e','l','d','y'])['mismatch']
 assert not nominate(['ch','e','ch','e','e','d','y'])['eligible']
 assert nominate(['o','l','o','l','d','y'])['inner_pairs']==[]
 data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');out={};summ={}
 for ed,rows in sorted(data.items()):
  out[ed]=[]
  for r in sorted(rows,key=lambda r:(r['ivtff_group_raw'],r['id'])):
   x=nominate(r['units'])
   if x is not None:out[ed].append(dict(r,**x))
  ev=out[ed];eligible=[x for x in ev if x['eligible']];forms=sorted({x['ivtff_group_raw'] for x in eligible})
  summ[ed]={'groups':len(rows),'collapsed_echo_candidates':len(ev),'candidate_types':len({x['ivtff_group_raw'] for x in ev}),'eligible_occurrences':len(eligible),'eligible_types':len(forms),'mismatching_occurrences':sum(x['mismatch'] for x in eligible),'manual_first_forms':forms[:8],'status':'WITNESSES_ONLY' if eligible else 'NO_HOMOLOGOUS_INNER_RUN_OPPORTUNITY'}
 result={'status':'NO_HOMOLOGOUS_INNER_RUN_OPPORTUNITY' if all(x['eligible_occurrences']==0 for x in summ.values()) else 'READER_SPECIFIC_WITNESSES_ONLY','readers':summ,'inference':'Exploratory nomination only; no source identity, copy mechanism, meaning or significance.'}
 for name,obj in [('CANDIDATES.json',out),('RESULT.json',result)]:(B/'artifacts'/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
