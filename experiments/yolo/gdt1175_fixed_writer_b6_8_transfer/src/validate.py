#!/usr/bin/env python3
"""Artifact validation; independent surface count is not a semantic proof."""
from pathlib import Path
import json,re,xml.etree.ElementTree as E
from collections import Counter
import run
HERE=Path(__file__).resolve().parents[1];ART=HERE/'artifacts'
# Independent greedy scanner; inherited22 signs, not Python character counts.
PAT=re.compile(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]')
def surface_counts(text):
 lengths=[];payload=[]
 for word in text.split():
  signs=PAT.findall(word)
  assert ''.join(signs)==word,word
  lengths.append(len(signs))
  core=signs[1:] if signs[0]=='m' else signs[:]
  if 'y' in core:core=core[:core.index('y')]
  i=0
  while i<len(core):
   if core[i]!='l':i+=1;continue
   end=core.index('r',i+1)
   cost=end-i+1
   if i>=2 and core[i-2]=='e' and core[i-1] in 'aoei':cost+=2
   payload.append(cost);i=end+1
 return lengths,payload

def main():
 lock=run.verify_lock()
 expected=run.calculate()
 observed=json.loads((ART/'RESULT.json').read_text())
 assert json.loads(json.dumps(expected))==observed,'Result not reproducible'
 assert (ART/'WRITTEN.txt').read_text()==observed['encoded_text']+'\n'
 src=json.loads((ART/'SOURCE_ACCOUNT.json').read_text())
 node=E.parse(ART/'SOURCE.xml').getroot()
 exact=' '.join(''.join(node.itertext()).split())
 assert src['source_text']==exact==' '.join(c['source'] for c in src['clauses'])
 assert node.get('{http://www.w3.org/XML/1998/namespace}id')=='b6.8'
 assert not any(x.tag.split('}')[-1] in {'gap','unclear','supplied'} for x in node.iter())
 assert not any(x in exact for x in ('[...]','…','...'))
 source_words=set(exact.lower().split())
 for v in observed['literal_occurrences']:assert v['name'].split(':',1)[1] in source_words,v
 lengths,payload=surface_counts(observed['encoded_text'])
 assert sum(lengths)==observed['glyphs'] and len(lengths)==observed['words']
 assert len(payload)==len(observed['literal_occurrences'])
 assert Counter(payload)==Counter(v['glyphs'] for v in observed['literal_occurrences'])
 assert sum(payload)==observed['literal_glyphs']
 assert (sum(payload)*2>sum(lengths))==observed['literal_over_half']
 assert observed['grammar_roots']==29 and observed['grammar_tags']==17
 # Meaning-bearing reference/quantity choices, not claims source syntax is proven.
 assert 'QUOTE1:zwenn(QUOTE1:toterr(PLURAL(EGG)))' in observed['readback'][3]
 assert 'TAKE' not in observed['readback'][2] and 'PUT' not in observed['readback'][2]
 assert 'NOT(EXCESS(APPLY(SALT_MATERIAL, UNSAID)))' in observed['readback'][-1]
 result={'status':'PASS','experiment':'GDT1175','locked_files_verified':len(lock['files']),
 'checks':['frozen input and runner hashes','exact contiguous source coverage','source completeness markers','all literal labels are single source words','unchanged writer reproducibility and roundtrip','independent multigraph surface cost including typed predicates','fixed29roots17tags','unresolved-fragment/numeral/salt obligations'],
 'ceiling':'Scoped validation only; no automatic proof of manual source interpretation, historicity, or native meaning.'}
 (ART/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
