import collections,gzip,hashlib,json,re
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[2]
def parse(text):
 result=[];seen=set()
 for block in re.split(r'\n[ \t]*\n',text.strip('\n')):
  if not block.strip():continue
  lines=block.split('\n');ids=re.findall(r'^# sent_id = (.*)$',block,re.M);assert len(ids)==1 and ids[0] not in seen;sid=ids[0];seen.add(sid)
  texts=re.findall(r'^# text = (.*)$',block,re.M);assert len(texts)<=1
  sources=re.findall(r'^# source = (.*)$',block,re.M)
  rows=[line.split('\t') for line in lines if line and not line.startswith('#')];assert all(len(x)==10 for x in rows)
  assert all(re.fullmatch(r'\d+(?:[-.]\d+)?',x[0]) for x in rows)
  integer=[x for x in rows if x[0].isdigit()];assert [int(x[0]) for x in integer]==list(range(1,len(integer)+1))
  suppressed=set()
  for x in rows:
   if '-' not in x[0]:continue
   a,b=map(int,x[0].split('-'));span=set(range(a,b+1));assert a<b and not(span & suppressed) and span<=set(range(1,len(integer)+1));suppressed|=span
  printed=[x for x in rows if '-' in x[0] or (x[0].isdigit() and int(x[0]) not in suppressed)]
  pieces=[]
  for x in printed:
   pieces.append(x[1])
   if 'SpaceAfter=No' not in x[9].split('|'):pieces.append(' ')
  reconstructed=''.join(pieces).strip();primary=(texts[0] if texts else reconstructed).split()
  result.append({'sent_id':sid,'source':sources[-1] if sources else '', 'text_comment_present':bool(texts),'text_comment_matches_surface':not texts or texts[0].strip()==reconstructed,'primary':primary,'secondary':[{'unit':x[1],'row_id':x[0]} for x in integer]})
 return result

def main():
 lock=json.loads((P/'src/REGISTRATION_LOCK.json').read_text())
 for path,h in lock['hashes'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==h
 spec=json.loads((P/'src/SOURCE_SPEC.json').read_text());acq=json.loads((P/'artifacts/SOURCE_RECEIPT.json').read_text());result=json.loads((P/'artifacts/RESULT.json').read_text());samples=json.loads(gzip.decompress((P/'artifacts/SAMPLES.json.gz').read_bytes()));frequencies=json.loads((P/'artifacts/FREQUENCIES.json').read_text());target=json.loads((R/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json').read_text())['targets']
 limits={r:{'types':[round(v['type_ratio']*8000)-400,round(v['type_ratio']*8000)+400],'top10':[round(v['top10_share']*8000)-400,round(v['top10_share']*8000)+400],'native_types':round(v['type_ratio']*8000),'native_top10':round(v['top10_share']*8000)} for r,v in target.items()};assert limits==result['limits'] and all(v['tokens']==8000 for v in target.values())
 verified=0;primarypasses=[];stops=[]
 for source in spec['sources']:
  cid=source['corpus_id'];r=result['sources'][cid];rec=next(x for x in acq['sources'] if x['corpus_id']==cid)
  if rec['status']!='SOURCE_HASH_MATCH':assert r['status']=='SOURCE_ACQUISITION_STOP';stops.append(cid);continue
  compressed=(P/source['local_file']).read_bytes();raw=gzip.decompress(compressed);assert hashlib.sha256(raw).hexdigest()==source['sha256']==rec['raw_sha256'];assert len(raw)==source['bytes'];assert hashlib.sha256(compressed).hexdigest()==rec['compressed_sha256']
  try:records=parse(raw.decode('utf-8'))
  except Exception:
   assert r['status']=='SOURCE_FORMAT_STOP';stops.append(cid);continue
  assert r['status']=='SOURCE_SCORED' and r['sentence_count']==len(records)
  for projection in ['PRIMARY','FORM_SENSITIVITY']:
   events=[];used=[]
   for i,s in enumerate(records):
    values=[{'unit':u,'unit_index':j} for j,u in enumerate(s['primary'])] if projection=='PRIMARY' else s['secondary']
    count=0
    for v in values:
     if len(events)>=8000:break
     events.append({'sentence_index':i,'sent_id':s['sent_id'],**v});count+=1
    if count:used.append({'sentence_index':i,'sent_id':s['sent_id'],'source':s['source'],'units_taken':count,'text_comment_present':s['text_comment_present'],'text_comment_matches_surface':s['text_comment_matches_surface']})
    if len(events)==8000:break
   assert samples[cid][projection]=={'units':events,'sentences':used};m=r['projections'][projection]
   if len(events)<8000:
    assert m=={'status':'NO_CAPACITY','units':len(events)}
    if projection=='PRIMARY':stops.append(cid)
    continue
   counts={}
   for e in events:counts[e['unit']]=counts.get(e['unit'],0)+1
   V=len(set(e['unit'] for e in events));T=sum(sorted(counts.values(),reverse=True)[:10]);expectedfreq=[{'form':w,'count':n} for w,n in sorted(counts.items(),key=lambda x:(-x[1],x[0]))];assert frequencies[cid][projection]==expectedfreq
   assert m['types']==V and m['top10']==T and m['type_ratio']==V/8000 and m['top10_share']==T/8000 and m['units']==8000
   checks={ed:{'types_within':lim['types'][0]<=V<=lim['types'][1],'top10_within':lim['top10'][0]<=T<=lim['top10'][1],'joint':lim['types'][0]<=V<=lim['types'][1] and lim['top10'][0]<=T<=lim['top10'][1]} for ed,lim in limits.items()};assert checks==m['reader_checks']
   ok=all(x['joint'] for x in checks.values());assert m['all_reader_compatible']==ok and m['status']==('POOLED_BANDS_COMPATIBLE' if ok else 'OUTSIDE_POOLED_BANDS')
   assert m['sample_sentences']==len(used) and m['fallback_sentences']==sum(not s['text_comment_present'] for s in used) and m['comment_surface_disagreements']==sum(not s['text_comment_matches_surface'] for s in used)
   assert m['one_character_units']==sum(len(e['unit'])==1 for e in events)
   assert m['sample_units_sha256']==hashlib.sha256(json.dumps([e['unit'] for e in events],ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
   if projection=='PRIMARY' and ok:primarypasses.append(cid)
   verified+=len(events)
 assert result['primary_compatible_sources']==primarypasses and result['source_stops']==stops
 status=('PRIMARY_REFERENCE_COMPATIBILITY_FOUND' if primarypasses else 'NO_PRIMARY_REFERENCE_COMPATIBILITY')+('_WITH_SOURCE_STOPS' if stops else '');assert result['status']==status
 for f in json.loads((P/'artifacts/FIXTURES.json').read_text())['fixtures']:assert parse(f['source'])==[f['expected']]
 out={'status':'PASS','source_files':len(spec['sources']),'sample_units_independently_reconstructed':verified,'source_stops':stops,'scope':'Separate CoNLL-U/text parsing, exact samples/counts/source hashes and all fixed decisions; no source-language or native meaning confirmation.'}
 (P/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
