"""Source extraction/receipt validation only. No Voynich target input."""
from pathlib import Path
import json,hashlib,urllib.request,xml.etree.ElementTree as ET
P=Path(__file__).resolve().parent
D=json.loads((P/'CYRANIDES_SOURCE_RESULT.json').read_text())
b=urllib.request.urlopen(D['source']['url'],timeout=45).read()
assert len(b)==D['source']['bytes']
assert hashlib.sha256(b).hexdigest()==D['source']['sha256']
r=ET.fromstring(b);ns={'t':'http://www.tei-c.org/ns/1.0'}
book=r.find('.//t:div[@subtype="book"][@n="1"]',ns)
rosters=[];sections=0;selected=[]
for c in book.findall('t:div',ns):
 n=int(c.attrib['n'])
 if n==0:continue
 ss=c.findall('t:div',ns);sections+=len(ss)
 text=lambda s:' '.join(''.join(s.itertext()).split())
 rosters.append({'chapter':n,'opening':text(ss[0])})
 for s in ss:
  if n>=7 and any(x in text(s) for x in D['instruction_selector_strings']):selected.append(f'1.{n}.{s.attrib["n"]}')
assert len(rosters)==24 and sections==353
assert rosters==D['rosters']
assert selected==D['keyword_selected_sections_chapters7_24']
print(json.dumps({'status':'PASS_SOURCE_ONLY','source_bytes':len(b),'rosters':len(rosters),'sections':sections,'selected_sections':len(selected),'target_access':False}))
