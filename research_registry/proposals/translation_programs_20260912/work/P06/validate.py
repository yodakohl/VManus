import csv,json,hashlib
from fractions import Fraction
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P06')
def read(n):return list(csv.DictReader((D/n).open(),delimiter='\t'))
s=json.loads((D/'SOURCE.json').read_text());p=Path(s['source'])
assert hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256'];assert hashlib.sha256((D/'DECISION.md').read_bytes()).hexdigest()==s['decision_sha256']
seq=[(r['record_id'],r['locus']+':'+str(i),w) for r in csv.DictReader(p.open(),delimiter='\t') for i,w in enumerate(r['zl3b_line'].split(),1)]
model=json.loads((D/'MODEL.json').read_text());ns=model['nouns'];ops=model['operators'];ix={a:i for i,(_,a,_) in enumerate(seq)}
for m in ['C','I']:assert [(r['record'],r['at'],r['word']) for r in read('ALIGNMENT_'+m+'.tsv')]==seq
bs=read('BINDINGS.tsv');assert len(bs)==19
for b in bs:
 i=ix[b['at']];left=[a for r,a,w in seq[:i] if r==b['record'] and w in ns];right=[]
 for r,a,w in seq[i+1:]:
  if r!=b['record'] or w in ops:break
  if w in ns:right.append(a)
 ni,no=(1,2) if b['word']=='qokeedy' else (2,1)
 assert b['inputs']==','.join(left[-ni:]) and b['outputs']==','.join(right[:no])
# Replay mass witnesses without importing the builder.
mentions={r['at']:r for r in read('MENTIONS_C.tsv')};events={r['at']:r for r in read('EVENTS_C.tsv')};bound={b['at']:b for b in bs}
for rid in {r for r,_,_ in seq}:
 live={};created=set();total=Fraction(0);pos={};latest={};output_positions={}
 for r,at,w in seq:
  if r!=rid:continue
  if w in ns:
   q=mentions[at]['portion']
   if at in output_positions:assert q==output_positions[at];latest[w]=q
   elif w not in latest:
    assert q=='E@'+at;live[q]=Fraction(1);created.add(q);total+=1;latest[w]=q
   else:assert q==(latest[w] if latest[w] in live else '')
   pos[at]=q
  if at in events:
   e=events[at];b=bound[at];ins=list(filter(None,b['inputs'].split(',')));actual=[pos.get(a,'') for a in ins]
   assert e['input_ids']==','.join(actual)
   if e['status']=='PASS':
    assert not b['missing'] and all(q in live for q in actual) and len(set(actual))==len(actual)
    lhs,rhs=e['witness'].split(' = ');im=[Fraction(t) for t in lhs.split('+')];om=[Fraction(t) for t in rhs.split('+')]
    assert im==[live[q] for q in actual] and sum(im)==sum(om) and all(v>0 for v in om)
    for q in actual:del live[q]
    outids=e['output_ids'].split(',');assert len(outids)==len(om)
    for loc,q,mass in zip(b['outputs'].split(','),outids,om):assert q not in created;created.add(q);live[q]=mass;output_positions[loc]=q
   else:assert not e['output_ids'] and not e['equation']
  assert sum(live.values())==total
 final=next(b for b in read('BALANCES_C.tsv') if b['record']==rid);assert Fraction(final['remaining_witness_mass'])==total==Fraction(final['external_witness_mass'])
for c in read('CYCLES.tsv'):
 a,b=events[c['split']],events[c['merge']];assert a['word']=='qokeedy' and b['word']=='qokedy' and a['status']==b['status']=='PASS'
 assert set(a['output_ids'].split(','))==set(b['input_ids'].split(',')) and ix[c['split']]<ix[c['merge']]
for e in read('EVENTS_I.tsv'):
 if e['status']=='PASS':
  l,r=e['witness'].split(' = ');assert sum(Fraction(v) for v in l.split('+'))==sum(Fraction(v) for v in r.split('+'))
(D/'VALIDATION.json').write_text(json.dumps(dict(status='PASS',checks=['source/decision hashes','both341group alignments','all19fixed argument sets','independent full inventory and mention replay','positive rational conservation witnesses','no duplicated consumed inputs','exact split-child reunion','independent-trial local balances'],limitation='Witness masses arbitrary; no meaning or physical flow validation'),indent=2)+'\n')
print('PASS')
