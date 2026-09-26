#!/usr/bin/env python3
"""Fetch only two fixed, already-admitted IIIF text-detail rectangles."""
from pathlib import Path
import datetime, hashlib, json, urllib.request
from PIL import Image
B = Path(__file__).resolve().parents[1]
REGIONS = [('N', [1320,770,1030,470], 0), ('W', [790,1170,540,1270], 90)]
def main():
    out=[]
    (B/'runtime').mkdir(exist_ok=True)
    for name,rect,rotation in REGIONS:
        x,y,w,h=rect
        assert x>=0 and y>=0 and x+w<=3000 and y+h<=3890
        url='https://collections.library.yale.edu/iiif/2/1006229/'+','.join(map(str,rect))+'/full/'+str(rotation)+'/default.jpg'
        dest=B/'runtime'/('TEXT_'+name+'.jpg')
        data=dest.read_bytes() if dest.exists() else urllib.request.urlopen(url,timeout=45).read()
        dest.write_bytes(data)
        with Image.open(dest) as im: size=list(im.size)
        out.append(dict(block=name,rect=rect,rotation=rotation,url=url,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),dimensions=size,path='runtime/'+dest.name))
    receipt=B/'artifacts/IMAGE_RECEIPTS.json'
    if receipt.exists():
        assert json.loads(receipt.read_text())['images']==out
    else:
        receipt.write_text(json.dumps(dict(acquired_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),images=out),indent=2)+'\n')
    extra=B/'artifacts/W_COMPLETE_RECEIPT.json'
    if extra.exists():
        for row in json.loads(extra.read_text())['images']:
            assert row['rect']==[730,1030,650,1550] and row['rotation']==90
            assert row['url']=='https://collections.library.yale.edu/iiif/2/1006229/730,1030,650,1550/full/90/default.jpg'
            dest=B/row['path']
            data=dest.read_bytes() if dest.exists() else urllib.request.urlopen(row['url'],timeout=45).read()
            assert hashlib.sha256(data).hexdigest()==row['sha256']
            assert len(data)==row['bytes']
            dest.write_bytes(data)
    print('Fixed in-scope rectangles fetched/hash-checked; no interpretation validation.')
if __name__=='__main__': main()
