#!/usr/bin/env python3
"""One registered complete historical source image, with a no-retry receipt."""
from pathlib import Path
from PIL import Image
import datetime,hashlib,json,sys,urllib.request
HERE=Path(__file__).resolve().parent
URL='https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f254/full/full/0/native.jpg'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 destination=Path(sys.argv[1]);receipt=HERE/'GD_BNF123V_ACQUISITION_20261002.json'
 if receipt.exists():raise SystemExit('Receipt exists: no retry')
 r={'request_count':1,'url':URL,'request_started_utc':now(),'public_registration_commit':'c7b0527c3329a51fb52fa3269bb3456a60e59613','remote_verified_before_request':True,'source':'BnF Latin6823 f123v / canvasf254','pixels_previously_viewed':False,'scope':'Source only; no Voynich access','budget_note':'Fixed13:37UTC checkpoint; preregistered13:02 start was a rounded estimate. Preparation/publication already completed by13:01:20UTC, so inclusive time begins earlier.'}
 receipt.write_text(json.dumps(r,indent=2)+'\n')
 try:
  with urllib.request.urlopen(URL,timeout=60) as response:
   data=response.read();r.update(status=response.status,final_url=response.url,content_type=response.headers.get('Content-Type'))
  destination.write_bytes(data)
  with Image.open(destination) as im:im.load();r['dimensions']=list(im.size)
  r.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),local_basename=destination.name)
  assert r['status']==200 and r['dimensions']==[3351,4466] and r['final_url']==URL
  r['result']='FULL_REGISTERED_SOURCE_ACQUIRED'
 except Exception as e:r.update(result='MISSING_REGISTERED_SOURCE',error_type=type(e).__name__,error=str(e))
 r['completed_utc']=now();receipt.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
