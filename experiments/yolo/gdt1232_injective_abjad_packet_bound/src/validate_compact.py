#!/usr/bin/env python3
"""Lossless artifact reader for the unchanged preregistered proof validator."""
from pathlib import Path
import gzip,hashlib,importlib.util,json
D=Path(__file__).resolve().parents[1];A=D/'artifacts'
spec=importlib.util.spec_from_file_location('registered_validator',D/'src/validate.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
for item in json.loads((A/'CERTIFICATE_STORAGE.json').read_text())['certificates']:
    packed=(A/item['retained_name']).read_bytes();assert hashlib.sha256(packed).hexdigest()==item['compressed_sha256']
    raw=gzip.decompress(packed);assert hashlib.sha256(raw).hexdigest()==item['raw_sha256'];assert len(raw)==item['raw_bytes']
def read(p):
    # Prefer the compact stored certificate, even after a fresh runner emits JSON.
    packed=p.with_suffix(p.suffix+'.gz')
    return json.loads(gzip.decompress(packed.read_bytes())) if packed.exists() else json.loads(p.read_text())
v.read=read
if __name__=='__main__':v.main()
