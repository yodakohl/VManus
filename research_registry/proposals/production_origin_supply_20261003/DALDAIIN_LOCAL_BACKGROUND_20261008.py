"""Descriptive selected-page windows. No null probability or meaning test."""
import csv,json,hashlib
from pathlib import Path
BASE=Path('research_registry/proposals/production_origin_supply_20261003')
paths=[BASE/'F45R_MANUAL_TEXT_20261008.tsv',BASE/'F89R1_MANUAL_TEXT_20261008.tsv']
result=[]
for reader in ['ZL3b','IT2a','RF1b']:
    windows=[]
    for path in paths:
        rows=[x for x in csv.DictReader(path.open(),delimiter='\t') if x['edition']==reader and x['kind']=='P']
        rows.sort(key=lambda x:(int(x['locus'].rsplit('.',1)[1]),int(x['source_group_index'])))
        words=[x['ivtff_group_raw'] for x in rows]
        page=rows[0]['locus'].split('.')[0]
        assert all(x['locus'].split('.')[0]==page for x in rows)
        targets=[i for i,w in enumerate(words) if w=='daldaiin'];assert len(targets)==1
        i=targets[0];before=words[i-5:i];after=words[i+1:i+6];windows.append(set(before))
        prior_hits=[j for j in range(5,len(words)) if 'dal' in words[j-5:j]]
        following_hits=[j for j in range(len(words)-5) if 'dal' in words[j+1:j+6]]
        row={'reader':reader,'page':page,'prose_groups':len(words),'dal_count':words.count('dal'),'daldaiin_index0':i,'prior5':before,'following_up_to5':after,'full_prior_window':i>=5,'full_following_window':i+5<len(words),'prior_dal_distances':[i-j for j in range(i) if words[j]=='dal'],'following_dal_distances':[j-i for j in range(i+1,len(words)) if words[j]=='dal'],'background_prior':{'eligible':len(words)-5,'with_dal':len(prior_hits),'anchor_indices0':prior_hits},'background_following':{'eligible':len(words)-5,'with_dal':len(following_hits),'anchor_indices0':following_hits}}
        assert 'dal' in before
        # Direct independent recount by marking all anchors following each dal occurrence.
        marked={j for k,w in enumerate(words) if w=='dal' for j in range(k+1,min(k+6,len(words))) if j>=5}
        assert marked==set(prior_hits)
        result.append(row)
    common=sorted(set.intersection(*windows))
    for row in result[-2:]:row['common_prior_words_across_two_targets']=common
inputs=paths+[BASE/'DALDAIIN_LOCAL_BACKGROUND_PLAN_20261008.json',Path(__file__)]
out={'status':'DESCRIPTIVE_SELECTED_PAGE_BACKGROUND_ONLY','rows':result,'input_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},'limitations':'Five/page/target postselected. Anchors strongly overlap; no probability, independent repetitions, same-paragraph assumption, exact source-copy or meaning. Raw uncertain boundaries retained as stored.'}
(BASE/'DALDAIIN_LOCAL_BACKGROUND_RESULT_20261008.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
for row in result:
    print(json.dumps({k:v for k,v in row.items() if k not in ['background_prior','background_following']}|{'background_prior':{k:v for k,v in row['background_prior'].items() if k!='anchor_indices0'},'background_following':{k:v for k,v in row['background_following'].items() if k!='anchor_indices0'}},ensure_ascii=False))
