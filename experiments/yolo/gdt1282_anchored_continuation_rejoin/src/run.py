import collections,hashlib,importlib.util,json,re,sys
from pathlib import Path
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parents[1];R=B.parents[2]
SEEDS='experiments/yolo/gdt926_repeated_context_continuation_atlas/artifacts/CANDIDATES_ZL3b.json'
PARAS='experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json'
def save(n,x):(B/('artifacts/'+n+'.json')).write_text(json.dumps(x,indent=2)+'\n')
def suffix_frames(p,div):
 out=[]
 for line in p['lines']:
  if not line['anchor_eligible']:continue
  for i in range(len(line['words'])-2):
   off=line['offset']+i;words=line['words'][i:i+3]
   if off>div and len(set(words))>=2:out.append({'offset':off,'locus':line['locus'],'i':i,'words':words,'line':line})
 return out

def joins(a,b,da,db,initial):
 left=suffix_frames(a,da);right=collections.defaultdict(list)
 for y in suffix_frames(b,db):right[tuple(y['words'])].append(y)
 out=[]
 for x in left:
  for y in right[tuple(x['words'])]:
   wa,wb=x['line']['words'],y['line']['words'];n=3
   while x['i']+n<len(wa) and y['i']+n<len(wb) and wa[x['i']+n]==wb[y['i']+n]:n+=1
   out.append({'a_offset':x['offset'],'b_offset':y['offset'],'a_locus':x['locus'],'b_locus':y['locus'],'a_start':x['i'],'b_start':y['i'],'three_words':x['words'],'right_extended_words':wa[x['i']:x['i']+n],'a_source_ids':x['line']['source_ids'][x['i']:x['i']+n],'b_source_ids':y['line']['source_ids'][y['i']:y['i']+n],'a_branch_groups':x['offset']-da,'b_branch_groups':y['offset']-db,'same_as_initial':x['words']==initial,'a_branch_excluded_lines':[l['locus'] for l in a['lines'] if not l['anchor_eligible'] and l['offset']<x['offset'] and l['offset']+len(l['words'])>da],'b_branch_excluded_lines':[l['locus'] for l in b['lines'] if not l['anchor_eligible'] and l['offset']<y['offset'] and l['offset']+len(l['words'])>db]})
 return sorted(out,key=lambda o:(o['a_branch_groups']+o['b_branch_groups'],max(o['a_branch_groups'],o['b_branch_groups']),o['a_offset'],o['b_offset'],o['three_words']))
def artificial(words,pid,leaf):return {'id':pid,'page':pid,'leaf':leaf,'groups':len(words),'lines':[{'locus':pid+'.1','row':1,'start':True,'end':True,'words':words,'source_ids':[pid+'|'+str(i) for i in range(len(words))],'anchor_eligible':True,'offset':0}]}
def controls():
 a=artificial(list('abcxdef'),'P',1);b=artificial(list('abcyabcxdef'),'Q',2);r=joins(a,b,3,3,list('abc'));assert any(x['three_words']==list('def') for x in r)
 path=R/'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/src/run.py';spec=importlib.util.spec_from_file_location('old928',path);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old);oldr=old.census([a,b]);assert len(oldr)==1 and not oldr[0]['qualifies']
 assert joins(a,artificial(list('abcydef'),'Q',2),3,3,list('abc'))
 assert not joins(a,artificial(list('abcymno'),'Q',2),3,3,list('abc'))
 assert not joins(artificial(list('abcdef'),'P',1),artificial(list('abcxdef'),'Q',2),3,3,list('abc'))
 same=joins(artificial(list('abcxabc'),'P',1),artificial(list('abcyabc'),'Q',2),3,3,list('abc'));assert same[0]['same_as_initial']
 split=artificial(list('abcydef'),'Q',2);split['lines']=[dict(split['lines'][0],words=list('abcyd'),source_ids=list('01234')),dict(split['lines'][0],locus='Q.2',words=list('ef'),source_ids=list('56'),offset=5)];assert not joins(a,split,3,3,list('abc'))
 return {'cases':6,'old928_counterexample_qualifies':False,'new_counterexample_joins':r}
def main():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 seeds=json.loads((R/SEEDS).read_text());panels=json.loads((R/PARAS).read_text());assert len(seeds)==13 and all(len(s['occurrences'])==2 and s['length']==3 for s in seeds);cases=[];selected={};summary={}
 for reader,paras in panels.items():
  locations={}
  for p in paras:
   assert not p['page'].startswith('f84') and p['page']!='f116v'
   for l in p['lines']:assert (p['page'],l['locus']) not in locations;locations[p['page'],l['locus']]=(p,l)
  readercases=[]
  for seed in seeds:
   sites=[]
   for o in seed['occurrences']:
    page,locus=o['line'].split('|');site={'original_line':o['line'],'original_start':o['start']}
    if (page,locus) not in locations:site.update(status='NO_COMPLETE_PARAGRAPH');sites.append(site);continue
    p,l=locations[page,locus];selected[reader+'|'+p['id']]=dict(p,reader=reader);site['paragraph_id']=p['id']
    if not l['anchor_eligible']:site.update(status='ANCHOR_LINE_INELIGIBLE');sites.append(site);continue
    hits=[i for i in range(len(l['words'])-len(seed['anchor'])+1) if l['words'][i:i+len(seed['anchor'])]==seed['anchor']]
    if len(hits)!=1:site.update(status='ANCHOR_NOT_UNIQUE',matches=hits);sites.append(site);continue
    i=hits[0];end=i+len(seed['anchor'])
    if end==len(l['words']):site.update(status='NO_FOLLOWING_GROUP');sites.append(site);continue
    div=l['offset']+end;tail=[{'locus':q['locus'],'words':q['words'][max(0,div-q['offset']):],'source_ids':q['source_ids'][max(0,div-q['offset']):],'anchor_eligible':q['anchor_eligible']} for q in p['lines'] if q['offset']+len(q['words'])>div]
    site.update(status='READY',start=i,initial_source_ids=l['source_ids'][i:end],divergence_offset=div,divergence_word=l['words'][end],first_divergence_is_paragraph_final=div==p['groups']-1,complete_raw_tail=tail,excluded_tail_lines=[q['locus'] for q in tail if not q['anchor_eligible']])
    if reader=='ZL3b':assert i==o['start'] and l['words'][end]==o['next']
    sites.append(site)
   result={'reader':reader,'context_id':seed['id'],'anchor':seed['anchor'],'sites':sites,'joins':[]}
   if not all(x['status']=='READY' for x in sites):result['status']='UNTESTABLE'
   elif sites[0]['divergence_word']==sites[1]['divergence_word']:result['status']='NO_WRITTEN_DIVERGENCE'
   else:
    a,b=[selected[reader+'|'+s['paragraph_id']] for s in sites];result['joins']=joins(a,b,sites[0]['divergence_offset'],sites[1]['divergence_offset'],seed['anchor']);result['status']='LITERAL_REJOIN_FOUND' if result['joins'] else 'NO_ELIGIBLE_LITERAL_REJOIN'
   cases.append(result);readercases.append(result)
  summary[reader]={'pairs':len(readercases),'statuses':dict(collections.Counter(c['status'] for c in readercases)),'ready_sites':sum(s['status']=='READY' for c in readercases for s in c['sites']),'ready_sites_with_excluded_tail_lines':sum(bool(s.get('excluded_tail_lines')) for c in readercases for s in c['sites']),'immediately_terminal_divergence_sites':sum(s.get('first_divergence_is_paragraph_final',False) for c in readercases for s in c['sites']),'join_position_pairs':sum(len(c['joins']) for c in readercases)}
 status='BOUNDED_LITERAL_REJOIN_FOUND' if summary['ZL3b']['statuses'].get('LITERAL_REJOIN_FOUND',0) else 'NO_LITERAL_REJOIN_IN_FIXED_13';save('CASES',cases);save('PARAGRAPHS',selected);save('RESULT',{'status':status,'readers':summary,'controls':controls(),'claim_ceiling':'Fixed13anchoredliteralcontinuationcensus;unassessabletextretained,no semanticbranch,wordmeaning,pvalueor928revision.'});print(json.dumps({'status':status,'readers':summary},indent=2))
if __name__=='__main__':
 if '--controls' in sys.argv:print(json.dumps(controls(),indent=2))
 else:main()
