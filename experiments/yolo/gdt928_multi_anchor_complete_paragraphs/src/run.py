import collections,itertools,json,re,hashlib,csv
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];P=R/'experiments/yolo/gdt915_terminal_lr_phrase_transfer';EDS=['ZL3b','IT2a','RF1b']
def write(n,x):(E/'artifacts'/n).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def load():
 for p,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 allowed=set(json.loads((P/'src/SPEC.json').read_text())['allowed_selectors']);panels={};dens={}
 for ed in EDS:
  pages=collections.defaultdict(list);den=collections.Counter()
  for phase in ['DISCOVERY','EVALUATION']:
   d=json.loads((P/'artifacts'/f'SOURCE_{phase}_{ed}.json').read_text())
   for r in d['lines']:
    m=r['metadata'];assert m['page'] in allowed and not m['page'].startswith('f84')
    if m['kind']!='P':continue
    gs=[dict(zip(d['group_columns'],g)) for g in r['groups']];w=[g['ivtff_group_raw'] for g in gs]
    eligible=len(w)>=2 and all(re.fullmatch('[a-z]+',z) for z in w) and all(int(b['source_group_index'])==int(a['source_group_index'])+1 and a['right_separator']==b['left_separator']=='DEFINITE_SPACE' for a,b in zip(gs,gs[1:]))
    pages[m['page']].append({'locus':m['locus'],'row':int(m['source_row_index']),'start':m['paragraph_start']=='1','end':m['paragraph_end']=='1','words':w,'source_ids':[g['source_group_id'] for g in gs],'anchor_eligible':eligible});den['P_lines']+=1
  paras=[]
  for page,ls in sorted(pages.items()):
   active=[]
   for l in sorted(ls,key=lambda l:l['row']):
    if l['start']:
     if active:den['unclosed_start']+=1
     active=[]
    if l['start'] or active:active.append(l)
    if l['end'] and active:
     ns=[int(x['locus'].rsplit('.',1)[1]) for x in active]
     if all(b==a+1 for a,b in zip(ns,ns[1:])):
      off=0
      for x in active:x['offset']=off;off+=len(x['words'])
      paras.append({'id':page+'|'+active[0]['locus']+'-'+active[-1]['locus'],'page':page,'leaf':int(re.match(r'f(\d+)',page)[1]),'lines':active,'groups':off});den['complete_paragraphs']+=1;den['anchor_lines']+=sum(x['anchor_eligible'] for x in active)
     else:den['gapped_paragraphs']+=1
     active=[]
   if active:den['unclosed_end']+=1
  panels[ed]=paras;dens[ed]=dict(den)
 return panels,dens

def census(paras):
 index=collections.defaultdict(list);lines={};pm={p['id']:p for p in paras}
 for p in paras:
  for l in p['lines']:
   key=(p['id'],l['locus']);lines[key]=l
   if not l['anchor_eligible']:continue
   for i in range(len(l['words'])-2):
    a=tuple(l['words'][i:i+3])
    if len(set(a))>=2:index[a].append((p['id'],l['locus'],i))
 matches=collections.defaultdict(dict)
 for os in index.values():
  for a,b in itertools.combinations(os,2):
   if pm[a[0]]['leaf']==pm[b[0]]['leaf']:continue
   if a[0]>b[0]:a,b=b,a
   la,lb=lines[a[:2]],lines[b[:2]];wa,wb=la['words'],lb['words'];i,j=a[2],b[2];n=3
   while i>0 and j>0 and wa[i-1]==wb[j-1]:i-=1;j-=1;n+=1
   while i+n<len(wa) and j+n<len(wb) and wa[i+n]==wb[j+n]:n+=1
   key=(a[1],i,b[1],j,n);matches[(a[0],b[0])][key]={'a_locus':a[1],'b_locus':b[1],'a_start':i,'b_start':j,'a_offset':la['offset']+i,'b_offset':lb['offset']+j,'length':n,'words':wa[i:i+n],'a_source_ids':la['source_ids'][i:i+n],'b_source_ids':lb['source_ids'][j:j+n]}
 pairs=[]
 for (a,b),ms in sorted(matches.items()):
  ms=sorted(ms.values(),key=lambda m:(m['a_offset'],m['b_offset'],m['length']));orders=[]
  for i,j in itertools.combinations(range(len(ms)),2):
   x,y=ms[i],ms[j]
   da=1 if x['a_offset']+x['length']<=y['a_offset'] else -1 if y['a_offset']+y['length']<=x['a_offset'] else 0
   db=1 if x['b_offset']+x['length']<=y['b_offset'] else -1 if y['b_offset']+y['length']<=x['b_offset'] else 0
   if da and db:orders.append({'match1':i,'match2':j,'order':'SAME' if da==db else 'REVERSED','distinct_strings':x['words']!=y['words']})
  kinds={o['order'] for o in orders};pairs.append({'a':a,'b':b,'matches':ms,'disjoint_match_pairs':orders,'qualifies':bool(orders),'order_status':'AMBIGUOUS' if len(kinds)>1 else next(iter(kinds)) if kinds else 'NO_DISJOINT_PAIR'})
 return pairs

def main():
 panels,dens=load();write('PARAGRAPHS.json',panels);allpairs={ed:census(ps) for ed,ps in panels.items()};write('PAIRS.json',allpairs)
 summary={'status':'COMPLETE_EXPOSED_MULTI_ANCHOR_CENSUS','denominators':dens,'panels':{ed:{'paragraph_pairs_with_match':len(ps),'qualifying_pairs':sum(p['qualifies'] for p in ps),'order_counts':dict(collections.Counter(p['order_status'] for p in ps)),'qualifying_distinct_strings':sum(any(o['distinct_strings'] for o in p['disjoint_match_pairs']) for p in ps)} for ed,ps in allpairs.items()},'meanings':0,'significance_claim':False,'held_access':False};write('RESULT.json',summary)
 with (E/'artifacts/PAIR_INDEX.tsv').open('w') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['edition','paragraph_a','paragraph_b','maximal_matches','disjoint_pairs','order_status','row_status'])
  for ed,ps in allpairs.items():
   for p in ps:w.writerow([ed,p['a'],p['b'],len(p['matches']),len(p['disjoint_match_pairs']),p['order_status'],'recorded'])
 text=['# All qualifying complete-paragraph pairs','','Every qualifying pair and all correspondences; no semantic roles assigned. Full paragraph groups and uncertainties remain visible. RF without boundaries supplies no paragraph-order evidence.','']
 for ed,ps in allpairs.items():
  pm={p['id']:p for p in panels[ed]};text+=['## '+ed,'']
  for i,p in enumerate([p for p in ps if p['qualifies']],1):
   text += [f"### {i}. {p['a']} / {p['b']}",'','Order: '+p['order_status']+'.','']
   for j,m in enumerate(p['matches']):text.append(f"Match {j}: `{' '.join(m['words'])}` — {m['a_locus']}:{m['a_start']+1} / {m['b_locus']}:{m['b_start']+1}.")
   text+=['','All disjoint comparisons: '+json.dumps(p['disjoint_match_pairs']), '']
   for pid in [p['a'],p['b']]:
    text+=['Paragraph '+pid+':','']
    text += [l['locus']+': `'+ ' '.join(l['words'])+'`' for l in pm[pid]['lines']];text.append('')
  if not any(p['qualifies'] for p in ps):text+=['No qualifying pair.','']
 (E/'CANDIDATE_PARAGRAPHS.md').write_text('\n'.join(text).rstrip()+'\n');print(json.dumps(summary))
if __name__=='__main__':main()
