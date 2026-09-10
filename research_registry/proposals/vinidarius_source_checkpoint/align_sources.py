import json,html,re,collections,hashlib
from pathlib import Path
import argparse
parser=argparse.ArgumentParser(description='Align frozen A/M annotations by original source character offsets; no semantic adjudication.')
parser.add_argument('source_directory',type=Path)
args=parser.parse_args()
D=Path(__file__).resolve().parent
SOURCE=args.source_directory
a=json.loads((D/'SOURCE_TYPED_A.json').read_text());m=json.loads((D/'SOURCE_TYPED_M.json').read_text())
sources={n:(SOURCE/(n+'.html')).read_bytes().decode() for n in ['pantry','recipes']}
def coordinate_map(raw,base):
 text=[]; mapping=[];pos=0
 for z in re.finditer(r'&(?:#[0-9]+|#x[0-9a-fA-F]+|[a-zA-Z][a-zA-Z0-9]+);',raw):
  for i in range(pos,z.start()):text.append(raw[i]);mapping.append((base+i,base+i+1))
  decoded=html.unescape(z.group());text.extend(decoded);mapping.extend([(base+z.start(),base+z.end())]*len(decoded));pos=z.end()
 for i in range(pos,len(raw)):text.append(raw[i]);mapping.append((base+i,base+i+1))
 return ''.join(text),mapping
A={};M={}
def put(dest,document,span,entry,record):
 key=(document,*span);assert key not in dest
 dest[key]={'record':record,'surface':entry['surface'],'category':entry.get('category','OMITTED'),'lemma':entry.get('lemma'),'status':entry.get('status'),'reason':entry.get('reason'),'alternatives':entry.get('category_alternatives',entry.get('possible_categories',[]))}
for r in a['records']+[{'id':'PANTRY_POSTLUDE','source':'pantry','segments':[a['common_pantry_closing']]}]:
 for s in r['segments']:
  raw=s['raw'];base,end=s['html_span'];assert sources[r['source']][base:end]==raw
  decoded,mp=coordinate_map(raw,base);assert decoded==s['text']
  for q in s['mentions']+s['omitted_tokens']:
   x,y=q['span'];assert decoded[x:y]==q['surface'];put(A,r['source'],(mp[x][0],mp[y-1][1]),q,r['id'])
for r in m['records']+[m['pantry_postlude']]:
 for s in r['source_segments']:
  base,end=s['html_character_span'];raw=s['source_html'];doc=s['document'];assert sources[doc][base:end]==raw
  decoded,mp=coordinate_map(raw,base);assert decoded==s['text'];tx,ty=s['record_text_span']
  for q in r['mentions']+r['omitted_tokens']+r['unresolved_tokens']:
   x,y=q['span']
   if not(tx<=x and y<=ty):continue
   assert decoded[x-tx:y-tx]==q['surface'];put(M,doc,(mp[x-tx][0],mp[y-tx-1][1]),q,r['id'])
renames={'PART':'EXPLICIT_PART','STATE':'EXPLICIT_STATE'}
rows=[];agree=[]
for k in sorted(A.keys()|M.keys()):
 l=A.get(k);r=M.get(k)
 if l and r:assert l['surface']==r['surface']
 la=(renames.get(l['category'],l['category']),l['lemma']) if l else None
 ra=(r['category'],r['lemma']) if r else None
 if la==ra:agree.append(k)
 else:rows.append({'source':k[0],'source_span':list(k[1:]),'a':l,'m':r})
x={'status':'SOURCE_ANNOTATION_DISAGREEMENTS_NOT_ADJUDICATED','source_hashes':{n:hashlib.sha256((SOURCE/(n+'.html')).read_bytes()).hexdigest() for n in sources},'A_sha256':hashlib.sha256((D/'SOURCE_TYPED_A.json').read_bytes()).hexdigest(),'M_sha256':hashlib.sha256((D/'SOURCE_TYPED_M.json').read_bytes()).hexdigest(),'A_tokens':len(A),'M_tokens':len(M),'identical_category_lemma':len(agree),'differing':len(rows),'category_pairs':dict(collections.Counter(str((q['a']['category'] if q['a'] else None,q['m']['category'] if q['m'] else None)) for q in rows)),'rows':rows}
print(json.dumps(x,ensure_ascii=False,indent=2))
