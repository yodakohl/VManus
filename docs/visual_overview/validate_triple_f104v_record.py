"""Check original metadata and saved observations, not paleographic truth."""
import hashlib,json,subprocess,sys
from pathlib import Path
base=Path(__file__).resolve().parent
stem='TRIPLE_F104V_2026-09-06'
subprocess.run([sys.executable,str(base/'validate_orientation_sources.py'),stem+'_SOURCES.json'],check=True)
seal=json.loads((base/(stem+'_A_SEAL.json')).read_text())
a=base/(stem+'_A.md')
assert seal['path']=='docs/visual_overview/'+a.name
assert hashlib.sha256(a.read_bytes()).hexdigest()==seal['sha256']
notes={}
for role in ['A','B']:
    p=base/(stem+'_'+role+'.md');assert p.stat().st_size>0
    notes[role]=hashlib.sha256(p.read_bytes()).hexdigest()
r={'status':'SOURCE_METADATA_AND_NOTE_SEAL_PASS','native_judgments_validated':False,'notes_sha256':notes}
(base/(stem+'_VALIDATION.json')).write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
