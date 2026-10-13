"""Retrieve only public MIT software, never bundled data or editions."""
from pathlib import Path
import hashlib,json,urllib.request
ROOT=Path(__file__).resolve().parents[4]
DEST=ROOT/'.cache/rasm_arch_source_20261013'
PIN='32646fe6e76f581128bb4ac465b4c606ac88cd13'
HASHES={'rasm_arch/__init__.py':'29d23d75612198ff1206aaba0105c61c5d72aa61848a840764e9a3936343c623','rasm_arch/rasm_arch.py':'dcbeeb69253c6a467276c267e3f26871cc427f5e9c1698ae573bf876a6c416cd','rasm_arch/util.py':'befeced908b7e7d9fb3c9a6c5add3dd5b72aecf48ddf9fd5facdf2c042f177a0','LICENSE':'fb92312fd87a1dee0919efd837278e528aecf366cc4e09ff64c53c9d104bc9ae'}
def main():
 for rel,h in HASHES.items():
  p=DEST/rel
  if not p.exists():
   b=urllib.request.urlopen('https://raw.githubusercontent.com/kabikaj/rasm_arch/'+PIN+'/'+rel).read();assert hashlib.sha256(b).hexdigest()==h
   p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
  assert hashlib.sha256(p.read_bytes()).hexdigest()==h
 print(json.dumps({'status':'PINNED_CODE_ONLY_READY','files':list(HASHES),'pin':PIN,'excluded':'All rasm_arch_data and all edition/corpus resources'}))
if __name__=='__main__':main()
