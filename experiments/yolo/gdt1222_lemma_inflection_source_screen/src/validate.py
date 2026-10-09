#!/usr/bin/env python3
"""Separate block parser and index-based punctuation attachment; no runner import."""
from pathlib import Path
from collections import Counter,defaultdict
import json,hashlib,re
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
CP='research_registry/proposals/production_origin_supply_20261003/HAND_WRITER_LEMMA_BUNDLE_CONTRACT_20261006.json'
def compact(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'))
def hashed(x):return hashlib.sha256(compact(x).encode()).hexdigest()
def attributes(s):
 if s=='_':return None
 result={}
 for field in s.split('|'):
  assert '=' in field
  key,_,value=field.partition('=');assert key and value and key not in result
  result[key]=value
 return [[key,result[key]] for key in sorted(result)]
def record(row):
 assert len(row)==10
 if row[3]=='PUNCT':return ['P',row[1]]
 extra=attributes(row[9]);lookup=dict(extra) if extra is not None else {}
 return ['W',row[2],row[3],attributes(row[5]),lookup.get('TraditionalMood'),lookup.get('TraditionalTense'),row[1] if row[2]=='_' else None]
def indexed_groups(aa):
 word_positions=[i for i,a in enumerate(aa) if a[0]=='W']
 if not word_positions:return [aa] if aa else []
 buckets={p:[] for p in word_positions}
 for i,a in enumerate(aa):
  preceding=[p for p in word_positions if p<=i]
  host=preceding[-1] if preceding else word_positions[0]
  buckets[host].append(a)
 return [buckets[p] for p in word_positions]
def main():
 c=json.loads((R/CP).read_text());out=json.loads((A/'RESULT.json').read_text());lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
 for p,h in lock['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 expected={};samples={b:[] for b in c['scope']};ids={b:[] for b in c['scope']};lex={b:set() for b in c['scope']};aforms={b:defaultdict(set) for b in c['scope']};fan={b:defaultdict(set) for b in c['scope']}
 for b in c['scope']:expected[b]=dict(sentences=0,source_tokens=0,lexical_tokens=0,groups=0,unknown_lemma_tokens=0,analysis_stream_sha256=hashlib.sha256(),group_stream_sha256=hashlib.sha256())
 manual={x['id']:x for x in c['manual_observations']};seen={};full_roundtrips=0
 for block in re.split(r'\n\s*\n',(R/c['source']).read_text().strip()):
  lines=block.splitlines();heads=[x for x in lines if x.startswith('# sent_id = ')];assert len(heads)==1
  ident=heads[0].partition(' = ')[2];num=int(re.fullmatch(r'train-s(\d+)',ident).group(1));b=None
  for name,(lo,hi) in c['scope'].items():
   if lo<=num<=hi:b=name
  if b is None and num not in (1,2,4):continue
  rows=[]
  for line in lines:
   if line.startswith('#'):continue
   row=line.split('\t')
   if re.fullmatch('[0-9]+',row[0]):rows.append(row)
  assert [row[0] for row in rows]==[str(i+1) for i in range(len(rows))]
  aa=[record(row) for row in rows]
  for row,a in zip(rows,aa):
   key=ident+':'+row[0]
   if key in manual:
    m=manual[key];assert row[1]==m['form'];assert a==['W',m['lemma'],m['upos'],attributes(m['feats']),m['traditional_mood'],m['traditional_tense'],None];seen[key]=a
  if b is None:continue
  gg=indexed_groups(aa);assert sum(gg,[])==aa;full_roundtrips+=1;v=expected[b];ids[b].append(num)
  v['sentences']+=1;v['source_tokens']+=len(rows);v['groups']+=len(gg)
  v['analysis_stream_sha256'].update((hashed([ident,aa])+'\n').encode());v['group_stream_sha256'].update((hashed([ident,gg])+'\n').encode())
  for row,a in zip(rows,aa):
   if a[0]!='W':continue
   v['lexical_tokens']+=1;v['unknown_lemma_tokens']+=row[2]=='_';lex[b].add((a[1],a[2]));k=compact(a);aforms[b][k].add(row[1]);fan[b][row[1]].add(k)
  for g in gg:
   if len(samples[b])<8000:samples[b].append(g)
 for b,v in expected.items():
  lo,hi=c['scope'][b];assert ids[b]==list(range(lo,hi+1));assert len(samples[b])==8000
  counts=Counter(compact(g) for g in samples[b]);types=len(counts);top=sum(counts[k] for k in sorted(counts,key=lambda k:(-counts[k],k))[:10])
  for k in ('analysis_stream_sha256','group_stream_sha256'):v[k]=v[k].hexdigest()
  v.update(sample_groups=8000,sample_sha256=hashed(samples[b]),types=types,top10_count=top,type_ratio=types/8000,top10_share=top/8000,lemma_upos_types=len(lex[b]),analysis_types=len(aforms[b]),form_types=len(fan[b]),forms_with_multiple_analyses=sum(len(vals)>1 for vals in fan[b].values()),analyses_with_multiple_forms=sum(len(vals)>1 for vals in aforms[b].values()),max_analyses_per_form=max([len(vals) for vals in fan[b].values()] or [0]),max_forms_per_analysis=max([len(vals) for vals in aforms[b].values()] or [0]))
 assert expected==out['books'];assert seen==out['manual_observations'] and set(seen)==set(manual)
 target=json.loads((R/c['screen']['target']).read_text())['targets'];comparisons=[]
 for b,v in expected.items():
  for ed,t in target.items():
   for metric,ref in [('types',t['types']),('top10_count',round(t['top10_share']*8000))]:
    value=v[metric];comparisons.append(dict(book=b,reader=ed,metric=metric,value=value,target=ref,difference=abs(value-ref),within=abs(value-ref)<=400))
 assert comparisons==out['comparisons'];passed=all(x['within'] for x in comparisons);assert passed==out['all_necessary_conditions'];assert out['status']==('LEMMA_INFLECTION_FREQUENCY_COMPATIBLE' if passed else 'LEMMA_INFLECTION_FREQUENCY_FAIL');assert out['all_projected_sentence_roundtrips'] is True and out['original_FORM_roundtrip_claimed'] is False
 # Explicit edge cases for punctuation, unspecified features and lexical fallback.
 w=['W','x','NOUN',None,None,None,None];p=['P','.'];q=['P',','];z=['W','y','NOUN',None,None,None,None]
 fixtures=[([q,w,p,z,p],[[q,w,p],[z,p]]),([p,q],[[p,q]]),([w,z],[[w],[z]])]
 for atoms,groups in fixtures:assert indexed_groups(atoms)==groups
 missing=['1','unread','_','X','_','_','0','root','_','_'];assert record(missing)==['W','_','X',None,None,None,'unread']
 bad=['1','word','word','NOUN','_','Case=Nom|Case=Acc','0','root','_','_']
 try:record(bad)
 except AssertionError:pass
 else:raise AssertionError('duplicate feature accepted')
 v={'status':'PASS','author_independence':'same author, nonimporting implementation','method':'block parser, index-based punctuation host, independent attributes and counts','full_projected_sentence_roundtrips':full_roundtrips,'manual_contrasts':len(seen),'edge_fixtures':5,'source_result_sha256':hashlib.sha256((A/'RESULT.json').read_bytes()).hexdigest(),'all_source_sample_hashes_and_inventories_equal':True,'scientific_decision':out['status'],'meaning_validation':False}
 (A/'VALIDATION.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(v,indent=2))
if __name__=='__main__':main()
