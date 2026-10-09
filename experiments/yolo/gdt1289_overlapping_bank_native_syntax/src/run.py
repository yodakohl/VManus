import gzip,hashlib,itertools,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
SIGNS=['a','o','e','i','n','d','q','y','s','r','l','m','k','t','p','f','ch','sh','ckh','cth','cph','cfh']
ENDINGS=['a','ch','ckh','cth','d','e','f','i','k','l','m','n','o','p','r','s','sh','t','y']
SELECTORS=['q','cph','cfh'];PHASES=['N','E','Q','D2','D1']
CACHE='experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'
LINES='experiments/yolo/gdt983_qo_reduplication_expansion/artifacts/SOURCE_LINES.json'
PAIRS='experiments/yolo/gdt1274_shorter_reference_doublet_bound/artifacts/RESULT.json'
def save(n,x):(B/('artifacts/'+n+'.json')).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def gz(p):return json.loads(gzip.decompress((R/p).read_bytes()))
def step(states,symbol):
 out=set()
 for phase,bank in states:
  if symbol=='P':
   if phase in ['N','E','D1']:out.add(('N',bank))
   elif phase=='D2':out.add(('D1',bank))
  else:
   s=int(symbol[1:])
   if phase=='N':
    if s!=bank:out.add(('E',s))
    if s==0:out.add(('Q',bank))
   elif phase=='Q' and s==0:out.add(('D2',bank))
 return out

def trace(symbols,initial):
 current=set(initial);out=[sorted(current)]
 for x in symbols:current=step(current,x);out.append(sorted(current))
 return out

def fixtures():
 allstates={(p,b) for p in PHASES for b in range(3)};cases=[]
 for s in range(3):
  word=['S'+str(s),'P','S'+str(s),'P'];t=trace(word,allstates);assert not t[-1];cases.append({'symbols':word,'initial':sorted(allstates),'trace':t,'expected_nonempty':False})
 for word,start in [(['S0','P','S0'],{('N',1)}),(['S0','P','S0','S0','P','P'],{('N',1)}),(['S1','P','S2','P'],{('N',0)}),(['S0','P','P'],{('Q',2)})]:
  t=trace(word,start);assert t[-1];cases.append({'symbols':word,'initial':sorted(start),'trace':t,'expected_nonempty':True})
 return {'status':'PASS','cases':cases,'scope':'Relaxed necessary grammar, not full source-table legality.'}

def main():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for f,h in lock['hashes'].items():assert hashlib.sha256((R/f).read_bytes()).hexdigest()==h,f
 fx=fixtures();data=gz(CACHE);lines=json.loads((R/LINES).read_text());pairs=json.loads((R/PAIRS).read_text())['cases'];packet={};results={}
 for reader in ['ZL3b','IT2a','RF1b']:
  byword={}
  for r in data[reader]:
   assert not r['page'].startswith('f84') and r['page']!='f116v';assert r['left_separator']==r['right_separator']=='DEFINITE_SPACE';assert r['kind']=='P'
   byword.setdefault(tuple(r['units']),[]).append(r)
  nodes=gz('experiments/yolo/gdt1234_prefix_quotient_code_capacity/artifacts/CERTIFICATE_'+reader+'.json.gz')['nodes'];lookup={tuple(n['word']):i for i,n in enumerate(nodes)};ends=[]
  for g in ENDINGS:
   i=lookup[(g,)];ancestry=[i]
   while nodes[i]['parents'] is not None:
    left,long=nodes[i]['parents'];assert left<i and long<i
    assert nodes[long]['word']==nodes[left]['word']+nodes[i]['word'];i=long;ancestry.append(i)
   w=tuple(nodes[i]['word']);assert w[-1]==g and w in byword;rs=byword[w]
   ends.append({'unit':g,'ancestry':ancestry,'leaf':i,'word':''.join(w),'units':list(w),'source_ids':sorted(r['id'] for r in rs),'frequency':len(rs),'pages':sorted({r['page'] for r in rs})})
  line=lines[reader+'|f75v.39'];assert line['metadata']['edition']==reader and line['metadata']['page']=='f75v'
  candidates=[g for g in line['groups'] if g['ivtff_group_raw']=='qoqokeey'];assert len(candidates)==1
  qword=candidates[0];units=list('qoqokeey');assert units[:4]==list('qoqo') and len(units)>6
  pair=next(p for p in pairs if p['reader']==reader);groups={int(g['source_group_index']):g for g in pair['complete_line']};i=pair['first_group_index'];local=[groups[j] for j in [i-1,i,i+1,i+2]]
  assert local[1]['ivtff_group_raw']==local[2]['ivtff_group_raw']=='qokeedy'
  for a,b in zip(local,local[1:]):assert a['right_separator']==b['left_separator']=='DEFINITE_SPACE'
  cases=[]
  for permutation in itertools.permutations(range(3)):
   roles=dict(zip(SELECTORS,['S'+str(x) for x in permutation]));encode=lambda w:[roles.get(x,'P') for x in w]
   primary=trace(encode(units[:4]),{(p,b) for p in PHASES for b in range(3)})
   first=trace(encode(list('qokeedy')),{('N',b) for b in range(3)});middle={tuple(x) for x in first[-1] if x[0]=='N'};second=trace(encode(list('qokeedy')),middle)
   cases.append({'selector_roles':roles,'primary_prefix_trace':primary,'primary_compatible':bool(primary[-1]),'doublet_first_trace':first,'doublet_second_trace':second,'doublet_compatible':any(s[0]=='N' for s in second[-1])})
  pcount=sum(c['primary_compatible'] for c in cases);dcount=sum(c['doublet_compatible'] for c in cases)
  status='EXACT_BANK_CARRIER_SYNTAX_EXCLUDED' if len(ends)==19 and (pcount==0 or dcount==0) else 'NECESSARY_SYNTAX_CAPACITY'
  packet[reader]={'ending_witnesses':ends,'qoqo_complete_line':line,'qoqo_group':qword,'qoqo_units':units,'doublet_old_case':pair,'cases':cases}
  results[reader]={'status':status,'payload_units_forced':ENDINGS,'selector_units_forced':SELECTORS,'endpoint_types':len({e['word'] for e in ends}),'single_occurrence_endpoint_types':sorted({e['word'] for e in ends if e['frequency']==1}),'primary_compatible_assignments':pcount,'doublet_compatible_assignments':dcount,'qoqo_locus':'f75v.39','qoqo_left_separator':qword['left_separator'],'doublet_locus':pair['locus']}
 save('FIXTURES',fx);save('PACKET',packet);out={'status':'ALL_READERS_EXACT_OVERLAP_CARRIER_SYNTAX_EXCLUDED' if all(r['status']=='EXACT_BANK_CARRIER_SYNTAX_EXCLUDED' for r in results.values()) else 'MIXED_OR_CAPACITY','readers':results,'scope':'FullRAW982carrier under global22unitbijection and retained native boundaries; not all bank scripts or meaning.'};save('RESULT',out);print(json.dumps(out,indent=2))
if __name__=='__main__':main()
