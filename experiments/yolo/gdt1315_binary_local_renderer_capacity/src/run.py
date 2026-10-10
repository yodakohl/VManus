import collections,csv,gzip,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2];SIGNS='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
def save(n,x):
 raw=(json.dumps(x,indent=2,sort_keys=True)+'\n').encode();(B/'artifacts'/n).write_bytes(gzip.compress(raw,mtime=0) if n.endswith('.gz') else raw)
def bits(units,mask):return ''.join(str((mask>>SIGNS.index(u))&1) for u in units)
def summarize(cells):
 hist=collections.Counter(len(v) for v in cells.values());maximum=max(hist,default=0);key=min((k for k,v in cells.items() if len(v)==maximum),default=None)
 return {'cells':len(cells),'distinct_output_histogram':dict(sorted(hist.items())),'state_lower_bound':maximum,'cells_exceeding_two':sum(n for k,n in hist.items() if k>2),'maximum_context':key,'maximum_witnesses':cells[key] if key is not None else {}}
def eligible_triples(rows):
 by={(r['locus'],int(r['source_group_index'])):r for r in rows}
 assert len(by)==len(rows)
 for (locus,i),r in sorted(by.items()):
  if (locus,i-1) in by and (locus,i+1) in by:
   a,c=by[locus,i-1],by[locus,i+1]
   if a['right_separator']==r['left_separator']==r['right_separator']==c['left_separator']=='DEFINITE_SPACE':yield a,r,c

def fixtures():
 assert summarize({('x',):{'A':0,'B':1}})['state_lower_bound']==2
 assert summarize({('x',):{'A':0,'B':1,'C':2}})['state_lower_bound']==3
 assert summarize({('x',1):{'A':0},('x',2):{'B':1}})['state_lower_bound']==1
 assert bits(['a'],1<<21)!=bits(['a','a'],1<<21)
 rows=[{'locus':'toy','source_group_index':i,'left_separator':'DEFINITE_SPACE','right_separator':'DEFINITE_SPACE'} for i in [1,2,4]];assert list(eligible_triples(rows))==[]
 return 'PASS'
def main():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 strict=json.loads(gzip.decompress((R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz').read_bytes()));edges=json.loads(gzip.decompress((R/'experiments/yolo/gdt1314_binary_line_edge_capacity/artifacts/EDGES.json.gz').read_bytes()));prior=json.loads((R/'experiments/yolo/gdt1314_binary_line_edge_capacity/artifacts/RESULT.json').read_text());allowed={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};results={};packets={};allconflicts={};joins=0
 for ed in ['ZL3b','IT2a','RF1b']:
  source={};meta={}
  for phase in ['DISCOVERY','EVALUATION']:
   for line in json.loads((R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{ed}.json').read_text())['lines']:
    m=line['metadata'];assert m['page'] in allowed and not m['page'].startswith('f84') and m['page'] not in ('f1r','f116v');assert m['edition']==ed;assert int(m['source_group_count'])==len(line['groups']);meta[m['locus']]=m
    for g in line['groups']:assert g[0] not in source;source[g[0]]=(m,g)
  rows=strict[ed]+edges[ed];assert len({r['id'] for r in rows})==len(rows)
  for r in rows:
   m,g=source[r['id']];assert m['page']==r['page'] and m['locus']==r['locus'] and m['kind']=='P';assert int(g[1])==int(r['source_group_index']) and g[2]==r['ivtff_group_raw'] and g[3]==r['left_separator'] and g[4]==r['right_separator'];assert ''.join(r['units'])==g[2];joins+=1
  events=[]
  for a,b,c in eligible_triples(rows):
   m=meta[b['locus']];events.append({'left':a,'center':b,'right':c,'line_group_count':int(m['source_group_count']),'paragraph_start':m['paragraph_start'],'paragraph_end':m['paragraph_end']})
  packets[ed]=events;keyresults=[];allconflicts[ed]={}
  for mask in prior['readers'][ed]['surviving_masks']:
   cells={level:collections.defaultdict(dict) for level in ['SOURCE','PAGE','LAYOUT']}
   for e in events:
    r=e['center'];triple=tuple(bits(e[t]['units'],mask) for t in ['left','center','right']);ctx={'SOURCE':triple,'PAGE':(r['page'],)+triple,'LAYOUT':(r['page'],int(r['source_group_index']),e['line_group_count'])+triple}
    for level,key in ctx.items():cells[level][key].setdefault(r['ivtff_group_raw'],r['id'])
   summary={level:summarize(c) for level,c in cells.items()};lb=summary['LAYOUT']['state_lower_bound'];conflicts=[{'context':k,'outputs':v} for k,v in sorted(cells['LAYOUT'].items()) if len(v)>2];allconflicts[ed][str(mask)]=conflicts
   keyresults.append({'mask':mask,'class1':[s for i,s in enumerate(SIGNS) if mask>>i&1],'levels':summary,'two_state_excluded':lb>2})
  results[ed]={'joined_groups':len(rows),'eligible_triples':len(events),'keys':keyresults,'all_keys_two_state_excluded':all(k['two_state_excluded'] for k in keyresults)}
  print(ed,len(events),[(k['class1'],[k['levels'][l]['state_lower_bound'] for l in ['SOURCE','PAGE','LAYOUT']]) for k in keyresults],flush=True)
 status='LOCAL_TWO_STATE_RENDERER_EXCLUDED' if all(r['all_keys_two_state_excluded'] for r in results.values()) else 'LOCAL_RENDERER_BOUND_ONLY'
 save('RESULT.json',{'status':status,'source_joins':joins,'fixtures':fixtures(),'readers':results,'ceiling':'Necessary hidden-input capacity for a fixed local deterministic renderer only; not native states, a realizable automaton or a general cipher rejection.'});save('EVENTS.json.gz',packets);save('CONFLICTS.json.gz',allconflicts)
if __name__=='__main__':main()
