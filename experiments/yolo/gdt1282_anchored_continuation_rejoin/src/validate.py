"""Independent direct enumeration and raw-source checks for fixedrejoincases."""
import collections,hashlib,json,re
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def main():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 seeds=json.loads((R/'experiments/yolo/gdt926_repeated_context_continuation_atlas/artifacts/CANDIDATES_ZL3b.json').read_text());panels=json.loads((R/'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json').read_text());cases=json.loads((B/'artifacts/CASES.json').read_text());selected=json.loads((B/'artifacts/PARAGRAPHS.json').read_text());result=json.loads((B/'artifacts/RESULT.json').read_text());raw={}
 for reader in panels:
  for phase in ['DISCOVERY','EVALUATION']:
   for line in json.loads((R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{reader}.json').read_text())['lines']:raw[reader,line['metadata']['page'],line['metadata']['locus']]=line
 # Verify every selected fullparagraph, rawIDs, flags, eligibility and offsets.
 for key,p in selected.items():
  reader=p['reader'];off=0;nums=[]
  assert not p['page'].startswith('f84') and p['page']!='f116v'
  for l in p['lines']:
   source=raw[reader,p['page'],l['locus']];m=source['metadata'];gs=source['groups'];words=[g[2] for g in gs];ids=[g[0] for g in gs]
   eligible=len(gs)>=2 and all(re.fullmatch('[a-z]+',w) for w in words) and all(int(b[1])==int(a[1])+1 and a[4]==b[3]=='DEFINITE_SPACE' for a,b in zip(gs,gs[1:]))
   assert l['words']==words and l['source_ids']==ids and l['anchor_eligible']==bool(eligible) and l['offset']==off and l['row']==int(m['source_row_index']);assert l['start']==(m['paragraph_start']=='1') and l['end']==(m['paragraph_end']=='1');off+=len(words);nums.append(int(l['locus'].rsplit('.',1)[1]))
  assert off==p['groups'] and p['lines'][0]['start'] and p['lines'][-1]['end'] and all(y==x+1 for x,y in zip(nums,nums[1:]))
 expected_summary={};tested=0;ready=0;lookup={(c['reader'],c['context_id']):c for c in cases};assert len(lookup)==39
 for reader,paras in panels.items():
  byloc={(p['page'],l['locus']):(p,l) for p in paras for l in p['lines']};rs=[]
  for seed in seeds:
   c=lookup[reader,seed['id']];assert c['anchor']==seed['anchor'];sites=[]
   for old,s in zip(seed['occurrences'],c['sites']):
    page,locus=old['line'].split('|');assert s['original_line']==old['line'] and s['original_start']==old['start']
    if (page,locus) not in byloc:assert s['status']=='NO_COMPLETE_PARAGRAPH';sites.append(None);continue
    p,l=byloc[page,locus];assert s['paragraph_id']==p['id'] and selected[reader+'|'+p['id']]==dict(p,reader=reader)
    if not l['anchor_eligible']:assert s['status']=='ANCHOR_LINE_INELIGIBLE';sites.append(None);continue
    hits=[i for i in range(len(l['words'])-2) if l['words'][i:i+3]==seed['anchor']]
    if len(hits)!=1:assert s['status']=='ANCHOR_NOT_UNIQUE' and s['matches']==hits;sites.append(None);continue
    start=hits[0];end=start+3
    if end==len(l['words']):assert s['status']=='NO_FOLLOWING_GROUP';sites.append(None);continue
    div=l['offset']+end;assert s['status']=='READY' and s['start']==start and s['initial_source_ids']==l['source_ids'][start:end] and s['divergence_offset']==div and s['divergence_word']==l['words'][end]
    assert s['first_divergence_is_paragraph_final']==(div==p['groups']-1)
    tail=[]
    for q in p['lines']:
     keep=[i for i in range(len(q['words'])) if q['offset']+i>=div]
     if keep:tail.append({'locus':q['locus'],'words':[q['words'][i] for i in keep],'source_ids':[q['source_ids'][i] for i in keep],'anchor_eligible':q['anchor_eligible']})
    assert s['complete_raw_tail']==tail and s['excluded_tail_lines']==[q['locus'] for q in tail if not q['anchor_eligible']]
    sites.append((p,div));ready+=1
   expected=[]
   if any(s is None for s in sites):status='UNTESTABLE'
   elif c['sites'][0]['divergence_word']==c['sites'][1]['divergence_word']:status='NO_WRITTEN_DIVERGENCE'
   else:
    tested+=1;(pa,da),(pb,db)=sites
    for la in pa['lines']:
     if not la['anchor_eligible']:continue
     for ia in range(len(la['words'])-2):
      oa=la['offset']+ia;wa=la['words'][ia:ia+3]
      if oa<=da or len(set(wa))<2:continue
      for lb in pb['lines']:
       if not lb['anchor_eligible']:continue
       for ib in range(len(lb['words'])-2):
        ob=lb['offset']+ib
        if ob<=db or lb['words'][ib:ib+3]!=wa:continue
        common=[]
        for x,y in zip(la['words'][ia:],lb['words'][ib:]):
         if x!=y:break
         common.append(x)
        n=len(common);expected.append({'a_offset':oa,'b_offset':ob,'a_locus':la['locus'],'b_locus':lb['locus'],'a_start':ia,'b_start':ib,'three_words':wa,'right_extended_words':common,'a_source_ids':la['source_ids'][ia:ia+n],'b_source_ids':lb['source_ids'][ib:ib+n],'a_branch_groups':oa-da,'b_branch_groups':ob-db,'same_as_initial':wa==seed['anchor'],'a_branch_excluded_lines':[l['locus'] for l in pa['lines'] if not l['anchor_eligible'] and l['offset']<oa and l['offset']+len(l['words'])>da],'b_branch_excluded_lines':[l['locus'] for l in pb['lines'] if not l['anchor_eligible'] and l['offset']<ob and l['offset']+len(l['words'])>db]})
    expected.sort(key=lambda x:(x['a_branch_groups']+x['b_branch_groups'],max(x['a_branch_groups'],x['b_branch_groups']),x['a_offset'],x['b_offset'],x['three_words']));status='LITERAL_REJOIN_FOUND' if expected else 'NO_ELIGIBLE_LITERAL_REJOIN'
   assert c['status']==status and c['joins']==expected;rs.append(c)
  expected_summary[reader]={'pairs':len(rs),'statuses':dict(collections.Counter(c['status'] for c in rs)),'ready_sites':sum(s['status']=='READY' for c in rs for s in c['sites']),'ready_sites_with_excluded_tail_lines':sum(bool(s.get('excluded_tail_lines')) for c in rs for s in c['sites']),'immediately_terminal_divergence_sites':sum(s.get('first_divergence_is_paragraph_final',False) for c in rs for s in c['sites']),'join_position_pairs':sum(len(c['joins']) for c in rs)}
 assert result['readers']==expected_summary
 assert result['status']==('BOUNDED_LITERAL_REJOIN_FOUND' if expected_summary['ZL3b']['statuses'].get('LITERAL_REJOIN_FOUND') else 'NO_LITERAL_REJOIN_IN_FIXED_13')
 assert result['controls']['cases']==6 and not result['controls']['old928_counterexample_qualifies'] and result['controls']['new_counterexample_joins']
 out={'status':'PASS','context_reader_pairs':len(cases),'assessable_divergent_pairs':tested,'ready_sites':ready,'selected_full_paragraphs':len(selected),'scope':'Directnestedjoinenumerationandrawfullparagraph/source/eligibilitychecks;no independentpalaeographyorsemanticverification.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
