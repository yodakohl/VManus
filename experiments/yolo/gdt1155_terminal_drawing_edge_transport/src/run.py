"""Frozen GDT1155 ending channel; whole-form matches, no meanings."""
import collections,csv,hashlib,json,math,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
BASE='experiments/yolo/gdt915_terminal_lr_phrase_transfer'
INVENTORY='experiments/yolo/gdt800_terminal_b2_b3_line_final_bridge/artifacts/GDT800_155_MATCHED_STEM_SUMMARY.tsv'

def dump(n,x):(A/n).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def mean(x):return sum(x)/len(x) if x else None

def extract(reader,lines,forms):
 pages=collections.defaultdict(list);events=[];excluded=[];hosts={}
 for line in lines:
  m=line['metadata']
  if m['kind']=='P':pages[m['page']].append(line)
 for page,ls in sorted(pages.items()):
  ls.sort(key=lambda x:int(x['metadata']['source_row_index']))
  for li,line in enumerate(ls):
   m=line['metadata'];gs=line['groups'];n=int(m['source_group_count']);assert len(gs)==n
   assert [int(g[1]) for g in gs]==list(range(1,n+1))
   assert gs[0][3]=='LINE_START' and gs[-1][4]=='LINE_END'
   nxt=ls[li+1]['metadata'] if li+1<len(ls) else None
   for i,g in enumerate(gs):
    sid,ix,w,left,right=g
    if w not in forms:continue
    stem,ending=forms[w];reasons=[]
    if n<2:reasons.append('HOST_FEWER_THAN_TWO_GROUPS')
    if left=='LINE_START':
     if i!=0:reasons.append('LEFT_START_NOT_FIRST')
    elif left=='DEFINITE_SPACE':
     if i==0 or int(gs[i-1][1])+1!=int(ix) or gs[i-1][4]!=left:reasons.append('LEFT_JOIN_MISMATCH')
    else:reasons.append('LEFT_BOUNDARY_'+left)
    boundary=None
    if right in ['DEFINITE_SPACE','DRAWING_INTERRUPTION']:
     boundary='SPACE' if right=='DEFINITE_SPACE' else 'DRAWING'
     if i+1>=n or int(gs[i+1][1])!=int(ix)+1 or gs[i+1][3]!=right:reasons.append('RIGHT_JOIN_MISMATCH')
    elif right=='LINE_END':
     boundary='END'
     if int(ix)!=n:reasons.append('END_NOT_FINAL_GROUP')
     if nxt is None:reasons.append('NO_NEXT_PROSE_LOCUS')
     else:
      here=m['locus'].rsplit('.',1)[-1];there=nxt['locus'].rsplit('.',1)[-1]
      if not here.isdigit() or not there.isdigit() or int(there)!=int(here)+1:reasons.append('NEXT_PROSE_NOT_CONSECUTIVE_NUMERIC')
      if int(nxt['source_row_index'])<=int(m['source_row_index']):reasons.append('NEXT_PROSE_NOT_HIGHER_ROW')
      if not nxt['code'].startswith(('+','*')):reasons.append('NEXT_PROSE_NOT_BELOW_CODE')
    else:reasons.append('RIGHT_BOUNDARY_'+right)
    record={'reader':reader,'source_id':sid,'page':page,'leaf':int(re.match(r'f(\d+)',page)[1]),'locus':m['locus'],'source_row_index':int(m['source_row_index']),'source_group_index':int(ix),'source_group_count':n,'word':w,'stem':stem,'ending':ending,'m':int(ending=='m'),'left_separator':left,'right_separator':right,'boundary':boundary,'stratum':[m[k] for k in ['section','currier','hand']],'next_prose_locus':nxt['locus'] if nxt else None,'next_prose_code':nxt['code'] if nxt else None,'reasons':reasons}
    if reasons:excluded.append(record)
    else:
     events.append(record)
     if boundary=='DRAWING':hosts[m['locus']]=line
 return events,excluded,hosts

def counts(events):
 total=collections.defaultdict(lambda:[0,0]);leaves=collections.defaultdict(lambda:collections.defaultdict(lambda:[0,0]))
 for e in events:
  if e['boundary']=='DRAWING':continue
  b=e['boundary'];s=tuple(e['stratum']);keys=[(b,),(b,s),(b,s,e['stem'])]
  for k in keys:
   total[k][0]+=1;total[k][1]+=e['m'];leaves[e['leaf']][k][0]+=1;leaves[e['leaf']][k][1]+=e['m']
 return total,leaves

def predict(e,b,total,leaves):
 s=tuple(e['stratum']);leaf=e['leaf']
 def cnt(k):return tuple(a-z for a,z in zip(total.get(k,(0,0)),leaves.get(leaf,{}).get(k,(0,0))))
 ng,mg=cnt((b,));ns,ms=cnt((b,s));nt,mt=cnt((b,s,e['stem']))
 g=(mg+.5)/(ng+1);ss=(ms+20*g)/(ns+20);p=(mt+10*ss)/(nt+10)
 return {'N_global':ng,'M_global':mg,'g':g,'N_stratum':ns,'M_stratum':ms,'s':ss,'N_stem_stratum':nt,'M_stem_stratum':mt,'p':p}

def aggregate(predictions):
 result={};leafrows={}
 for b in ['DRAWING','END','SPACE']:
  es=[e for e in predictions if e['boundary']==b];by=collections.defaultdict(list)
  for e in es:by[e['leaf']].append(e)
  rows=[{'leaf':leaf,'events':len(xs),'m':sum(x['m'] for x in xs),'l':sum(1-x['m'] for x in xs),'mean_gain_bits':mean([x['gain_bits'] for x in xs]),'losses':sum(x['gain_bits']<0 for x in xs),'source_ids':[x['source_id'] for x in xs]} for leaf,xs in sorted(by.items())]
  leafrows[b]=rows;result[b]={'events':len(es),'leaves':len(rows),'m':sum(e['m'] for e in es),'l':sum(1-e['m'] for e in es),'stem_count':len({e['stem'] for e in es}),'stems':sorted({e['stem'] for e in es}),'strata':sorted({tuple(e['stratum']) for e in es}),'micro_gain_bits':mean([e['gain_bits'] for e in es]),'equal_leaf_gain_bits':mean([x['mean_gain_bits'] for x in rows]),'positive_leaves':sum(x['mean_gain_bits']>0 for x in rows),'positive_leaf_fraction':sum(x['mean_gain_bits']>0 for x in rows)/len(rows) if rows else None,'losses':sum(e['gain_bits']<0 for e in es),'zero_gains':sum(e['gain_bits']==0 for e in es)}
 return result,leafrows

def main():
 pins=json.loads((E/'PREREG_LOCK.json').read_text())['files']
 for f,h in pins.items():assert hashlib.sha256((R/f).read_bytes()).hexdigest()==h,f
 spec=json.loads((R/BASE/'src/SPEC.json').read_text());allow=set(spec['allowed_selectors'])
 forms={}
 with (R/INVENTORY).open() as f:
  for row in csv.DictReader(f,delimiter='\t'):
   stem=row['stem'];assert stem and re.fullmatch('[a-z]+',stem)
   for ending,column in [('l','l_surface'),('m','m_surface')]:
    assert row[column]==stem+ending and row[column] not in forms;forms[row[column]]=(stem,ending)
 assert len(forms)==310
 events={};excluded={};hosts={};predictions={};leafs={};summary={}
 for reader in sorted(spec['editions']):
  lines=[]
  for phase in ['DISCOVERY','EVALUATION']:
   src=json.loads((R/BASE/'artifacts'/f'SOURCE_{phase}_{reader}.json').read_text());assert src['group_columns']==spec['group_columns']
   for line in src['lines']:
    page=line['metadata']['page'];assert page in allow and not page.startswith('f84') and page!='f116v'
   lines.extend(src['lines'])
  assert len({x['metadata']['locus'] for x in lines})==len(lines)
  events[reader],excluded[reader],hosts[reader]=extract(reader,lines,forms)
  total,by_leaf=counts(events[reader]);predictions[reader]=[]
  for e in events[reader]:
   mend=predict(e,'END',total,by_leaf);mspace=predict(e,'SPACE',total,by_leaf)
   pe=mend['p'] if e['m'] else 1-mend['p'];ps=mspace['p'] if e['m'] else 1-mspace['p']
   predictions[reader].append({**e,'model_END':mend,'model_SPACE':mspace,'prob_observed_END':pe,'prob_observed_SPACE':ps,'gain_bits':math.log2(pe/ps)})
  ag,leafs[reader]=aggregate(predictions[reader]);d=ag['DRAWING'];en=ag['END'];capacity=d['events']>=20 and d['leaves']>=5 and d['m']>0 and d['l']>0
  supported=capacity and d['equal_leaf_gain_bits']>=.01 and d['positive_leaf_fraction']>=.6 and en['equal_leaf_gain_bits'] is not None and en['equal_leaf_gain_bits']>0
  summary[reader]={'status':'SUPPORTED' if supported else 'NOT_SUPPORTED' if capacity else 'NO_CAPACITY','capacity':capacity,'exact_form_hits':len(events[reader])+len(excluded[reader]),'accepted':len(events[reader]),'excluded':len(excluded[reader]),'exclusion_reason_counts':dict(collections.Counter(r for e in excluded[reader] for r in e['reasons'])),'boundaries':ag}
 support=sum(summary[r]['status']=='SUPPORTED' for r in ['ZL3b','IT2a'])
 status='READER_CONCORDANT_PREDICTIVE_TRANSFER' if support==2 else 'READER_SPECIFIC_PREDICTIVE_TRANSFER' if support==1 else 'ALL_NO_CAPACITY' if all(summary[r]['status']=='NO_CAPACITY' for r in ['ZL3b','IT2a']) else 'NO_SUPPORTED_TRANSFER'
 result={'status':status,'readers':summary,'frozen_stems':155,'frozen_whole_forms':310,'pins_verified':True,'meanings':0,'independent_confirmation':False,'significance_claim':False,'l_m_equivalence_claim':False,'physical_edge_claim':False,'causal_production_order_claim':False,'relation_packet_score_ready':False}
 for name,obj in [('EVENTS.json',events),('EXCLUDED_HITS.json',excluded),('PREDICTIONS.json',predictions),('LEAF_GAINS.json',leafs),('DRAWING_HOSTS.json',hosts),('RESULT.json',result)]:dump(name,obj)
 text=['# GDT1155 all drawing-event predictions','','END means the registered below-locus transition reference; not a proved physical right edge. Models exclude the entire target leaf and all drawing events.','','|Reader|Source group|Form|Leaf|END p(m)|SPACE p(m)|Observed gain bits|','|---|---|---|---:|---:|---:|---:|']
 for reader,ps in predictions.items():
  for e in ps:
   if e['boundary']=='DRAWING':text.append(f"|{reader}|{e['source_id'].replace('|',' / ')}|{e['word']}|{e['leaf']}|{e['model_END']['p']:.9f}|{e['model_SPACE']['p']:.9f}|{e['gain_bits']:.9f}|")
 (E/'CANDIDATE_TABLE.md').write_text('\n'.join(text)+'\n')
 text=['# GDT1155 complete target host loci','','All raw groups and separator labels retained; target words remain untranslated. Source-locus records are not an independent physical-line map.']
 for reader,hs in hosts.items():
  for locus,line in hs.items():
   text.extend(['',f'## {reader} {locus}','','Metadata: `'+json.dumps(line['metadata'],sort_keys=True)+'`','','|Source group|Raw group|Left separator|Right separator|','|---|---|---|---|'])
   for g in line['groups']:text.append('|'+ '|'.join([g[0].replace('|',' / '),g[2].replace('|','&#124;'),g[3],g[4]])+'|')
 (E/'WHOLE_CONTEXTS.md').write_text('\n'.join(text)+'\n')
 print(json.dumps({'status':status,'readers':{r:{'status':v['status'],'drawing':v['boundaries']['DRAWING'],'end_calibration':v['boundaries']['END']['equal_leaf_gain_bits'],'space_calibration':v['boundaries']['SPACE']['equal_leaf_gain_bits']} for r,v in summary.items()}},indent=2))
if __name__=='__main__':main()
