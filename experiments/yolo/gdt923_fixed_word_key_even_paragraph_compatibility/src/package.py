#!/usr/bin/env python3
"""Losslessly compress the complete witness table; preserve its raw-byte hash."""
import gzip,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parent.parent; A=E/'artifacts';p=A/'WITNESSES.json';q=A/'WITNESSES.json.gz'
if p.exists():
 raw=p.read_bytes();q.write_bytes(gzip.compress(raw,mtime=0));assert gzip.decompress(q.read_bytes())==raw
 (A/'PACKAGING.json').write_text(json.dumps(dict(raw_witness_sha256=hashlib.sha256(raw).hexdigest(),raw_bytes=len(raw),gzip_sha256=hashlib.sha256(q.read_bytes()).hexdigest(),gzip_bytes=q.stat().st_size,policy='Lossless packaging only; no rows removed, grouped or selected.'),indent=2)+'\n');p.unlink()
else:
 assert q.exists();m=json.loads((A/'PACKAGING.json').read_text());assert hashlib.sha256(gzip.decompress(q.read_bytes())).hexdigest()==m['raw_witness_sha256']
print('Lossless witness packaging PASS')
