#!/usr/bin/env python3
"""Frozen-source forward writing; no manuscript input or new writer rules."""
from pathlib import Path
from collections import Counter
import hashlib, importlib.util, json
HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parents[2]
ART=HERE/'artifacts'
WRITER=ROOT/'research_registry/proposals/production_origin_supply_20261003/B6_7_PRODUCTIVE_STEMS.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load_writer():
 spec=importlib.util.spec_from_file_location('fixed_b6_writer',WRITER)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 return m
def verify_lock():
 lock=json.loads((ART/'REGISTRATION_LOCK.json').read_text())
 for p,h in lock['files'].items():
  assert sha(ROOT/p)==h,('Frozen file changed',p)
 return lock
def calculate():
 verify_lock();m=load_writer()
 src=json.loads((ART/'SOURCE_ACCOUNT.json').read_text())
 trees=[m.from_json(c['tree']) for c in src['clauses']]
 text=m.write(trees)
 assert m.read(text)==trees
 assert m.read(' '.join(text.split()))==trees
 words=text.split();lengths=[len(m.tokenize(w)) for w in words]
 literals=[]
 def walk(t,clause):
  name,kids=t
  if name.startswith(('LIT:','QUOTE')):
   value=name.split(':',1)[1]
   cost=len(m.literal(value))+(2 if name.startswith('QUOTE') else 0)
   literals.append({'clause':clause,'name':name,'glyphs':cost})
  for k in kids:walk(k,clause)
 for c,t in zip(src['clauses'],trees):walk(t,c['id'])
 total=sum(lengths);cost=sum(x['glyphs'] for x in literals)
 stop=bool(src['rule_changes'] or src['unrepresented_content'] or 2*cost>total)
 result={'experiment':'GDT1175','source_id':'b6.8','status':'STOP_FIXED_WRITER_LARGE_RUN' if stop else 'PASS_CONDITIONAL_ENGINEERING_TRANSFER',
 'clauses':len(trees),'words':len(words),'types':len(set(words)),'glyphs':total,
 'mean_glyphs_per_word':total/len(words),'max_word_glyphs':max(lengths),
 'length_counts':dict(sorted(Counter(lengths).items())),
 'literal_occurrences':literals,'literal_glyphs':cost,'literal_fraction':cost/total,
 'literal_over_half':2*cost>total,'rule_changes':src['rule_changes'],'unrepresented_content':src['unrepresented_content'],
 'roundtrip':True,'linebreaks_irrelevant':True,'grammar_roots':len(m.LEX),'grammar_tags':len(m.TAG),
 'claim_ceiling':'Stipulated semantic/opaque-word account only. Unknown source words require external language knowledge. No target statistics, historical authenticity, native gloss or independent holdout.',
 'encoded_text':text,'readback':[m.show(t) for t in m.read(text)]}
 return result

def main():
 result=calculate()
 (ART/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 (ART/'WRITTEN.txt').write_text(result['encoded_text']+'\n')
 src=json.loads((ART/'SOURCE_ACCOUNT.json').read_text())
 rows=['# Vollständige feste b6.8-Schreibprobe','',
 'Erfundene Schriftzeichenfolgen; keine Voynich-Wortbedeutungen. Rücklesung der festgehaltenen Quellannahmen; ausgeschriebene unbekannte Wörter bleiben ohne Sprachkenntnis unbekannt.','']
 for c,line,tree in zip(src['clauses'],result['encoded_text'].splitlines(),result['readback']):
  rows += ['## '+c['id'],'',c['source'],'','```text',line,'```','',c['reading'],'','`'+tree+'`','']
 (ART/'FULL_TEXT.md').write_text('\n'.join(rows)+'\n')
 print(json.dumps({k:result[k] for k in ['status','clauses','words','glyphs','literal_glyphs','literal_fraction','roundtrip']},indent=2))
if __name__=='__main__':main()
