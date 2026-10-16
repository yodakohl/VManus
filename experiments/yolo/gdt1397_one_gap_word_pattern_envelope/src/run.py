#!/usr/bin/env python3
"""Generous fixed-source wordwise one-gap pattern envelope; no meanings."""
import argparse,collections,gzip,hashlib,itertools,json,re
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 data=p.read_bytes();return json.loads(gzip.decompress(data) if p.suffix=='.gz' else data)
def save(name,x):
 p=B/'artifacts'/name;data=(json.dumps(x,indent=2,ensure_ascii=False)+'\n').encode()
 p.write_bytes(gzip.compress(data,mtime=0) if p.suffix=='.gz' else data)
def pattern(u):
 table={};out=[]
 for x in u:
  if x not in table:table[x]=len(table)
  out.append(table[x])
 return tuple(out)
def key(p):return '.'.join(map(str,p))
def variants(w):
 yield None,w
 for i in range(1,len(w)-1):
  for j in range(i+1,len(w)):yield [i,j],w[:i]+w[j:]
def envelope(W):
 maps={'FWD':{},'BIDIR':{}}
 for w in sorted(W):
  for gap,retained in variants(w):
   for direction,out in [('FWD',retained),('REV',retained[::-1])]:
    p=pattern(out);witness={'pattern':list(p),'word':w,'gap':gap,'direction':direction,'retained':retained,'output':out};k=key(p)
    maps['BIDIR'].setdefault(k,witness)
    if direction=='FWD':maps['FWD'].setdefault(k,witness)
 return {'modes':maps}
def controls():
 words=[''.join(w) for n in range(1,6) for w in itertools.product('ab',repeat=n)];checks=0
 for w in words:
  direct={v for _,v in variants(w)};other={w}|{w[:p]+w[-q:] for p in range(1,len(w)) for q in range(1,len(w)-p)};assert direct==other
  for _,v in variants(w):
   assert len(v)>=min(2,len(w)) and v[0]==w[0] and v[-1]==w[-1]
   for order in itertools.permutations('ab'):
    trans=dict(zip('ab',order));assert pattern(v)==pattern(''.join(trans[x] for x in v));checks+=1
 for a in words:
  for z in words:
   if len(a)!=len(z):continue
   bij=any(''.join(dict(zip('ab',p))[c] for c in a)==z for p in itertools.permutations('ab'));assert (pattern(a)==pattern(z))==bij;checks+=1
 assert pattern('abccde')!=(0,1,2,3,3,4)
 toy=['abcaad','abba'];e=envelope(toy);fwd={key(pattern(v)) for w in toy for _,v in variants(w)};rev={key(pattern(v[::-1])) for w in toy for _,v in variants(w)}
 assert set(e['modes']['FWD'])==fwd and set(e['modes']['BIDIR'])==fwd|rev
 return {'status':'PASS_SOURCE_FREE_CONTROLS','checks':checks,'literal_and_one_gap':True,'bijection_pattern_equivalence':True,'reversed_envelope':True,'empirical_data_read':False}
def support(p,maps,lengths):
 if key(p) in maps:return 'SUPPORTED'
 return 'LENGTH_UNSUPPORTED' if len(p) not in lengths else 'PATTERN_UNSUPPORTED'
def summarize(rows):
 bad=[x for x in rows if x['_status']!='SUPPORTED'];leafs=sorted({re.match(r'f\d+',p).group() for x in bad for p in x['pages']})
 return {'types':len(rows),'occurrences':sum(x['count'] for x in rows),'unsupported_types':len(bad),'unsupported_occurrences':sum(x['count'] for x in bad),'unsupported_leaves':leafs,'length_failure_types':sum(x['_status']=='LENGTH_UNSUPPORTED' for x in bad),'pattern_failure_types':sum(x['_status']=='PATTERN_UNSUPPORTED' for x in bad),'status':'EXCLUDED' if bad else 'WORDWISE_SUPPORTED'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');a=ap.parse_args()
 if a.controls:print(json.dumps(controls()));return
 for pin in read(B/'LOCK.json')['files']:assert hashlib.sha256((R/pin['path']).read_bytes()).hexdigest()==pin['sha256'],pin['path']
 spec=read(B/'src/SPEC.json');source=read(R/'experiments/yolo/gdt1228_bare_hebrew_bijection_screen/artifacts/SOURCE_PROJECTION.json');words=[w for sec in source['source_sections'] for w in sec['words']];W=set(words);old=read(R/'experiments/yolo/gdt1396_inner_deletion_singleton_wordbook/artifacts/RESULT.json')['source'];whash=hashlib.sha256('\n'.join(sorted(W)).encode()).hexdigest();assert whash==old['wordbook_sha256'];assert len(W)==2411 and len(words)==6288 and len(set(''.join(W)))==22
 env=envelope(W);lengths={mode:{len(w['pattern']) for w in v.values()} for mode,v in env['modes'].items()};src={'wordbook_types':len(W),'tokens':len(words),'sections':len(source['source_sections']),'alphabet_size':22,'max_word_length':max(map(len,W)),'wordbook_sha256':whash,'modes':{mode:{'patterns':len(v),'lengths':sorted(lengths[mode])} for mode,v in env['modes'].items()}}
 cache=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');out={'source':src,'readers':{}};saved={};pat=re.compile('|'.join(sorted(spec['signs'],key=lambda x:(-len(x),x))))
 for ed in spec['readers']:
  grouped=collections.defaultdict(list)
  for row in cache[ed]:
   assert row['edition']==ed and row['kind']=='P' and not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v') and row['left_separator']==row['right_separator']=='DEFINITE_SPACE';units=pat.findall(row['ivtff_group_raw']);assert units==row['units'] and ''.join(units)==row['ivtff_group_raw'];grouped[row['ivtff_group_raw']].append(row)
  rows=[]
  for form,occ in sorted(grouped.items()):
   units=occ[0]['units'];p=pattern(units);rows.append({'form':form,'units':units,'pattern':list(p),'pattern_key':key(p),'count':len(occ),'ids':sorted(x['id'] for x in occ),'pages':sorted({x['page'] for x in occ}),'status':{mode:support(p,env['modes'][mode],lengths[mode]) for mode in spec['modes']}})
  modes={};first={}
  for mode in spec['modes']:
   prepared=[dict(x,_status=x['status'][mode]) for x in rows];modes[mode]={'ALL':summarize(prepared),'GE2':summarize([x for x in prepared if x['count']>=spec['recurrence_min']])};bad=sorted((x for x in prepared if x['_status']!='SUPPORTED'),key=lambda x:(-x['count'],x['form']));first[mode]=[{'form':x['form'],'count':x['count'],'status':x['_status'],'first_id':x['ids'][0]} for x in bad[:10]]
  out['readers'][ed]={'strict_groups':len(cache[ed]),'native_types':len(rows),'native_max_units':max(len(x['units']) for x in rows),'modes':modes,'first_failures':first};saved[ed]=rows
 ws=read(R/'research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929/LEXICAL_WORKSHEET_20261016.json');selected=[u for u in ws['units'] if u['unit_id']==spec['passage_unit']];assert len(selected)==1;unit=selected[0];groups=[]
 for line in unit['lines']:
  m=line['metadata'];assert m['page']=='f75v' and m['edition']=='IT2a';assert line['diplomatic_forms']==[g[2] for g in line['original_groups']]
  for g in line['original_groups']:
   raw=g[2];u=pat.findall(raw);valid=bool(raw) and ''.join(u)==raw;p=pattern(u) if valid else None
   groups.append({'original':g,'page':m['page'],'locus':m['locus'],'units':u if valid else None,'pattern':list(p) if valid else None,'status':{mode:support(p,env['modes'][mode],lengths[mode]) if valid else 'UNPARSEABLE' for mode in spec['modes']}})
 assert len(groups)==spec['passage_expected_groups'];badids=[x['original'][0] for x in groups if x['units'] is None];passage={'unit_id':spec['passage_unit'],'reader':'IT2a','original_groups':len(groups),'scorable_groups':len(groups)-len(badids),'unparseable_ids':badids,'modes':{},'groups':groups}
 for mode in spec['modes']:
  n=sum(x['status'][mode] not in ('SUPPORTED','UNPARSEABLE') for x in groups);passage['modes'][mode]={'status':'UNSCORABLE' if badids else ('WHOLE_PASSAGE_EXCLUDED' if n else 'WORDWISE_SUPPORTED_ONLY'),'unsupported_groups':n}
 out['passage']=passage;dec=[x['modes']['BIDIR']['ALL']['status']=='EXCLUDED' for x in out['readers'].values()];out['status']='FIXED_W_ONE_GAP_ENVELOPE_EXCLUDED_ALL_READERS' if all(dec) else ('MIXED_WORD_ENVELOPE' if any(dec) else 'NECESSARY_WORDWISE_SUPPORT_ONLY')
 save('SOURCE_ENVELOPE.json',env);save('NATIVE_SUPPORT.json.gz',{'readers':saved});save('RESULT.json',out);print(json.dumps({'status':out['status'],'source':src,'readers':{ed:{'BIDIR_ALL':v['modes']['BIDIR']['ALL'],'BIDIR_GE2':v['modes']['BIDIR']['GE2']} for ed,v in out['readers'].items()},'passage':passage['modes']},indent=2))
if __name__=='__main__':main()
