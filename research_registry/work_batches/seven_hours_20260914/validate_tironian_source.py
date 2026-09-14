#!/usr/bin/env python3
"""Re-fetch only the documented external sources; no Voynich data access."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin
import hashlib,json,urllib.request
B=Path(__file__).resolve().parent
S=json.loads((B/'TIRONIAN_SOURCE_RESULT.json').read_text())
def fetch(u):
 with urllib.request.urlopen(u,timeout=30) as r:return r.read()
def sha(b):return hashlib.sha256(b).hexdigest()
class Cells(HTMLParser):
 def __init__(self):super().__init__();self.cells=[];self.cell=None
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='td':self.cell={'text':[],'images':[]}
  if t=='img' and self.cell is not None:self.cell['images'].append(urljoin(S['source_page'],a['src']))
 def handle_data(self,d):
  if self.cell is not None and d.strip():self.cell['text'].append(d.strip())
 def handle_endtag(self,t):
  if t=='td' and self.cell is not None:self.cells.append(self.cell);self.cell=None
errors=[]
try:
 raw=fetch(S['source_page']);p=Cells();p.feed(raw.decode('utf-8',errors='replace'))
 if sha(raw)!=S['source_page_sha256']:errors.append('source-page-hash')
 entries=[c for c in p.cells if any(t.startswith('CNT ') for t in c['text'])]
 if len(entries)!=15:errors.append('complete-page-entry-count')
 for x in S['selected_contrasts']:
  matches=[c for c in entries if x['image_url'] in c['images']]
  if len(matches)!=1 or x['expansion'] not in matches[0]['text'] or x['id'].replace('CNT','CNT ') not in matches[0]['text']:errors.append('entry-binding:'+x['id'])
  if sha(fetch(x['image_url']))!=x['sha256']:errors.append('note-image-hash:'+x['id'])
 if sha(fetch(S['geneva']['image_url']))!=S['geneva']['sha256']:errors.append('geneva-image-hash')
except Exception as e:errors.append(type(e).__name__+':source-refetch')
r={'status':'PASS' if not errors else 'FAIL','errors':errors,'coverage':'external15entry page,3exact sign/expansion bindings,4image byte checks','native_shape_interpretation_validated':False,'voynich_data_accessed':False,'meaning_confirmed':False}
(B/'TIRONIAN_VALIDATION.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));raise SystemExit(bool(errors))
