"""Reproduce two code mappings and the already-published f56r reading comparison."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
base=ROOT/'transcription/sources/sta'
files=['STA-Eva_def.bit','STA-Eva_Bint.bit','STA-EvaT_def.bit']
output={'status':'EXACT_LOCAL_CONVENTION_ROWS_VERIFIED','tables':{}}
for name in files:
 p=base/name;rows={}
 for number,line in enumerate(p.read_text().splitlines(),1):
  fields=line.split()
  if len(fields)==2 and fields[0] in {'Pd','Pe','Q2'}:
   assert fields[0] not in rows
   rows[fields[0]]={'output':fields[1],'line':number}
 output['tables'][name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rows':rows}
t=output['tables']
assert t[files[0]]['rows']['Pd']['output']=='@167;' and t[files[0]]['rows']['Pe']['output']=='@168;'
assert t[files[1]]['rows']['Pd']['output']=='p' and t[files[1]]['rows']['Pe']['output']=='f'
assert 'Pd' not in t[files[2]]['rows'] and 'Pe' not in t[files[2]]['rows'] and t[files[2]]['rows']['Q2']['output']=='t'
p=ROOT/'experiments/yolo/gdt859_f56r_initial_bar_separator/artifacts/SOURCE_LINES.json'
s=json.loads(p.read_text());first={}
for edition,packet in s['editions'].items():
 assert len(packet['lines'])==1
 line=packet['lines'][0];assert line['metadata']['page']=='f56r' and line['metadata']['locus']=='f56r.1'
 first[edition]=[g[2] for g in line['groups'][:2]]
assert first['ZL3b']==first['RF1b']==['o@167;chal','chchs@168;y']
assert first['IT2a']==['otchal','chchsty']
output['published_raw_first_groups']=first
output['published_packet_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
output['claim_ceiling']='Code-table mappings and raw reading difference only; no intended simplification, physical identity or link definition.'
(Path(__file__).parent/'F56R_ENTITY_CONVENTIONS.json').write_text(json.dumps(output,indent=2)+'\n')
print(output['status'])
