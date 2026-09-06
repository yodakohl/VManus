import argparse,hashlib,json
from PIL import Image
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def read(n):return json.loads((E/'artifacts'/n).read_text())
def choose(data,page,locus):
 answer=[]
 for line in data['lines']:
  m=line['metadata']
  if (m['page'],m['locus'])==(page,locus):answer.append(line)
 return answer
def boundaries(line):
 out=[]
 for i in range(1,len(line['groups'])):
  left,right=line['groups'][i-1:i+1];out.append(dict(left_index=left[1],right_index=right[1],left_raw=left[2],right_raw=right[2],left_right_separator=left[4],right_left_separator=right[3],consecutive=int(right[1])-int(left[1])==1))
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');a=ap.parse_args();toy=dict(metadata=dict(page='f1r',locus='f1r.1'),groups=[['a','1','x','LINE_START','UNCERTAIN_SPACE'],['b','2','y','UNCERTAIN_SPACE','LINE_END']]);assert choose(dict(lines=[toy]),'f1r','f1r.1')==[toy];assert choose(dict(lines=[toy]),'f1r','f1r.2')==[];assert len(choose(dict(lines=[toy,toy]),'f1r','f1r.1'))==2;assert boundaries(toy)[0]['left_right_separator']=='UNCERTAIN_SPACE'
 if a.controls:print('INDEPENDENT CONTROLS PASS');return
 s=json.loads((E/'src/SPEC.json').read_text());saved=read('SOURCE_LINES.json');seps=read('SEPARATORS.json');result=read('RESULT.json');assert saved['group_columns']==s['group_columns'];issues=[];counts={};gc={}
 for ed,q in s['sources'].items():
  raw=(ROOT/q['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==q['sha256'];original=json.loads(raw);assert original['group_columns']==s['group_columns'];lines=choose(original,'f56r','f56r.1');assert saved['editions'][ed]==dict(source_sha256=q['sha256'],lines=lines);assert seps[ed]==[boundaries(line) for line in lines];counts[ed]=len(lines);gc[ed]=[len(line['groups']) for line in lines]
  if len(lines)!=1:issues.append(dict(edition=ed,count=len(lines)))
 assert sorted(issues,key=lambda x:x['edition'])==sorted(result['issues'],key=lambda x:x['edition']);assert result['line_counts']==counts and result['group_counts']==gc
 n=result['native'];exists=all((E/'artifacts'/f).exists() for f in ['VIEWER_A.json','VIEWER_B.json','A_SEAL.json'])
 if exists:
  aa=read('VIEWER_A.json');bb=read('VIEWER_B.json');seal=read('A_SEAL.json');assert hashlib.sha256((E/'artifacts/VIEWER_A.json').read_bytes()).hexdigest()==seal['sha256'];assert isinstance(seal['sealed_at_utc'],str) and seal['sealed_at_utc'];assert n['viewer_A']==aa and n['viewer_B']==bb and n['A_seal']==seal
  for ob in [aa,bb]:
   assert ob['page']=='f56r' and str(ob['canvas_id'])=='1006184' and set(ob['targets'])=={'AB','BC'} and isinstance(ob['note'],str)
   for v in ob['targets'].values():assert type(v['localized']) is bool and v['connection'] in {'CONNECTED','NOT_CONNECTED','UNCERTAIN'} and isinstance(v['note'],str)
  assert n['AB_connected_support']==all(ob['targets']['AB']['localized'] and ob['targets']['AB']['connection']=='CONNECTED' for ob in [aa,bb]);assert n['BC_disconnected_support']==all(ob['targets']['BC']['localized'] and ob['targets']['BC']['connection']=='NOT_CONNECTED' for ob in [aa,bb]);assert n['vision_verified_by_software'] is False and n['ordinal_alignment_verified_by_software'] is False and n['status']=='AVAILABLE'
 else:assert n==dict(status='PENDING')
 assert result['status']==('SOURCE_INCOMPLETE' if issues else 'LOCAL_NATIVE_AND_TRANSCRIPTION_AUDIT_COMPLETE' if exists else 'SOURCE_COMPLETE_NATIVE_PENDING')
 source_doc=json.loads((ROOT/s['source_provenance']).read_text());assert s['native_source'] in source_doc['source_images']
 image_meta=s['native_source'];image_file=ROOT/'docs/visual_overview/runtime'/image_meta['cache_filename'];assert image_file.is_file(),'Original source image missing; see README'
 assert image_file.stat().st_size==image_meta['bytes'] and hashlib.sha256(image_file.read_bytes()).hexdigest()==image_meta['sha256']
 with Image.open(image_file) as image:assert image.size==(image_meta['width'],image_meta['height'])
 validation=dict(status='PASS',source_hash_and_lossless_line_parity=True,original_image_hash_bytes_dimensions_verified=True,independent_separator_reconstruction=True,native_seal_schema_checked=exists,vision_verified_by_software=False,ordinal_alignment_verified_by_software=False,controls='PASS')
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(validation,sort_keys=True,separators=(',',':'))+'\n');print(json.dumps(validation))
if __name__=='__main__':main()
