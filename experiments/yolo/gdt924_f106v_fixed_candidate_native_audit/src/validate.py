#!/usr/bin/env python3
"""Mechanical packet audit; does not certify palaeographic judgments."""
import hashlib,json
from pathlib import Path
from PIL import Image
E=Path(__file__).resolve().parent.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def main():
 lock=read(E/'PREREG_LOCK.json')
 for p,h in lock.items(): assert sha(E/p)==h,(p,'lock')
 expected=read(E/'src/EXPECTED.json'); source=read(E/'src/SOURCE.json')
 assert len(expected['words'])==len(expected['source_group_ids'])==17
 assert len(set(expected['words']))==17
 assert source['page']==expected['page']=='f106v'
 original=Image.open(E/'runtime/f106v.jpg')
 assert original.size==(source['width'],source['height'])
 packets={r:read(E/f'src/OBSERVER_{r}.json') for r in ['A','B']}
 checks=[]
 for r,p in packets.items():
  assert p['reader'] in ({'A','A/root'} if r=='A' else {'B'}) and p['page']=='f106v'
  assert p['image_sha256']==sha(E/'runtime/f106v.jpg')
  assert len(p['rows'])==17 and p['exposure'] and p['limitations']
  for i,c in enumerate(p['rows']):
   assert (c['index'],c['expected'])==(i,expected['words'][i])
   assert c['status'] in {'MATCH','CONTRADICTED','UNRESOLVED'}
   assert c['confidence'] and c['observation']
  for v in p['views']:
   f=E/v['file']
   if not f.exists() and 'crop' in v: f=E/'artifacts'/Path(v['file']).name
   assert sha(f)==v['sha256']
   if 'crop' in v:
    box=v['crop']; assert len(box)==4 and 0<=box[0]<box[2]<=original.width and 0<=box[1]<box[3]<=original.height
    im=Image.open(f); cmp=original.crop(tuple(box))
    assert im.size==cmp.size and im.mode==cmp.mode and im.tobytes()==cmp.tobytes()
  checks.append({'reader':r,'rows':17,'views':len(p['views']),'packet_sha256':sha(E/f'src/OBSERVER_{r}.json')})
 result=read(E/'artifacts/RESULT.json')
 joint=[]
 for i,w in enumerate(expected['words']):
  a,b=(packets[r]['rows'][i]['status'] for r in ['A','B'])
  s=a if a==b else 'UNRESOLVED'
  joint.append(s)
  assert result['rows'][i]==dict(index=i,expected=w,A=a,B=b,joint=s)
 located=all(p['paragraph_localized'] and p['boundaries_resolved'] and p['line_counts']==[11,6] for p in packets.values())
 verdict='NATIVE_INPUT_UNRESOLVED'
 if 'CONTRADICTED' in joint: verdict='NATIVE_CONTRADICTION'
 if located and set(joint)=={'MATCH'}: verdict='NATIVE_INPUT_SUPPORTED'
 assert result['status']==verdict and result['complete_localization_and_boundaries']==located
 for s,k in [('MATCH','matching'),('UNRESOLVED','unresolved'),('CONTRADICTED','contradicted')]: assert result[f'joint_{k}_groups']==joint.count(s)
 assert result['confirmed_meanings']==0
 assert result['packet_hashes']=={r:sha(E/f'src/OBSERVER_{r}.json') for r in packets}
 out={'status':'PASS','scope':'Mechanical source, native crop pixels, packet completeness and reconciliation only; not independent certification of visual truth or Latin interpretation.','checks':checks,'preregistration_hashes_checked':len(lock),'joint_status':verdict,'joint_counts':{s:joint.count(s) for s in sorted(set(joint))},'source_sha256':sha(E/'runtime/f106v.jpg'),'result_sha256':sha(E/'artifacts/RESULT.json'),'validator_sha256':sha(Path(__file__))}
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
