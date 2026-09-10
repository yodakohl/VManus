#!/usr/bin/env python3
"""Losslessly package the complete search receipts after the frozen fitter ends."""
import argparse,gzip,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1]
def digest(b):return hashlib.sha256(b).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
    raw=E/'artifacts/CANDIDATES.json';packed=raw.with_suffix('.json.gz');receipt=E/'artifacts/PACKING.json'
    if a.check or not raw.exists():
        r=json.loads(receipt.read_text());data=packed.read_bytes();plain=gzip.decompress(data)
        assert digest(data)==r['compressed_sha256'] and digest(plain)==r['logical_sha256']
        assert len(data)==r['compressed_bytes'] and len(plain)==r['logical_bytes']
        if raw.exists():assert raw.read_bytes()==plain
    else:
        plain=raw.read_bytes();data=gzip.compress(plain,mtime=0);packed.write_bytes(data)
        assert gzip.decompress(packed.read_bytes())==plain
        r=dict(logical_path='artifacts/CANDIDATES.json',published_path='artifacts/CANDIDATES.json.gz',logical_sha256=digest(plain),compressed_sha256=digest(data),logical_bytes=len(plain),compressed_bytes=len(data),lossless=True)
        receipt.write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
        raw.unlink() # Only this experiment's generated duplicate, verified above.
    print(json.dumps(r,sort_keys=True))
if __name__=='__main__':main()
