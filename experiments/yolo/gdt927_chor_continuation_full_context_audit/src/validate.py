import json,re,hashlib,collections
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];P=R/'experiments/yolo/gdt915_terminal_lr_phrase_transfer'
for p,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
out=json.loads((E/'artifacts/OCCURRENCES.json').read_text());paras=json.loads((E/'artifacts/PARAGRAPHS.json').read_text());results=json.loads((E/'artifacts/RESULT.json').read_text());checks={}
for ed in ['ZL3b','IT2a','RF1b']:
 raw={}
 for phase in ['DISCOVERY','EVALUATION']:
  d=json.loads((P/'artifacts'/f'SOURCE_{phase}_{ed}.json').read_text());cols=d['group_columns']
  for l in d['lines']:
   m=l['metadata'];assert not m['page'].startswith('f84')
   if m['kind']=='P':raw[m['page']+'|'+m['locus']]=(m,[dict(zip(cols,g)) for g in l['groups']])
 expected=[]
 for uid,(m,gs) in raw.items():
  w=[g['ivtff_group_raw'] for g in gs]
  def safe(i):
   for a,b in [(i-1,i),(i,i+1)]:
    if a<0 or b>=len(gs):continue
    if gs[a]['right_separator']!='DEFINITE_SPACE' or gs[b]['left_separator']!='DEFINITE_SPACE' or int(gs[b]['source_group_index'])!=int(gs[a]['source_group_index'])+1:return False
   return True
  for start in range(len(w)):
   for n in [1,2]:
    t=' '.join(w[start:start+n])
    if len(w[start:start+n])!=n or t not in ['chor','ykchor','chordy','ykchor chordy']:continue
    expected.append((t,uid,start,all(safe(i) for i in range(start,start+n))))
 assert sorted(expected)==sorted((o['target'],o['line'],o['start'],o['locally_safe']) for o in out[ed])
 for p in paras[ed]:
  for l in p['lines']:assert l['words']==[g['ivtff_group_raw'] for g in raw[l['id']][1]]
  if p['complete_marked_paragraph']:
   assert p['lines'][0]['metadata']['paragraph_start']=='1' and p['lines'][-1]['metadata']['paragraph_end']=='1'
   ns=[int(l['metadata']['locus'].rsplit('.',1)[1]) for l in p['lines']];assert ns==list(range(ns[0],ns[-1]+1))
 assert len([o for o in out[ed] if o['target']=='ykchor chordy'])==1
 for t,c in results['panels'][ed]['counts'].items():
  os=[o for o in out[ed] if o['target']==t];ss=[o for o in os if o['locally_safe']]
  assert len(os)==c['exact_occurrences'] and len(ss)==c['safe_occurrences'] and sum(o['line_final'] for o in ss)==c['line_final']
  if c['paragraph_final'] is not None:assert sum(o['paragraph_final'] is True for o in ss)==c['paragraph_final']
 checks[ed]={'all_target_occurrences':len(expected),'paragraph_group_counts':[p['groups'] for p in paras[ed]],'complete_marked_paragraphs':sum(p['complete_marked_paragraph'] for p in paras[ed])}
# Recheck exported context and flank signatures from complete host words.
for ed,os in out.items():
 signatures={'chor':set(),'ykchor chordy':set()}
 hosts=json.loads((E/'artifacts/HOST_LINES.json').read_text())[ed]
 flags=results['panels'][ed]['paragraph_flags_available']
 for o in os:
  host=hosts[o['line']];w=host['words'];i=o['start'];n=len(o['target'].split());assert o['left']==w[:i] and o['right']==w[i+n:]
  assert o['line_final']==(i+n==len(w))
  assert o['paragraph_final']==(((i+n==len(w)) and host['metadata']['paragraph_end']=='1') if flags else None)
  sig=None
  if o['locally_safe'] and i>=2 and all(host['safe'][j] and re.fullmatch('[a-z]+',w[j]) for j in [i-2,i-1]):
   if i+n==len(w):following='PARAGRAPH_END' if flags and o['paragraph_final'] else 'LINE_END' if flags else 'UNKNOWN_PARAGRAPH_END'
   elif host['safe'][i+n] and re.fullmatch('[a-z]+',w[i+n]):following=w[i+n]
   else:following=None
   if following is not None:sig=[w[i-2],w[i-1],following]
  assert sig==o['signature']
  if o['target'] in signatures and o['signature'] is not None:signatures[o['target']].add(tuple(o['signature']))
 assert len(signatures['chor']&signatures['ykchor chordy'])==results['panels'][ed]['shared_flank_signatures']
v={'status':'PASS','coverage':'all original exact occurrences and local boundaries,seed paragraph coverage,all position counts,flank-signature intersections','panels':checks,'semantic_validation':False,'significance_control':False}
(E/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
