import collections,hashlib,json,re,csv
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];P=R/'experiments/yolo/gdt915_terminal_lr_phrase_transfer';EDS=['ZL3b','IT2a','RF1b']
def write(n,x):(E/'artifacts'/n).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def load():
 lock=json.loads((E/'PREREG_LOCK.json').read_text())
 for p,h in lock['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 allowed=set(json.loads((P/'src/SPEC.json').read_text())['allowed_selectors']);panels={};allp={};dens={}
 for ed in EDS:
  eligible=[];raw=[];den=collections.Counter()
  for phase in ['DISCOVERY','EVALUATION']:
   d=json.loads((P/'artifacts'/f'SOURCE_{phase}_{ed}.json').read_text())
   for row in d['lines']:
    m=row['metadata'];assert m['page'] in allowed and not m['page'].startswith('f84')
    if m['kind']!='P':continue
    den['P_lines']+=1;gs=[dict(zip(d['group_columns'],g)) for g in row['groups']];w=[g['ivtff_group_raw'] for g in gs]
    v={'id':m['page']+'|'+m['locus'],'page':m['page'],'locus':m['locus'],'leaf':int(re.match(r'f(\d+)',m['page'])[1]),'words':w,'source_ids':[g['source_group_id'] for g in gs],'row':int(m['source_row_index']),'paragraph_start':m['paragraph_start'],'paragraph_end':m['paragraph_end']}
    if len(gs)<2:reason='short'
    elif not all(re.fullmatch('[a-z]+',z) for z in w):reason='nonliteral'
    elif not all(int(b['source_group_index'])==int(a['source_group_index'])+1 and a['right_separator']==b['left_separator']=='DEFINITE_SPACE' for a,b in zip(gs,gs[1:])):reason='seam_or_index'
    else:reason='eligible'
    v['eligibility']=reason;den[reason]+=1;raw.append(v)
    if reason=='eligible':eligible.append(v)
  panels[ed]=eligible;allp[ed]=raw;dens[ed]=dict(den)
 return panels,allp,dens

def census(lines):
 buckets=collections.defaultdict(list)
 for l in lines:
  w=l['words']
  for i in range(len(w)-3):
   for j in range(i+3,len(w)):
    a=tuple(w[i:j])
    if len(set(a))<2:continue
    buckets[a].append({'line':l['id'],'leaf':l['leaf'],'start':i,'end':j,'next':w[j],'tail':w[j:]})
 result=[]
 for a,occ in buckets.items():
  leaves={o['leaf'] for o in occ};br=collections.defaultdict(list)
  for o in occ:br[o['next']].append(o)
  if len(leaves)<2 or len(br)<2:continue
  branches=[{'next':b,'occurrences':len(os),'leaves':sorted({o['leaf'] for o in os})} for b,os in sorted(br.items())]
  repeated=sum(len(b['leaves'])>=2 for b in branches)>=2
  result.append({'id':'A'+hashlib.sha256(' '.join(a).encode()).hexdigest()[:12],'anchor':list(a),'length':len(a),'distinct':len(set(a)),'leaves':sorted(leaves),'repeated_branch':repeated,'branches':branches,'occurrences':sorted(occ,key=lambda o:(o['line'],o['start']))})
 result.sort(key=lambda a:(-int(a['repeated_branch']),-a['length'],-a['distinct'],-len(a['leaves']),-len(a['occurrences']),a['anchor']))
 same=collections.defaultdict(list)
 for a in result:same[tuple((o['line'],o['start']) for o in a['occurrences'])].append(a['id'])
 for a in result:a['same_occurrence_start_set']=[x for x in same[tuple((o['line'],o['start']) for o in a['occurrences'])] if x!=a['id']]
 return result

def main():
 panels,raw,dens=load();results={ed:census(panels[ed]) for ed in EDS};write('ELIGIBLE_LINES.json',panels)
 for ed in EDS:write('CANDIDATES_'+ed+'.json',results[ed])
 top=results['ZL3b'][:10];cross=[];context={};maps={ed:{l['id']:l for l in raw[ed]} for ed in EDS}
 for a in top:
  for o in a['occurrences']:
   l=maps['ZL3b'][o['line']];samepage=sorted([x for x in raw['ZL3b'] if x['page']==l['page']],key=lambda x:x['row']);idx=next(i for i,x in enumerate(samepage) if x['id']==l['id'])
   context[l['id']]={'previous_cached_P':samepage[idx-1] if idx else None,'host':l,'next_cached_P':samepage[idx+1] if idx+1<len(samepage) else None}
   for ed in EDS[1:]:
    alt=maps[ed].get(l['id']);seq=a['anchor']+[o['next']];matches=[]
    if alt and alt['eligibility']=='eligible':matches=[i for i in range(len(alt['words'])-len(seq)+1) if alt['words'][i:i+len(seq)]==seq]
    status='ABSENT_LINE' if alt is None else 'INELIGIBLE_LINE' if alt['eligibility']!='eligible' else 'UNIQUE_MATCH' if len(matches)==1 else 'AMBIGUOUS_MATCH' if len(matches)>1 else 'NO_EXACT_MATCH'
    cross.append({'anchor_id':a['id'],'line':l['id'],'primary_start':o['start'],'next':o['next'],'edition':ed,'status':status,'matches':matches,'complete_alternate_line':alt['words'] if alt else None})
 write('TOP_CONTEXTS.json',context);write('ALTERNATE_AUDIT.json',cross)
 summary={'status':'COMPLETE_EXPOSED_CONTEXT_INVENTORY','denominators':dens,'panels':{ed:{'candidate_anchors':len(results[ed]),'repeated_branch_anchors':sum(a['repeated_branch'] for a in results[ed]),'max_anchor_length':max((a['length'] for a in results[ed]),default=0)} for ed in EDS},'top_ids':[a['id'] for a in top],'alternate_statuses':dict(collections.Counter(x['status'] for x in cross)),'meanings':0,'significance_claim':False,'prior_exposure':True,'independent_confirmation_capacity':0}
 write('RESULT.json',summary)
 with (E/'artifacts/CANDIDATE_INDEX.tsv').open('w') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['edition','rank','id','anchor','length','leaf_count','occurrences','branches','repeated_branch','same_occurrence_start_set','row_status'])
  for ed in EDS:
   for i,a in enumerate(results[ed],1):w.writerow([ed,i,a['id'],' '.join(a['anchor']),a['length'],len(a['leaves']),len(a['occurrences']),len(a['branches']),a['repeated_branch'],','.join(a['same_occurrence_start_set']) or 'NONE','recorded'])
 lines=['# Concrete repeated-context worklist','','Top10 ZL3b by the registered ranking. Full inventory and every occurrence are in artifacts/CANDIDATES_*.json. These are overlapping candidates, not independent evidence. Bold marks the identical anchor, not a decoded phrase.','']
 for rank,a in enumerate(top,1):
  lines += [f"## {rank}. {' '.join(a['anchor'])}",'',f"{a['id']}; {len(a['occurrences'])} occurrences; leaves {a['leaves']}; repeated-branch capacity: {a['repeated_branch']}.",'','| Locus | Full written line | IT2a / RF1b |','|---|---|---|']
  for o in a['occurrences']:
   l=maps['ZL3b'][o['line']];w=l['words'];formatted=' '.join(w[:o['start']])+' **'+' '.join(a['anchor'])+'** '+' '.join(w[o['end']:]);statuses=[x['status'] for x in cross if x['anchor_id']==a['id'] and x['line']==o['line'] and x['primary_start']==o['start']]
   lines.append('| '+o['line'].replace('|',' / ')+' | '+formatted.strip()+' | '+' / '.join(statuses)+' |')
  lines+=['','Branches: '+'; '.join(b['next']+' on leaves '+str(b['leaves']) for b in a['branches'])+'.','']
 (E/'CANDIDATE_TABLE.md').write_text('\n'.join(lines).rstrip()+'\n');print(json.dumps(summary))
if __name__=='__main__':main()
