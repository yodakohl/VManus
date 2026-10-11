"""Check the manually collated historical example and bound source files."""
from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parent;R=B.parents[3]
sources=json.loads((B/'SOURCES.json').read_text());trace=json.loads((B/'TRACE.json').read_text())
for x in sources['images']:
 p=R/x['path'];assert p.stat().st_size==x['bytes'];assert hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
letters=[]
for w in trace['words']:
 assert len(w)>=2 and w.isascii();letters.append(list(w)[1])
assert letters==trace['second_letters'];assert ''.join(letters)==trace['decoded_letter_stream']==trace['expected_normalized_letter_stream']=='cauehuncuirum'
anchors=trace['independent_table_anchors'];assert anchors[0]['word_in_example']==anchors[0]['table_form']=='busarat';assert anchors[1]['word_in_example']=='uimalo' and anchors[1]['table_form']=='vimalo';assert anchors[1]['word_in_example'][1:]==anchors[1]['table_form'][1:]
for name,sha in json.loads((B/'ARTIFACTS.json').read_text()).items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==sha
out={'status':'PASS','author_words':len(letters),'decoded_normalized_letters':''.join(letters),'source_images_verified':len(sources['images']),'table_supported_tight_seam':True,'scope':'Integrity and extraction from disclosed manual collation; not independent palaeography, blind recovery, native fit or restoration of plaintext spacing.'};(B/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
