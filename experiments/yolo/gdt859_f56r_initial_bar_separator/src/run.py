import argparse,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def save(n,x,check=False):
 p=E/'artifacts'/n
 if check:assert p.read_text()==enc(x),n
 else:p.write_text(enc(x))
def extract(source,page,locus):return [line for line in source['lines'] if line['metadata']['page']==page and line['metadata']['locus']==locus]
def separators(line):
 g=line['groups'];return [dict(left_index=a[1],right_index=b[1],left_raw=a[2],right_raw=b[2],left_right_separator=a[4],right_left_separator=b[3],consecutive=int(b[1])==int(a[1])+1) for a,b in zip(g,g[1:])]
def controls():
 line=dict(metadata=dict(page='f1r',locus='f1r.1'),groups=[['a','1','x','LINE_START','UNCERTAIN_SPACE'],['b','2','y','UNCERTAIN_SPACE','LINE_END']]);s=dict(lines=[line])
 assert extract(s,'f1r','f1r.1')==[line] and not extract(s,'f1r','f1r.2');assert len(extract(dict(lines=[line,line]),'f1r','f1r.1'))==2;z=separators(line)[0];assert z['left_right_separator']==z['right_left_separator']=='UNCERTAIN_SPACE'
 return dict(status='PASS',tests=['missing','duplicate','uncertain_seam_preserved'])
def native(s):
 paths=[E/'artifacts'/n for n in ['VIEWER_A.json','VIEWER_B.json','A_SEAL.json']]
 if not all(p.exists() for p in paths):return dict(status='PENDING')
 a,b,seal=[json.loads(p.read_text()) for p in paths];assert hashlib.sha256(paths[0].read_bytes()).hexdigest()==seal['sha256'];assert isinstance(seal['sealed_at_utc'],str) and seal['sealed_at_utc']
 for obs in [a,b]:
  assert obs['page']==s['page'] and str(obs['canvas_id'])==s['native_source']['canvas_id'];assert set(obs['targets'])=={'AB','BC'} and isinstance(obs['note'],str)
  for t in obs['targets'].values():assert isinstance(t['localized'],bool) and t['connection'] in ['CONNECTED','NOT_CONNECTED','UNCERTAIN'] and isinstance(t['note'],str)
 return dict(status='AVAILABLE',viewer_A=a,viewer_B=b,A_seal=seal,AB_connected_support=all(o['targets']['AB']['localized'] and o['targets']['AB']['connection']=='CONNECTED' for o in [a,b]),BC_disconnected_support=all(o['targets']['BC']['localized'] and o['targets']['BC']['connection']=='NOT_CONNECTED' for o in [a,b]),vision_verified_by_software=False,ordinal_alignment_verified_by_software=False)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');ap.add_argument('--check',action='store_true');a=ap.parse_args()
 if a.controls:save('CONTROLS.json',controls());print('CONTROLS PASS');return
 s=json.loads((E/'src/SPEC.json').read_text());packet=dict(group_columns=s['group_columns'],editions={});issues=[]
 for ed in s['editions']:
  q=s['sources'][ed];p=ROOT/q['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==q['sha256'];source=json.loads(p.read_text());assert source['group_columns']==s['group_columns'];matches=extract(source,s['page'],s['locus']);packet['editions'][ed]=dict(source_sha256=q['sha256'],lines=matches)
  if len(matches)!=1:issues.append(dict(edition=ed,count=len(matches)))
  for line in matches:
   assert all(len(g)==len(s['group_columns']) for g in line['groups']);assert line['metadata']['page']=='f56r'
 seps={ed:[separators(line) for line in v['lines']] for ed,v in packet['editions'].items()};n=native(s)
 result=dict(status='SOURCE_INCOMPLETE' if issues else 'SOURCE_COMPLETE_NATIVE_PENDING' if n['status']=='PENDING' else 'LOCAL_NATIVE_AND_TRANSCRIPTION_AUDIT_COMPLETE',issues=issues,line_counts={ed:len(v['lines']) for ed,v in packet['editions'].items()},group_counts={ed:[len(line['groups']) for line in v['lines']] for ed,v in packet['editions'].items()},native=n)
 for name,value in [('SOURCE_LINES.json',packet),('SEPARATORS.json',seps),('RESULT.json',result)]:save(name,value,a.check)
 print(enc(result))
if __name__=='__main__':main()
