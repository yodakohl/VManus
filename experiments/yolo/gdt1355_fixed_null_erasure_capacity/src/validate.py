from pathlib import Path
from collections import Counter,defaultdict
import csv,gzip,hashlib,itertools,json,re
B=Path(__file__).resolve().parents[1];R=B.parents[2]
PAT=re.compile('ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]')
def read(p):
    v=p.read_bytes();return json.loads(gzip.decompress(v) if p.suffix=='.gz' else v)
def direct(alpha,weights,supportsets):
    mandatory=set().union(*(s for s in supportsets if len(s)==1));free=[u for u in alpha if u not in mandatory];idx={u:i for i,u in enumerate(free)};constraints=[sum(1<<idx[u] for u in s) for s in supportsets if not s&mandatory];oldmask=mass=card=feasible=0;bestmass=bestcard=-1;mties=cties=0;mmask=cmask=0;mw=mc=cw=cc=0
    for serial in range(1<<len(free)):
        mask=serial^(serial>>1)
        if serial:
            changed=mask^oldmask;i=changed.bit_length()-1;delta=1 if mask&changed else -1;mass+=delta*weights[free[i]];card+=delta
        oldmask=mask
        if any(mask&c==c for c in constraints):continue
        feasible+=1
        if mass>bestmass:bestmass=mass;mties=1;mmask=mask;mw=mass;mc=card
        elif mass==bestmass:
            mties+=1
            if mask<mmask:mmask=mask;mw=mass;mc=card
        if card>bestcard:bestcard=card;cties=1;cmask=mask;cw=mass;cc=card
        elif card==bestcard:
            cties+=1
            if mask<cmask:cmask=mask;cw=mass;cc=card
    def entry(mask,m,c,t):return {'free_mask':mask,'null_units':[u for i,u in enumerate(free) if mask>>i&1],'erased_tokens':m,'null_types':c,'ties':t}
    return {'mandatory_nonnull_units':sorted(mandatory),'free_units':free,'candidate_subsets':1<<len(free),'feasible_subsets':feasible,'max_mass':entry(mmask,mw,mc,mties),'max_types':entry(cmask,cw,cc,cties)}
def main():
    for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');result=read(B/'artifacts/RESULT.json');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};maskchecks=0;receipts={}
    for reader,rows in data.items():
        byword=defaultdict(list)
        for r in rows:
            assert r['page'] in allow and not r['page'].startswith('f84') and r['page'] not in ['f1r','f116v'];assert r['kind']=='P' and r['left_separator']==r['right_separator']=='DEFINITE_SPACE';parts=PAT.findall(r['ivtff_group_raw']);assert parts==r['units'] and ''.join(parts)==r['ivtff_group_raw'];byword[tuple(parts)].append(r)
        alpha=sorted({u for w in byword for u in w});assert len(alpha)==22;ix={u:i for i,u in enumerate(alpha)}
        for panel in ['FULL','GE2']:
            occ={w:rr for w,rr in byword.items() if panel=='FULL' or len({re.match(r'f\d+',r['page'])[0] for r in rr})>=2};groups=[r for r in rows if tuple(r['units']) in occ];support=defaultdict(list);weights=Counter(u for r in groups for u in r['units'])
            for r in groups:support[frozenset(r['units'])].append(r)
            key=reader+'_'+panel;r=result['panels'][key];cert=read(B/f'artifacts/CERTIFICATE_{key}.json.gz');assert cert['alphabet']==alpha and cert['token_weights']=={u:weights[u] for u in alpha};assert r['groups']==len(groups) and r['types']==len(occ) and r['unit_tokens']==sum(weights.values()) and r['distinct_supports']==len(support)
            seen=set()
            for s in cert['word_supports']:
                ss=frozenset(s['units']);assert ss not in seen;seen.add(ss);rr=support[ss];assert s['mask']==sum(1<<ix[u] for u in ss) and s['groups']==len(rr) and s['first_row']==rr[0];assert s['physical_leaves']==sorted({int(re.match(r'f(\d+)',q['page'])[1]) for q in rr})
            assert seen==set(support);expected=[{'units':list(w),'count':len(rr),'physical_leaves':sorted({int(re.match(r'f(\d+)',q['page'])[1]) for q in rr}),'first_row':rr[0]} for w,rr in sorted(occ.items()) if len(set(w))==1];assert expected==cert['singleton_support_words']
            exact=direct(alpha,weights,list(support));maskchecks+=exact['candidate_subsets']
            for field in ['mandatory_nonnull_units','free_units','candidate_subsets','feasible_subsets']:assert r[field]==exact[field]
            for objective in ['max_mass','max_types']:
                for field,value in exact[objective].items():assert r[objective][field]==value,(key,objective,field)
                N=set(r[objective]['null_units']);hist=Counter();removed=affected=0
                for word,rr in occ.items():
                    residual=tuple(u for u in word if u not in N);assert residual;hist[len(residual)]+=len(rr);removed+=(len(word)-len(residual))*len(rr);affected+=len(rr)*(residual!=word)
                assert r[objective]['erased_tokens']==removed and r[objective]['erased_fraction']==[removed,sum(weights.values())] and r[objective]['affected_groups']==affected;assert r[objective]['residual_length_histogram']=={str(k):v for k,v in sorted(hist.items())}
            receipts[key]={'exact_candidates_checked':exact['candidate_subsets'],'max_mass':r['max_mass']['erased_fraction'],'max_types':r['max_types']['null_types']}
    cor=read(B/'artifacts/RF_NULLABLE_COROLLARY.json');parent=read(R/'experiments/yolo/gdt1267_general_ud_two_sided_closure/artifacts/RESULT.json');rows=data['RF1b'];byid={r['id']:r for r in rows}
    for u in ['k','e','s']:
        old=parent['readers']['RF1b']['singletons'][u];assert old['rule']=='WHOLE';ids=old['premises'][0]['source_ids'];assert [r['id'] for r in cor['whole_singleton_premises'][u]]==ids
        for row in cor['whole_singleton_premises'][u]:assert row==byid[row['id']] and row['units']==[u]
    assert cor['whole_fourth_power_witnesses']==parent['readers']['RF1b']['whole_witness_occurrences'];assert all(r==byid[r['id']] and r['units']==['k','e','e','e','e','s'] for r in cor['whole_fourth_power_witnesses']);assert cor['prior_source_counts']==parent['source_results'];assert len(cor['prior_source_counts'])==5 and all(s['supporting_tokens']==0 for s in cor['prior_source_counts'].values());assert cor['new_source_census'] is False and cor['status']=='RF_NULLABLE_OTHER_ENTRY_SOURCE_EXCLUSION_RETAINED'
    # Independent small fixture scores; array/direct comparison was frozen before target.
    assert direct(['a'],{'a':3},[frozenset('aaa')])['max_mass']['erased_tokens']==0
    t=direct(['a','b','c'],{'a':3,'b':5,'c':7},[frozenset('ab')]);assert t['max_mass']['null_units']==['b','c'] and t['max_types']['null_units']==['a','c']
    assert result['status']=='EXACT_FIXED_NULL_ERASURE_ENVELOPES';out={'status':'PASS','direct_candidate_checks':maskchecks,'panels':receipts,'RF_nullable_corollary':'OLD_PREMISES_MATCH_NO_NEW_SOURCE_CENSUS','scope':'Exact nonempty-residual capacity and narrowly bound RF logical corollary; no null identity, meaning or historical claim.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
