"""Validate text identity, prospective scope and image receipts, not perception."""
import argparse,hashlib,json
from datetime import datetime
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):return json.loads(p.read_text())
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--image-dir');args=parser.parse_args()
 lock=read(B/'src/REGISTRATION_LOCK.json')
 for p,h in lock['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 packet=read(B/'artifacts/TEXT_PACKET.json');obs=read(B/'artifacts/NATIVE_OBSERVATION.json');result=read(B/'artifacts/RESULT.json');full=read(B/'artifacts/FULL_IMAGE_RECEIPT.json');plan=read(B/'artifacts/CROP_PLAN.json');crops=read(B/'artifacts/CROP_RECEIPTS.json');canvas=read(B/'artifacts/CANVAS_METADATA.json')
 expected=[];n=0
 for reader in ['ZL3b','IT2a','RF1b']:
  source={}
  for phase in ['DISCOVERY','EVALUATION']:
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{reader}.json')['lines']:
    if line['metadata']['locus'] in ['f102v2.21','f102v2.33']:source[line['metadata']['locus']]=line
  assert len(source)==2
  for line in packet[reader]:
   loc=line['metadata']['locus'];assert line==source[loc];assert line['metadata']['page']=='f102v2' and line['metadata']['kind']=='P';n+=1
   form='oeees' if loc.endswith('.21') else 'aiiin';groups=[g for g in line['groups'] if g[2]==form];assert len(groups)==1;g=groups[0]
   left='UNCERTAIN_SMALL_SPACE' if reader=='ZL3b' and loc.endswith('.33') else 'DEFINITE_SPACE';assert g[3]==left and g[4]=='DEFINITE_SPACE'
   expected.append({'reader':reader,'locus':loc,'group_id':g[0],'raw':form,'left_separator':g[3],'right_separator':g[4]})
 assert expected==result['targets'] and n==result['source_lines']==6
 assert result['native_observation_sha256']==hashlib.sha256((B/'artifacts/NATIVE_OBSERVATION.json').read_bytes()).hexdigest();assert result['status']==obs['status']=='BODY_CONTRAST_SUPPORTED_LEFT_BOUNDARY_UNRESOLVED';assert result['manual_judgment_recomputed'] is False
 assert canvas['canvas_id'].endswith('/1006252') and (canvas['width'],canvas['height'])==(2981,3795)
 assert full['url']==canvas['url'] and (full['width'],full['height'])==(2981,3795)
 assert datetime.fromisoformat(lock['created_utc'])<datetime.fromisoformat(full['requested_utc'])<datetime.fromisoformat(full['acquired_utc'])<datetime.fromisoformat(plan['registered_utc'])
 assert len(plan['boxes'])==len(crops)==2
 for p,c in zip(plan['boxes'],crops):
  assert p['id']==c['id'] and p['locus']==c['locus'] and p['xywh']==c['xywh'];x,y,w,h=p['xywh'];assert x>=0 and y>=0 and x+w<=full['width'] and y+h<=full['height'];assert (c['width'],c['height'])==(w,h)
  assert c['url']==f"https://collections.library.yale.edu/iiif/2/1006252/{x},{y},{w},{h}/full/0/default.jpg"
  assert datetime.fromisoformat(plan['registered_utc'])<datetime.fromisoformat(c['requested_utc'])<datetime.fromisoformat(c['acquired_utc'])<datetime.fromisoformat(obs['recorded_utc'])
 assert obs['source_localization']['other_canvas_opened'] is False
 assert obs['targets'][1]['left_gap']=='UNRESOLVED' and obs['targets'][1]['three_body_count']=='UNRESOLVED_EXACT_RUN_TERMINAL_CUT'
 count=0
 if args.image_dir:
  from PIL import Image
  for receipt in [full]+crops:
   p=Path(args.image_dir)/receipt['local_basename'];assert hashlib.sha256(p.read_bytes()).hexdigest()==receipt['sha256'];assert Image.open(p).size==(receipt['width'],receipt['height']);count+=1
 out={'status':'PASS','full_source_lines':n,'target_groups':len(expected),'prospective_image_receipts':3,'local_image_bytes_checked':count,'manual_shape_judgment_validated':False,'ceiling':'Provenance, chronology, source identity and file integrity only. The frozen informed visual observation is not automatically verified.'}
 name='VALIDATION_IMAGES.json' if args.image_dir else 'VALIDATION.json';(B/'artifacts'/name).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
