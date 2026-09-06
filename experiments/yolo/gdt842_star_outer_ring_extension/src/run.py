import argparse,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
 for n,v in json.loads((E/'src/PREREG_LOCK.json').read_text()).items():assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==v,n
 s=json.loads((E/'src/SPEC.json').read_text());reads=[]
 for viewer in ['A','B']:
  r=json.loads((E/f'artifacts/VIEWER_{viewer}.json').read_text());assert r['image_sha256']==s['image_sha256'];assert r['viewer']==viewer
  assert [x['id'] for x in r['judgments']]==[x['id'] for x in s['targets']]
  assert all(x['state'] in s['states'] and x['reason'] for x in r['judgments']);reads.append(r['judgments'])
 pairs=[dict(id=x['id'],A=x['state'],B=y['state'],agree=x['state']==y['state']) for x,y in zip(*reads)]
 agreed=[x['A'] for x in pairs if x['agree']];passed=len(agreed)>=s['minimum_agreement'] and all(agreed.count(k)>=s['minimum_each_clear_class'] for k in s['states'][:2])
 result=dict(status='VISUAL_RING_EXTENSION_PASS' if passed else 'STOP_VISUAL_CAPACITY',agreement=len(agreed),total=len(pairs),agreed_pigmented=agreed.count('PIGMENTED_CENTRE'),agreed_outline=agreed.count('OUTLINE_CENTRE'),pairs=pairs)
 data=json.dumps(result,indent=2)+'\n';path=E/'artifacts/RESULT.json'
 if a.check:assert path.read_text()==data
 else:path.write_text(data)
 print(data)
if __name__=='__main__':main()
