#!/usr/bin/env python3
"""Fixed complete-source extraction and explicit semantic annotation replay."""
from pathlib import Path
from html.parser import HTMLParser
import argparse,hashlib,json,re,collections
ROOT=Path(__file__).resolve().parents[4]
EXP=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'research_registry/proposals/laufenberg_f85r2_20260926/external_cache/complete_source_roster/galen_gutenberg43383.html'
SOURCE_HASH='d234a983f9c363828a8c71b9b7ae68569548c72cfe2b2691ad5c0409d3609590'
SOURCE_URL='https://www.gutenberg.org/cache/epub/43383/pg43383-images.html'
CHAPTERS=[f'{b}_{i}' for b,n in [('I',17),('II',9),('III',15)] for i in range(1,n+1)]
VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
class Node:
 def __init__(self,tag,attrs=(),parent=None):self.tag,self.attrs,self.parent,self.children=tag,dict(attrs),parent,[]
class Parser(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True);self.root=Node('ROOT');self.stack=[self.root];self.mismatches=[]
 def handle_starttag(self,tag,attrs):
  n=Node(tag,attrs,self.stack[-1]);self.stack[-1].children.append(n)
  if tag not in VOID:self.stack.append(n)
 def handle_startendtag(self,tag,attrs):self.stack[-1].children.append(Node(tag,attrs,self.stack[-1]))
 def handle_endtag(self,tag):
  if tag in VOID:return
  ms=[i for i,n in enumerate(self.stack) if n.tag==tag]
  if not ms:self.mismatches.append(['unmatched_end',tag]);return
  i=ms[-1]
  if i!=len(self.stack)-1:self.mismatches.append(['implicit_close',tag,[n.tag for n in self.stack[i+1:]]])
  self.stack=self.stack[:i]
 def handle_data(self,data):self.stack[-1].children.append(data)
def omitted(n):return bool(set(n.attrs.get('class','').split())&{'footnote','fnanchor','pagenum','pagebreak'}) or n.tag in {'script','style'}
def plain(n):
 if isinstance(n,str):return n
 if omitted(n):return ''
 if n.tag=='br':return ' '
 return ''.join(plain(c) for c in n.children)
def walk(n):
 yield n
 if not isinstance(n,str):
  for c in n.children:yield from walk(c)
def ancestors(n):
 while n:yield n;n=n.parent
def norm(s):return re.sub(r'\s+',' ',s).strip()
def sha(b):return hashlib.sha256(b).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def extract():
 raw=SOURCE.read_bytes();assert sha(raw)==SOURCE_HASH
 ps=Parser();ps.feed(raw.decode('utf-8'));active=False;current=None;seen=[];rows=[];outside=[];empty=[];counts=collections.Counter()
 for n in walk(ps.root):
  if isinstance(n,str):continue
  if n.tag=='h2' and norm(plain(n))=='ΓΑΛΗΝΟΥ':active=False;break
  cid=n.attrs.get('id')
  if cid in CHAPTERS:active=True;current=cid;seen.append(cid)
  if not active or any(omitted(a) for a in ancestors(n)):continue
  if n.tag=='p':
   text=norm(plain(n))
   # One literal editorial note marker lacks the source's usual fnanchor tag.
   # Preserve every substantive bracketed translator addition.
   if current=='I_16' and counts[current]==0:
    assert text.count('Erasistratus[143]')==1
    text=text.replace('Erasistratus[143]','Erasistratus')
   if not text:empty.append({'chapter':current,'attrs':n.attrs});continue
   counts[current]+=1
   rows.append({'paragraph_id':f'{current}.p{counts[current]:03d}','chapter_id':current,'book':current.rsplit('_',1)[0],'text':text,'paragraph_sha256':sha(text.encode()),'words':len(text.split())})
  if n.tag!='p' and not any(a.tag=='p' or re.fullmatch(r'h[1-6]',a.tag) for a in ancestors(n)):
   direct=norm(''.join(c for c in n.children if isinstance(c,str)))
   if direct:outside.append({'tag':n.tag,'chapter':current,'text':direct})
 assert seen==CHAPTERS,seen
 assert all(counts[c]>0 for c in CHAPTERS)
 write(EXP/'runtime/PARAGRAPHS.json',rows)
 for book in ['I','II','III']:
  (EXP/f'runtime/BOOK_{book}.txt').write_text('\n\n'.join(f"[{r['paragraph_id']}] {r['text']}" for r in rows if r['book']==book)+'\n')
 write(EXP/'runtime/EXTRACTION_EXCEPTIONS.json',outside)
 meta={'source_sha256':SOURCE_HASH,'source_url':'https://www.gutenberg.org/cache/epub/43383/pg43383-images.html','chapters':CHAPTERS,'paragraph_count':len(rows),'word_count':sum(r['words'] for r in rows),'per_book':{b:{'paragraphs':sum(r['book']==b for r in rows),'words':sum(r['words'] for r in rows if r['book']==b)} for b in ['I','II','III']},'chapter_paragraph_counts':dict(counts),'parser_mismatches':ps.mismatches,'outside_authorial_text_count':len(outside),'empty_paragraphs':empty,'paragraphs':[{k:v for k,v in r.items() if k!='text'} for r in rows]}
 write(EXP/'artifacts/SOURCE_UNITS.json',meta)
 if outside:raise RuntimeError('Nonparagraph text requires coverage resolution; see runtime exceptions')
 return rows,meta
def aggregate(rows,anns):
 assert set(anns)=={r['paragraph_id'] for r in rows}
 out={}
 for scope in ['ALL','I','II','III']:
  rr=[r for r in rows if scope=='ALL' or r['book']==scope];o={'paragraphs':len(rr),'chapters':len(set(r['chapter_id'] for r in rr)),'concepts':{}}
  for c in ['winter','summer']:
   sets={k:set() for k in ['local_definite','local_possible','scope_definite','scope_possible']}
   for r in rr:
    a=anns[r['paragraph_id']];state=a[c];topic=a[c+'_topic']
    for k,yes in [('local_definite',state in ['E','A']),('local_possible',state in ['E','A','U']),('scope_definite',state in ['E','A'] or topic=='ACTIVE'),('scope_possible',state in ['E','A','U'] or topic in ['ACTIVE','UNCLEAR'])]:
     if yes:sets[k].add(r['paragraph_id'])
   o['concepts'][c]={k:{'paragraphs':len(ids),'chapters':len({r['chapter_id'] for r in rr if r['paragraph_id'] in ids}),'ids':sorted(ids)} for k,ids in sets.items()}
  out[scope]=o
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--extract-only',action='store_true');ap.add_argument('--acquire',action='store_true');args=ap.parse_args()
 if args.acquire and not SOURCE.exists():
  import urllib.request
  with urllib.request.urlopen(SOURCE_URL,timeout=30) as response:raw=response.read()
  assert sha(raw)==SOURCE_HASH,'Remote bytes changed; do not silently replace the fixed edition'
  SOURCE.parent.mkdir(parents=True,exist_ok=True);SOURCE.write_bytes(raw)
 rows,meta=extract()
 if args.extract_only:print(json.dumps({k:v for k,v in meta.items() if k not in ['paragraphs','chapters','chapter_paragraph_counts']},indent=2));return
 anns={};originals=[]
 for p in sorted((EXP/'artifacts').glob('ANNOTATIONS_*.json')):
  block=json.loads(p.read_text());originals.extend(block)
  for a in block:assert a['paragraph_id'] not in anns;anns[a['paragraph_id']]=a.copy()
 byid={r['paragraph_id']:r for r in rows}
 for a in originals:
  r=byid[a['paragraph_id']];assert a['complete_read'] is True and a['paragraph_sha256']==r['paragraph_sha256'] and a['chapter_id']==r['chapter_id']
  for c in ['winter','summer']:assert a[c] in ['E','A','U','N'] and a[c+'_topic'] in ['ACTIVE','NONE','UNCLEAR']
 original=aggregate(rows,anns);corrections=json.loads((EXP/'artifacts/CORRECTIONS.json').read_text())
 for fix in corrections:
  a=anns[fix['paragraph_id']]
  for f,v in fix['before'].items():assert a[f]==v
  a.update(fix['after'])
 result={'status':'COMPLETE_SOURCE_EDITION_PROFILE','source_units':meta['paragraph_count'],'chapters':len(CHAPTERS),'words':meta['word_count'],'paragraph_word_range':[min(r['words'] for r in rows),max(r['words'] for r in rows)],'original':original,'reviewed':aggregate(rows,anns),'correction_count':len(corrections),'manuscript_data_accessed':False,'source_to_target_bound':None,'confirmed_translated_words':0}
 write(EXP/'artifacts/RESULT.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ['original','reviewed']},indent=2))
if __name__=='__main__':main()
