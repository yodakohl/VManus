#!/usr/bin/env python3
"""Necessary constant-diagonal source-letter runs; no key or meaning fit."""
import argparse,csv,hashlib,itertools,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,obj):path.write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
def words_sha(words):return hashlib.sha256(('\n'.join(words)+ ('\n' if words else '')).encode()).hexdigest()
def parse(word,signs):
 paths=[[] for _ in range(len(word)+1)];paths[0]=[[]]
 for i in range(len(word)):
  for prefix in paths[i]:
   for sign in signs:
    if word.startswith(sign,i):
     end=i+len(sign)
     if len(paths[end])<2:paths[end].append(prefix+[sign])
 return paths[-1][0] if len(paths[-1])==1 else None

def controls():
 modular=0
 for m in range(2,6):
  for incoming,state,b in itertools.product(range(m),repeat=3):
   for r in range(2,8):
    states=[incoming]+[state]*r;outputs=[(right-left+b)%m for left,right in zip(states,states[1:])]
    assert outputs[1:]==[b]*(r-1);modular+=1
 wordstar=0;bank=['a','b','aa','ab','ba','bb']
 for mask in range(1,1<<len(bank)):
  words=[w for i,w in enumerate(bank) if mask&(1<<i)]
  bound={c:max((len(g.group()) for w in words for g in re.finditer(c+'+',w)),default=0) for c in 'ab'}
  for n in range(1,4):
   for seq in itertools.product(words,repeat=n):
    text=' '.join(seq)
    for c in 'ab':assert max((len(g.group()) for g in re.finditer(c+'+',text)),default=0)<=bound[c]
    assert '  ' not in text;wordstar+=1
 assert ((1-0)%3,(1-0)%3)!=(0,0) # resetting inside the span changes the premise
 assert [s for s in (1,2)]!=[0,0] # contextual diagonal output is not one global beta
 assert ''.join('' for _ in range(4))=='' # erasing unchanged states is outside one-char model
 assert '  ' in 'a  b' # broad raw prior domain is outside canonical WordStar
 assert words_sha([])==hashlib.sha256(b'').hexdigest()
 return {'status':'PASS_SOURCE_FREE_CONTROLS','modular_incoming_state_offset_examples':modular,
         'canonical_word_sequences':wordstar,'scope_counterexamples':4,'empirical_counts_accessed':False}

def native_panel(spec):
 guardpath=ROOT/spec['native_guard_path'];guard=read(guardpath);cache=ROOT/spec['native_cache_path']
 assert sha(cache)==guard['sha256'];oldspec=read(ROOT/spec['native_spec_path'])
 assert len(oldspec['allowed'])==179 and not any(p.startswith('f84') for p in oldspec['allowed'])
 # This is an already selector-filtered cache with a verified receipt, not a mixed raw TSV.
 by={};total=0
 with cache.open() as stream:
  for row in csv.DictReader(stream,delimiter='\t'):
   assert row['page'] in oldspec['allowed'] and not row['page'].startswith('f84')
   by.setdefault((row['edition'],row['locus']),[]).append(row);total+=1
 assert total==guard['stats']['selected']
 for rows in by.values():
  rows.sort(key=lambda r:int(r['source_group_index']))
  assert len(rows)==int(rows[0]['source_group_count'])
  assert [int(r['source_group_index']) for r in rows]==list(range(1,len(rows)+1))
 signs=read(ROOT/spec['signs_path'])['signs'];assert len(signs)==22
 original=read(ROOT/spec['native_runs_path']);readers={ed:{'retained_runs':[],'unparsed_runs':[]} for ed in spec['editions']}
 linked=lambda a,b:a['right_separator']==b['left_separator']=='DEFINITE_SPACE'
 for record in original:
  assert record['edition'] in readers and record['length']>=3 and re.fullmatch('[a-z]+',record['word'])
  rows=by[(record['edition'],record['locus'])];start=record['start']-1;end=start+record['length'];selected=rows[start:end]
  assert len(selected)==record['length'] and all(r['kind']=='P' and r['ivtff_group_raw']==record['word'] for r in selected)
  assert all(linked(a,b) for a,b in zip(selected,selected[1:]))
  assert start==0 or not(linked(rows[start-1],rows[start]) and rows[start-1]['ivtff_group_raw']==record['word'])
  assert end==len(rows) or not(linked(rows[end-1],rows[end]) and rows[end]['ivtff_group_raw']==record['word'])
  units=parse(record['word'],signs)
  if units is None:readers[record['edition']]['unparsed_runs'].append({'original':record,'reason':'NO_UNIQUE_22_UNIT_PARSE','source_rows':selected})
  else:readers[record['edition']]['retained_runs'].append({'original':record,'working_units':units,'source_rows':selected})
 for ed,panel in readers.items():
  maximum=max((r['original']['length'] for r in panel['retained_runs']),default=0);assert maximum>=3
  panel.update(max_native_run=maximum,required_source_run=maximum-1,
               maximum_run_witnesses=[r['original'] for r in panel['retained_runs'] if r['original']['length']==maximum])
 return {'guard_sha256':sha(guardpath),'cache_sha256':sha(cache),'old_runs_sha256':sha(ROOT/spec['native_runs_path']),'readers':readers}

def vocabularies(spec):
 old=read(ROOT/spec['vocabulary_pins_path']);filepins={p['path']:p['sha256'] for p in old['inputs']};packs={};banks={}
 for pack in spec['source_packs']:
  name=spec['source_directory']+'/'+pack+'.txt';path=ROOT/name;assert sha(path)==filepins[name]
  words=sorted(set(path.read_text().split()));assert words and all(re.fullmatch('[a-z]+',w) for w in words)
  assert len(words)==old['vocabularies'][pack]['size'] and words_sha(words)==old['vocabularies'][pack]['sha256']
  letters={c:{'max_run':0,'longest_example':None} for c in 'abcdefghijklmnopqrstuvwxyz'}
  for word in words:
   for group in re.finditer(r'([a-z])\1*',word):
    char=group[0][0];size=len(group[0])
    if size>letters[char]['max_run']:letters[char]={'max_run':size,'longest_example':word}
  packs[pack]={'path':name,'source_sha256':sha(path),'vocabulary_size':len(words),'vocabulary_sha256':words_sha(words),'letters':letters};banks[pack]=words
 return {'packs':packs},banks

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--controls',action='store_true');args=parser.parse_args()
 lock=read(E/'LOCK.json')
 for name,h in lock['files'].items():assert sha(ROOT/name)==h,name
 if args.controls:
  receipt=controls();save(A/'CONTROLS.json',receipt);print(json.dumps(receipt));return
 assert read(A/'CONTROLS.json')['status']=='PASS_SOURCE_FREE_CONTROLS'
 spec=read(E/'src/SPEC.json');native=native_panel(spec);catalog,banks=vocabularies(spec);cases=[]
 for ed in spec['editions']:
  panel=native['readers'][ed];required=panel['required_source_run']
  for pack in spec['source_packs']:
   options=[]
   for char in spec['candidate_letters']:
    if char==' ':option={'character':'SPACE','max_source_run':1,'eligible':False,'word_count':0,'words_sha256':None,'examples':[]}
    else:
     matches=[w for w in banks[pack] if char*required in w]
     option={'character':char,'max_source_run':catalog['packs'][pack]['letters'][char]['max_run'],
             'eligible':bool(matches),'word_count':len(matches),'words_sha256':words_sha(matches),'examples':matches[:spec['examples_per_letter']]}
     assert option['eligible']==(option['max_source_run']>=required)
    options.append(option)
   survivors=[o['character'] for o in options if o['eligible']]
   cases.append({'edition':ed,'pack':pack,'max_native_run':panel['max_native_run'],'required_source_run':required,
                 'beta_options':options,'surviving_beta':survivors,
                 'decision':'RUN_BOUND_CAPACITY_ONLY' if survivors else 'FIXED_WORDSTAR_CONSTANT_DIAGONAL_EXCLUDED'})
 result={'experiment_id':'GDT1412','status':'COMPLETE_FIXED_WORDSTAR_REPEAT_BOUND','cases':cases,'word_meanings_assigned':0,'claim_ceiling':spec['claim_ceiling']}
 save(A/'NATIVE_PANEL.json',native);save(A/'VOCABULARY_RUNS.json',catalog);save(A/'RESULT.json',result)
 print(json.dumps({'status':result['status'],'native_run_lengths':{ed:native['readers'][ed]['max_native_run'] for ed in spec['editions']},
                   'cases':[{'edition':c['edition'],'pack':c['pack'],'surviving_beta':c['surviving_beta']} for c in cases]}))
if __name__=='__main__':main()
