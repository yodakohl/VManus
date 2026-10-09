import collections,gzip,hashlib,json,re
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
TARGET='experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json'
def save(n,x):(B/('artifacts/'+n+'.json')).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sentences(text):
 seen=set();buffer=[]
 for line in text.split('\n')+['']:
  if line.strip():buffer.append(line);continue
  if not buffer:continue
  comments={};tokenrows=[]
  for l in buffer:
   if l.startswith('#'):
    if ' = ' in l:
     k,v=l[1:].split(' = ',1);k=k.strip();assert k not in comments or k not in ['sent_id','text'];comments[k]=v
   else:
    f=l.split('\t');assert len(f)==10;assert re.fullmatch(r'\d+(?:[-.]\d+)?',f[0]);tokenrows.append(f)
  sid=comments['sent_id'];assert sid not in seen;seen.add(sid)
  integers=[int(f[0]) for f in tokenrows if f[0].isdigit()];assert integers==list(range(1,len(integers)+1))
  covered=set();surface=[];raw=[]
  for f in tokenrows:
   ident=f[0]
   if '.' in ident:continue
   if '-' in ident:
    a,z=map(int,ident.split('-'));assert a<z and not(set(range(a,z+1)) & covered);assert all(i in integers for i in range(a,z+1));covered.update(range(a,z+1));surface.append(f)
   else:
    raw.append({'unit':f[1],'row_id':ident})
    if int(ident) not in covered:surface.append(f)
  rebuilt=''.join(f[1]+('' if 'SpaceAfter=No' in f[9].split('|') else ' ') for f in surface).strip()
  actual=comments.get('text',rebuilt);primary=actual.split()
  yield {'sent_id':sid,'source':comments.get('source',''),'text_comment_present':'text' in comments,'text_comment_matches_surface':('text' not in comments or comments['text'].strip()==rebuilt),'primary':primary,'secondary':raw}
  buffer=[]

def fixtures():
 # Range tokens preserve printed form; empty nodes are not printed.
 s='# sent_id = toy1\n# text = A del mar.\n1\tA\t_\tX\t_\t_\t0\troot\t_\t_\n2-3\tdel\t_\t_\t_\t_\t_\t_\t_\t_\n2\tde\t_\tX\t_\t_\t1\tdep\t_\t_\n3\tel\t_\tX\t_\t_\t1\tdep\t_\t_\n3.1\tghost\t_\tX\t_\t_\t_\t_\t1:dep\t_\n4\tmar\t_\tX\t_\t_\t1\tdep\t_\tSpaceAfter=No\n5\t.\t_\tPUNCT\t_\t_\t1\tpunct\t_\t_\n\n'
 d=list(sentences(s))[0];assert d['primary']==['A','del','mar.'] and [r['unit'] for r in d['secondary']]==['A','de','el','mar','.'] and d['text_comment_matches_surface']
 t=s.replace('# sent_id = toy1','# sent_id = toy2').replace('# text = A del mar.\n','');e=list(sentences(t))[0];assert e['primary']==d['primary'] and not e['text_comment_present']
 u=s.replace('# sent_id = toy1','# sent_id = toy3').replace('A del mar.','a  DEL mar !');f=list(sentences(u))[0];assert f['primary']==['a','DEL','mar','!'] and not f['text_comment_matches_surface']
 return {'status':'PASS','fixtures':[{'source':s,'expected':d},{'source':t,'expected':e},{'source':u,'expected':f}]}

def main():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 fx=fixtures();spec=json.loads((B/'src/SOURCE_SPEC.json').read_text());receipt=json.loads((B/'artifacts/SOURCE_RECEIPT.json').read_text());targets=json.loads((R/TARGET).read_text())['targets'];limits={}
 for reader,t in targets.items():
  assert t['tokens']==8000;v=round(t['type_ratio']*8000);top=round(t['top10_share']*8000);limits[reader]={'types':[v-400,v+400],'top10':[top-400,top+400],'native_types':v,'native_top10':top}
 result={};samples={};frequencies={}
 for source in spec['sources']:
  ident=source['corpus_id'];r=next(x for x in receipt['sources'] if x['corpus_id']==ident)
  if r['status']!='SOURCE_HASH_MATCH':result[ident]={'status':'SOURCE_ACQUISITION_STOP'};continue
  raw=gzip.decompress((B/source['local_file']).read_bytes());assert hashlib.sha256(raw).hexdigest()==source['sha256']
  try:
   records=list(sentences(raw.decode('utf-8')))
  except Exception as ex:
   result[ident]={'status':'SOURCE_FORMAT_STOP','error':type(ex).__name__+': '+str(ex)};continue
  sampled={};met={};freq={}
  for projection in ['PRIMARY','FORM_SENSITIVITY']:
   selected=[];sentences_used=[]
   for si,s in enumerate(records):
    units=[{'unit':u,'unit_index':j} for j,u in enumerate(s['primary'])] if projection=='PRIMARY' else [{'unit':r['unit'],'row_id':r['row_id']} for r in s['secondary']]
    remain=8000-len(selected);take=units[:remain]
    if take:
     sentences_used.append({'sentence_index':si,'sent_id':s['sent_id'],'source':s['source'],'units_taken':len(take),'text_comment_present':s['text_comment_present'],'text_comment_matches_surface':s['text_comment_matches_surface']})
     selected.extend({'sentence_index':si,'sent_id':s['sent_id'],**u} for u in take)
    if len(selected)==8000:break
   sampled[projection]={'units':selected,'sentences':sentences_used}
   if len(selected)<8000:met[projection]={'status':'NO_CAPACITY','units':len(selected)};continue
   c=collections.Counter(u['unit'] for u in selected);V=len(c);T=sum(sorted(c.values(),reverse=True)[:10]);tests={}
   for reader,lim in limits.items():
    a=lim['types'][0]<=V<=lim['types'][1];b=lim['top10'][0]<=T<=lim['top10'][1];tests[reader]={'types_within':a,'top10_within':b,'joint':a and b}
   compatible=all(t['joint'] for t in tests.values());met[projection]={'status':'POOLED_BANDS_COMPATIBLE' if compatible else 'OUTSIDE_POOLED_BANDS','units':8000,'types':V,'type_ratio':V/8000,'top10':T,'top10_share':T/8000,'reader_checks':tests,'all_reader_compatible':compatible,'sample_sentences':len(sentences_used),'fallback_sentences':sum(not s['text_comment_present'] for s in sentences_used),'comment_surface_disagreements':sum(not s['text_comment_matches_surface'] for s in sentences_used),'one_character_units':sum(len(x['unit'])==1 for x in selected),'sample_units_sha256':hashlib.sha256(json.dumps([u['unit'] for u in selected],ensure_ascii=False,separators=(',',':')).encode()).hexdigest()}
   freq[projection]=[{'form':w,'count':n} for w,n in sorted(c.items(),key=lambda t:(-t[1],t[0]))]
  samples[ident]=sampled;frequencies[ident]=freq;result[ident]={'status':'SOURCE_SCORED','sentence_count':len(records),'projections':met}
 primarypasses=[k for k,v in result.items() if v['status']=='SOURCE_SCORED' and v['projections']['PRIMARY'].get('all_reader_compatible')]
 stopped=[k for k,v in result.items() if v['status']!='SOURCE_SCORED' or v['projections']['PRIMARY']['status']=='NO_CAPACITY']
 status=('PRIMARY_REFERENCE_COMPATIBILITY_FOUND' if primarypasses else 'NO_PRIMARY_REFERENCE_COMPATIBILITY')+('_WITH_SOURCE_STOPS' if stopped else '')
 save('FIXTURES',fx);save('RESULT',{'status':status,'primary_compatible_sources':primarypasses,'source_stops':stopped,'limits':limits,'sources':result,'ceiling':'Two pooled frequency bands only; not universal stratum criteria, actual writer fit, language or source identification.'});save('FREQUENCIES',frequencies)
 (B/'artifacts/SAMPLES.json.gz').write_bytes(gzip.compress(json.dumps(samples,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
 print(json.dumps({'status':status,'sources':result},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
