#!/usr/bin/env python3
"""One registered native request; immutable receipt prevents retry."""
from pathlib import Path
import datetime,hashlib,json,math,urllib.request,urllib.error,subprocess
from PIL import Image
P=Path(__file__).resolve().parents[1]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 s=json.loads((P/'src/SOURCE.json').read_text());a=P/'artifacts';receipt=a/'ACQUISITION.json'
 if receipt.exists():raise SystemExit('Receipt exists; no repeated request permitted')
 r={'request_count':1,'request_url':s['url'],'request_started_utc':now(),'public_registration_commit':'46630bdcaebf7dcc853fb9f8e78afc5fb07819dc','public_main_verified_before_request':True,'canvas':s['canvas'],'folio':s['folio'],'sealed_opened':False,'independent_confirmation_capacity':0}
 receipt.write_text(json.dumps(r,indent=2)+'\n')
 try:
  with urllib.request.urlopen(s['url'],timeout=60) as response:
   data=response.read();r.update(http_status=response.status,final_url=response.url,content_type=response.headers.get('Content-Type'))
  r['response_completed_utc']=now();out=a/'native.jpg';out.write_bytes(data)
  im=Image.open(out);im.load();r.update(bytes=len(data),sha256=sha(out),dimensions=list(im.size),image_path='artifacts/native.jpg')
  assert r['http_status']==200 and list(im.size)==s['expected_dimensions']
  assert '/1006123/' in r['final_url']
  w,h=im.size;box=[math.floor(.65*w),math.floor(.68*h),w,h];crop=a/'contact_crop.png';im.crop(box).save(crop)
  r['crop']={'path':'artifacts/contact_crop.png','sha256':sha(crop),'parent_sha256':sha(out),'bounds':box,'dimensions':[w-box[0],h-box[1]],'resampled':False,'mode':im.mode}
  r['outcome']='NATIVE_INPUT_ACQUIRED'
 except Exception as e:
  r.update(outcome='MISSING_REGISTERED_NATIVE_INPUT',error_type=type(e).__name__,error=str(e),response_completed_utc=now())
 receipt.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
