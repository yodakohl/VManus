#!/usr/bin/env python3
"""Necessary fixed-vocabulary letter-pattern capacity under e/i allography."""
import argparse,collections,gzip,hashlib,itertools,json,re
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(name,x):
 p=B/'artifacts'/name;b=(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode();p.write_bytes(gzip.compress(b,mtime=0) if p.suffix=='.gz' else b)
def pattern(u):
 d={};p=[]
 for a in u:
  if a not in d:d[a]=len(d)
  p.append(d[a])
 return tuple(p)
def pkey(p):return '.'.join(map(str,p))
def collapse(u):return [x for k,x in enumerate(u) if not(k and x in ('e','i') and u[k-1]==x)]
def parse(s,signs):
 rx=re.compile('|'.join(re.escape(x) for x in sorted(signs,key=lambda t:(-len(t),t))));u=rx.findall(s);return u if s and ''.join(u)==s else None
def physical(page):
 m=re.match(r'^f\d+',page);assert m;return m.group()
def classify(p,env,lengths):return 'SUPPORTED' if pkey(p) in env else 'LENGTH_UNSUPPORTED' if len(p) not in lengths else 'PATTERN_UNSUPPORTED'
def sources(spec):
 recipe=read(R/spec['recipe_path']);deot=read(R/spec['deot_path']);other=read(R/spec['other_path']);out={}
 for n in spec['source_names']:
  if n in ('b4','w1','bs1','gr1'):words=[w for rec in recipe[n] for w in rec['words']]
  elif n=='deot':words=[w for sec in deot['source_sections'] for w in sec['words']]
  else:words=[r['unit'] for r in other[n]['PRIMARY']['units']];assert len(words)==8000
  assert all(isinstance(w,str) and w for w in words);W=sorted(set(words));modes={'FWD':{},'BIDIR':{}}
  for w in W:
   for direction,s in [('FWD',w),('REV',w[::-1])]:
    k=pkey(pattern(s));v={'word':w,'direction':direction,'pattern':list(pattern(s))}
    modes['BIDIR'].setdefault(k,v)
    if direction=='FWD':modes['FWD'].setdefault(k,v)
  out[n]={'tokens':len(words),'word_types':len(W),'wordbook_sha256':hashlib.sha256('\n'.join(W).encode()).hexdigest(),'source_alphabet_size':len(set(''.join(W))),'modes':modes}
 return out

def controls():
 checks=0
 for n in range(6):
  for u in itertools.product(['e','i','a'],repeat=n):
   c=collapse(u);assert collapse(c)==c
   runs=[next(g) for _,g in itertools.groupby(u)];expected=[]
   for x,g in itertools.groupby(u):expected.extend([x] if x in ('e','i') else list(g))
   assert c==expected and c==list(reversed(collapse(tuple(reversed(u)))))
   assert all(c[j]!=c[j-1] or c[j] not in ('e','i') for j in range(1,len(c)));checks+=1
 words=[u for n in range(5) for u in itertools.product('ab',repeat=n)]
 for a in words:
  for b in words:
   if len(a)!=len(b):continue
   equivalent=any(tuple(dict(zip('ab',p))[x] for x in a)==b for p in itertools.permutations('ab'))
   assert (pattern(a)==pattern(b))==equivalent;checks+=1
 assert collapse(['ch','e','e','ckh','i','i','n','n'])==['ch','e','ckh','i','n','n']
 assert pattern('Aa')!=(0,0) and pattern('áa')!=(0,0)
 assert parse('cheeiin',['ch','e','i','n'])==['ch','e','e','i','i','n'];assert parse('c',['ch','e','i','n']) is None
 return {'status':'PASS_SOURCE_FREE_CONTROLS','checks':checks,'idempotent_collapse':True,'reversal_commutes':True,'pattern_bijection_equivalence':True,'source_codepoints_not_normalized':True,'empirical_inputs_read':False}

def summary(rows,src,mode):
 bad=[x for x in rows if x['support'][src][mode]!='SUPPORTED'];leaves=sorted({l for x in bad for l in x['leaves']})
 return {'types':len(rows),'occurrences':sum(x['count'] for x in rows),'unsupported_types':len(bad),'unsupported_occurrences':sum(x['count'] for x in bad),'unsupported_physical_leaves':leaves,'length_failure_types':sum(x['support'][src][mode]=='LENGTH_UNSUPPORTED' for x in bad),'pattern_failure_types':sum(x['support'][src][mode]=='PATTERN_UNSUPPORTED' for x in bad),'unsupported_changed_types':sum(x['changed'] for x in bad),'unsupported_unchanged_types':sum(not x['changed'] for x in bad),'status':'EMPTY_PANEL' if not rows else 'EXCLUDED' if bad else 'WORDWISE_SUPPORTED_ONLY'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');args=ap.parse_args()
 if args.controls:print(json.dumps(controls()));return
 lock=read(B/'LOCK.json')
 for p,h in lock['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 spec=read(B/'src/SPEC.json');env=sources(spec);lengths={n:{m:{len(x['pattern']) for x in src['modes'][m].values()} for m in spec['modes']} for n,src in env.items()}
 def allsupport(p):return {n:{m:classify(p,src['modes'][m],lengths[n][m]) for m in spec['modes']} for n,src in env.items()}
 cache=read(R/spec['native_path']);native={};result={'sources':{n:{k:v for k,v in s.items() if k!='modes'}|{'modes':{m:{'patterns':len(s['modes'][m]),'lengths':sorted(lengths[n][m])} for m in spec['modes']}} for n,s in env.items()},'readers':{},'claim_ceiling':spec['claim_ceiling']}
 for ed in spec['readers']:
  by=collections.defaultdict(list)
  for row in cache[ed]:
   assert row['edition']==ed and row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
   assert not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v')
   assert parse(row['ivtff_group_raw'],spec['signs'])==row['units'];by[row['ivtff_group_raw']].append(row)
  rows=[]
  for form,occ in sorted(by.items()):
   u=occ[0]['units'];assert all(x['units']==u for x in occ);c=collapse(u);p=pattern(c);pages=sorted({x['page'] for x in occ});leaves=sorted({physical(x) for x in pages})
   rows.append({'form':form,'units':u,'collapsed_units':c,'changed':u!=c,'pattern':list(p),'pattern_key':pkey(p),'count':len(occ),'ids':sorted(x['id'] for x in occ),'pages':pages,'leaves':leaves,'support':allsupport(p)})
  native[ed]=rows;sr={}
  for n in spec['source_names']:
   sr[n]={m:{'FULL':summary(rows,n,m),'LEAF2':summary([x for x in rows if len(x['leaves'])>=2],n,m)} for m in spec['modes']}
   sr[n]['first_failures']={m:[{'form':x['form'],'count':x['count'],'leaves':x['leaves'],'changed':x['changed'],'status':x['support'][n][m],'first_id':x['ids'][0]} for x in sorted([x for x in rows if x['support'][n][m]!='SUPPORTED'],key=lambda x:(-x['count'],x['form']))[:10]] for m in spec['modes']}
  result['readers'][ed]={'strict_groups':len(cache[ed]),'raw_types':len(rows),'changed_raw_types':sum(x['changed'] for x in rows),'source_results':sr}
 ws=read(R/spec['worksheet_path']);us=[u for u in ws['units'] if u['unit_id']==spec['passage_unit']];assert len(us)==1;groups=[]
 for line in us[0]['lines']:
  meta=line['metadata'];assert meta['page']=='f75v' and meta['edition']=='IT2a';assert line['diplomatic_forms']==[g[2] for g in line['original_groups']]
  for g in line['original_groups']:
   raw=g[2];u=parse(raw,spec['signs']);c=collapse(u) if u is not None else None;p=pattern(c) if c is not None else None
   groups.append({'original':g,'page':meta['page'],'locus':meta['locus'],'units':u,'collapsed_units':c,'pattern':list(p) if p is not None else None,'support':allsupport(p) if p is not None else {n:{m:'UNPARSEABLE' for m in spec['modes']} for n in spec['source_names']}})
 assert len(groups)==spec['expected_passage_groups'];unparseable=[g['original'][0] for g in groups if g['units'] is None]
 passage={'unit_id':spec['passage_unit'],'original_groups':len(groups),'unparseable_ids':unparseable,'groups':groups,'sources':{}}
 for n in spec['source_names']:
  passage['sources'][n]={}
  for m in spec['modes']:
   missing=[g['original'][0] for g in groups if g['support'][n][m] not in ('SUPPORTED','UNPARSEABLE')]
   passage['sources'][n][m]={'status':'UNSCORABLE' if unparseable else 'WHOLE_PASSAGE_EXCLUDED' if missing else 'WORDWISE_SUPPORTED_ONLY','unsupported_groups':len(missing),'unsupported_ids':missing}
 result['passage']=passage;result['source_decisions']={n:{'all_readers_FULL_excluded':all(result['readers'][ed]['source_results'][n]['BIDIR']['FULL']['status']=='EXCLUDED' for ed in spec['readers']),'all_readers_LEAF2_excluded':all(result['readers'][ed]['source_results'][n]['BIDIR']['LEAF2']['status']=='EXCLUDED' for ed in spec['readers'])} for n in spec['source_names']}
 result['status']='ALL_EIGHT_FIXED_WORD_ENVELOPES_EXCLUDED' if all(v['all_readers_FULL_excluded'] for v in result['source_decisions'].values()) else 'MIXED_FIXED_WORD_ENVELOPES'
 save('SOURCE_ENVELOPES.json.gz',{'sources':env});save('NATIVE_SUPPORT.json.gz',{'readers':native});save('RESULT.json',result)
 print(json.dumps({'status':result['status'],'BIDIR':{n:{ed:{panel:result['readers'][ed]['source_results'][n]['BIDIR'][panel]['unsupported_types'] for panel in ['FULL','LEAF2']} for ed in spec['readers']} for n in spec['source_names']},'passage':{n:v['BIDIR'] for n,v in passage['sources'].items()}},indent=2))
if __name__=='__main__':main()
