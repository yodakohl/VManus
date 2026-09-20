"""Registered descriptive decision and exact necessary-condition witnesses."""
import hashlib,json,subprocess
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def classify(target,ob):
 if not ob['localized'] or ob['seam']=='UNCERTAIN':return 'UNRESOLVED'
 compatible={'T18':'INTERNAL_LIKE','T21':'SPACE_LIKE'}
 return 'COMPATIBLE' if ob['seam']==compatible[target] else 'WEAKENED_PHYSICAL_PREMISE'
def witnesses(spec):
 old=read(R/spec['grammar']);lex={x['raw']:x['symbol'] for x in read(R/spec['source_draft'])['lexicon']};packet=read(R/spec['source_packet']);out={}
 for edition,row in packet['readers'].items():
  groups=[g for line in row['rows'] for g in line['groups']];n=len(groups);bad=[]
  for kind,start in [('INITIAL',0),('CONCLUSION',n-len(old['patterns']['CONCLUSION']))]:
   for j,p in enumerate(old['patterns'][kind]):
    i=start+j;g=groups[i];raw=g['ivtff_group_raw'];s=lex.get(raw);allowed=old['types'][p[1:]] if p.startswith('@') else [p]
    if s is not None and s not in allowed:bad.append(dict(required_clause=kind,position=i+1,source_id=g['source_group_id'],raw=raw,known_value=s,required_values=allowed))
  out[edition]=dict(groups=n,whole_paragraph_contract=row['whole_paragraph_contract'],strict_anchor_eligible=row['strict_anchor_eligible'],necessary_fixed_endpoint_patterns='CONTRADICTED' if bad else 'NOT_EXCLUDED_BY_THIS_RELAXATION',witnesses=bad,unknown_groups=sum(g['ivtff_group_raw'] not in lex for g in groups))
 return out

def main():
 for n,h in read(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
 reg=read(E/'artifacts/PUBLIC_REGISTRATION.json');subprocess.run(['git','cat-file','-e',reg['commit']+'^{commit}'],cwd=R,check=True)
 spec=read(E/'src/SPEC.json');ob=read(E/'artifacts/NATIVE_OBSERVATIONS.json');assert set(ob['targets'])==set(spec['targets'])
 for o in ob['targets'].values():
  assert type(o['localized']) is bool and o['seam'] in spec['judgments']
  for k in ['localization_note','neighbor_whole_gaps','internal_gaps','confidence','note']:assert isinstance(o[k],str) and o[k]
 results={k:classify(k,v) for k,v in ob['targets'].items()}
 decision='PARK_EXACT_PHYSICAL_TOKEN_REALIZATION' if 'WEAKENED_PHYSICAL_PREMISE' in results.values() else 'RETAIN_LOCAL_SOURCE_COMPATIBILITY_NO_MEANING_SUPPORT' if all(v=='COMPATIBLE' for v in results.values()) else 'RETAIN_WITH_UNRESOLVED_SOURCE_PREMISE'
 result=dict(decision=decision,seams=results,native_observations=ob,source_necessary_conditions=witnesses(spec),registration_commit=reg['commit'],confirmed_words=0,independent_meaning_capacity=0,significance=False,visual_judgment_verified_by_software=False)
 write(E/'artifacts/RESULT.json',result);print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
