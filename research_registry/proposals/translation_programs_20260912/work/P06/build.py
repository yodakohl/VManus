import csv,json,hashlib
from fractions import Fraction
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P06');S=D.parent/'P12/PROSE.tsv'
ns={'shedy':'Gemisch','lchedy':'Rückstand','qokeey':'Flüssigkeit','shckhedy':'Fraktion'};ops={'qokeedy':'trenne','qokedy':'vereinige'}
records={}
for r in csv.DictReader(S.open(),delimiter='\t'):
 records.setdefault(r['record_id'],[]).extend(dict(record=r['record_id'],at=r['locus']+':'+str(i),word=w) for i,w in enumerate(r['zl3b_line'].split(),1))
def dump(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def tab(n,rs):
 with (D/n).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=list(rs[0])+['row_status'],delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(dict(r,row_status='recorded') for r in rs)
dump('SOURCE.json',dict(source=str(S),sha256=hashlib.sha256(S.read_bytes()).hexdigest(),decision_sha256=hashlib.sha256((D/'DECISION.md').read_bytes()).hexdigest(),sealed=['f84','f84r'],exposure='Entire f83r previously exposed; no independent confirmation'))
dump('MODEL.json',dict(nouns=ns,operators=ops,variants=['C linked inventory','I independent trials'],numeric_witness='each external portion mass1; split in halves; merge sum; arbitrary witness, not decoded quantities'))
bindings=[]
for rid,ts in records.items():
 for i,t in enumerate(ts):
  if t['word'] not in ops:continue
  left=[x for x in ts[:i] if x['word'] in ns];right=[]
  for x in ts[i+1:]:
   if x['word'] in ops:break
   if x['word'] in ns:right.append(x)
  ni,no=(1,2) if t['word']=='qokeedy' else (2,1)
  ins=left[-ni:];outs=right[:no]
  bindings.append(dict(record=rid,at=t['at'],word=t['word'],inputs=','.join(x['at'] for x in ins),outputs=','.join(x['at'] for x in outs),input_need=ni,output_need=no,missing=','.join(k for k,v in [('inputs',len(ins)<ni),('outputs',len(outs)<no)] if v)))
tab('BINDINGS.tsv',bindings)
results={};cycles=[]
for mode in ['C','I']:
 events=[];mentions=[];balances=[];alignment=[]
 for rid,ts in records.items():
  inventory={};latest={};positions={};reserved={};introduced=Fraction(0);source_count=0;wordat={t['at']:t['word'] for t in ts}
  md=['# '+rid+' / '+mode,'','Alle Werte hypothetisch. Zahlen sind nur frei gewählte Bilanzzeugen. ⟦…⟧ offen.','']
  for t in ts:
   w=t['word'];at=t['at'];reading=ns.get(w,'⟦'+w+'⟧')
   if mode=='C' and w in ns:
    if at in reserved:pid=reserved[at];latest[w]=pid
    elif w not in latest:
     pid='E@'+at;latest[w]=pid;inventory[pid]=dict(mass=Fraction(1),available=True,parent='',origin=at);introduced+=1;source_count+=1
    else:
     pid=latest[w]
     if not inventory[pid]['available']:pid=''
    positions[at]=pid
    mentions.append(dict(record=rid,at=at,word=w,portion=pid,status='BOUND' if pid else 'DEPLETED'))
    reading+=' [Portion='+pid+']'
   if w in ops:
    b=next(b for b in bindings if b['at']==at);ins=list(filter(None,b['inputs'].split(',')));outs=list(filter(None,b['outputs'].split(',')));errors=[b['missing']] if b['missing'] else [];pids=[];new=[];eq='';witness='';rejoin=''
    if mode=='C':
     pids=[positions.get(p,'') for p in ins]
     if any(not p for p in pids):errors.append('unavailable_reference')
     if any(p and not inventory[p]['available'] for p in pids):errors.append('consumed_input')
     if len([p for p in pids if p])!=len(set(p for p in pids if p)):errors.append('same_portion_twice')
    else:pids=['I@'+at+':in'+str(j) for j in range(len(ins))]
    if not errors:
     masses=[inventory[p]['mass'] for p in pids] if mode=='C' else [Fraction(1)]*len(pids)
     total=sum(masses);outm=[total/2,total/2] if w=='qokeedy' else [total]
     new=['O@'+at+':'+str(j) for j in range(len(outs))]
     eq='+'.join('m('+p+')' for p in pids)+' = '+'+'.join('m('+p+')' for p in new)
     witness='+'.join(map(str,masses))+' = '+'+'.join(map(str,outm))
     if mode=='C':
      parents=[inventory[p]['parent'] for p in pids]
      if w=='qokedy' and len(set(parents))==1 and parents[0]:
       producer=next(e for e in events if e['at']==parents[0] and e['record']==rid)
       if producer['word']=='qokeedy' and set(pids)==set(producer['output_ids'].split(',')):rejoin=parents[0];cycles.append(dict(record=rid,split=rejoin,merge=at,children=','.join(pids),result=new[0],mass_equal_input=True))
      for p in pids:inventory[p]['available']=False
      for out,p,mass in zip(outs,new,outm):inventory[p]=dict(mass=mass,available=True,parent=at,origin=out);reserved[out]=p
     else:source_count+=len(pids);introduced+=total
    status='PASS' if not errors else ','.join(errors)
    events.append(dict(record=rid,at=at,word=w,status=status,input_ids=','.join(pids),output_ids=','.join(new),equation=eq,witness=witness,rejoins_split=rejoin))
    reading=ops[w]+' [Eingaben='+b['inputs']+'; Ausgaben='+b['outputs']+'; '+status+'; '+eq+']'
   if mode=='C':assert sum(p['mass'] for p in inventory.values() if p['available'])==introduced
   alignment.append(dict(record=rid,at=at,word=w,reading=reading));md.append(at+' '+reading)
  (D/(rid+'_'+mode+'.md')).write_text('\n'.join(md)+'\n')
  balances.append(dict(record=rid,external_portions=source_count,external_witness_mass=str(introduced),remaining_witness_mass=str(sum(p['mass'] for p in inventory.values() if p['available'])) if mode=='C' else 'separate trials',remaining_ids=','.join(p for p,v in inventory.items() if v['available']) if mode=='C' else 'no cross-trial identity'))
 tab('EVENTS_'+mode+'.tsv',events);tab('BALANCES_'+mode+'.tsv',balances);tab('ALIGNMENT_'+mode+'.tsv',alignment)
 if mode=='C':tab('MENTIONS_C.tsv',mentions)
 results[mode]=dict(events=len(events),successful=sum(e['status']=='PASS' for e in events),successful_splits=sum(e['status']=='PASS' and e['word']=='qokeedy' for e in events),successful_merges=sum(e['status']=='PASS' and e['word']=='qokedy' for e in events),external_portions=sum(b['external_portions'] for b in balances))
with (D/'CYCLES.tsv').open('w') as f:
 wr=csv.DictWriter(f,fieldnames=['record','split','merge','children','result','mass_equal_input'],delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(cycles)
coverage=[dict(record=r,groups=len(ts),hypothesis=sum(t['word'] in ns or t['word'] in ops for t in ts)) for r,ts in records.items()];tab('COVERAGE.tsv',coverage)
dump('RESULT.json',dict(groups=341,hypothesis_positions=sum(c['hypothesis'] for c in coverage),open_positions=341-sum(c['hypothesis'] for c in coverage),summary=results,cycles=cycles,confirmed_meanings=0))
print((D/'RESULT.json').read_text())
