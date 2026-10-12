from pathlib import Path
from collections import Counter,defaultdict
import csv,gzip,hashlib,json,re
import numpy as np
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
    v=p.read_bytes();return json.loads(gzip.decompress(v) if p.suffix=='.gz' else v)
def save(p,x):
    raw=(json.dumps(x,indent=2,sort_keys=True)+'\n').encode();p.write_bytes(gzip.compress(raw,mtime=0) if p.suffix=='.gz' else raw)
def leaf(r):return int(re.match(r'f(\d+)',r['page'])[1])
def optimize(alpha,weights,supports):
    mandatory={m.bit_length()-1 for m in supports if m.bit_count()==1};free=[i for i in range(len(alpha)) if i not in mandatory];required=sum(1<<i for i in mandatory);size=1<<len(free);bad=np.zeros(size,dtype=np.bool_);mass=np.zeros(size,dtype=np.int64);count=np.zeros(size,dtype=np.int16)
    for m in supports:
        if not m&required:
            small=sum(1<<j for j,i in enumerate(free) if m>>i&1);bad[small]=True
    for j,i in enumerate(free):
        step=1<<j;view=bad.reshape(-1,2*step);view[:,step:] |= view[:,:step];mass[step:2*step]=mass[:step]+weights[i];count[step:2*step]=count[:step]+1
    feasible=~bad;assert feasible[0];maxmass=int(mass[feasible].max());maxcount=int(count[feasible].max());mm=np.flatnonzero(feasible&(mass==maxmass));mc=np.flatnonzero(feasible&(count==maxcount))
    def witness(indices):
        mask=int(indices[0]);units=[alpha[i] for j,i in enumerate(free) if mask>>j&1];return {'free_mask':mask,'null_units':units,'erased_tokens':int(mass[mask]),'null_types':int(count[mask]),'ties':len(indices)}
    return {'mandatory_nonnull_units':[alpha[i] for i in sorted(mandatory)],'free_units':[alpha[i] for i in free],'candidate_subsets':size,'feasible_subsets':int(feasible.sum()),'max_mass':witness(mm),'max_types':witness(mc)}
def main():
    for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};results={}
    for reader,rows in sorted(data.items()):
        original=defaultdict(list)
        for r in rows:
            assert r['page'] in allow and not r['page'].startswith('f84') and r['page'] not in ['f1r','f116v'];assert r['kind']=='P' and r['left_separator']==r['right_separator']=='DEFINITE_SPACE';assert ''.join(r['units'])==r['ivtff_group_raw'];original[tuple(r['units'])].append(r)
        alpha=sorted({u for w in original for u in w});assert len(alpha)==22;ix={u:i for i,u in enumerate(alpha)}
        for name in ['FULL','GE2']:
            occ={w:rr for w,rr in original.items() if name=='FULL' or len({leaf(r) for r in rr})>=2};groups=[r for rr in occ.values() for r in rr];weights=Counter(u for r in groups for u in r['units']);supports=defaultdict(list)
            for r in groups:supports[sum(1<<ix[u] for u in set(r['units']))].append(r)
            opt=optimize(alpha,[weights[u] for u in alpha],set(supports));total=sum(weights.values());assert total<2**60
            for field in ['max_mass','max_types']:
                w=opt[field];N=set(w['null_units']);hist=Counter();affected=0;erased=0
                for r in groups:
                    left=sum(u not in N for u in r['units']);assert left>0;hist[left]+=1;affected+=left<len(r['units']);erased+=len(r['units'])-left
                assert erased==w['erased_tokens'];w.update(residual_length_histogram={str(k):v for k,v in sorted(hist.items())},affected_groups=affected,erased_fraction=[erased,total])
            key=reader+'_'+name;certificate={'alphabet':alpha,'token_weights':{u:weights[u] for u in alpha},'word_supports':[{'mask':m,'units':[u for u in alpha if m>>ix[u]&1],'groups':len(rr),'physical_leaves':sorted({leaf(r) for r in rr}),'first_row':rr[0]} for m,rr in sorted(supports.items())],'singleton_support_words':[{'units':list(w),'count':len(rr),'physical_leaves':sorted({leaf(r) for r in rr}),'first_row':rr[0]} for w,rr in sorted(occ.items()) if len(set(w))==1]};save(B/f'artifacts/CERTIFICATE_{key}.json.gz',certificate)
            out={'groups':len(groups),'types':len(occ),'unit_tokens':total,'distinct_supports':len(supports),**opt};results[key]=out;print(json.dumps({'panel':key,'mandatory':out['mandatory_nonnull_units'],'free_subsets':out['candidate_subsets'],'feasible':out['feasible_subsets'],'max_mass':out['max_mass']['erased_fraction'],'max_mass_units':out['max_mass']['null_units'],'max_types':out['max_types']['null_types']}),flush=True)
    old=read(R/'experiments/yolo/gdt1267_general_ud_two_sided_closure/artifacts/RESULT.json');rf=old['readers']['RF1b'];byid={r['id']:r for r in data['RF1b']};premises={}
    for u in ['k','e','s']:
        record=rf['singletons'][u];assert record['rule']=='WHOLE' and len(record['premises'])==1;p=record['premises'][0];assert p['units']==[u] and p['frequency']==len(p['source_ids']);rr=[byid[i] for i in p['source_ids']];assert all(r['units']==[u] for r in rr);premises[u]=rr
    ww=rf['whole_witness_occurrences'];assert ww and all(byid[r['id']]==r and r['units']==['k','e','e','e','e','s'] for r in ww);assert rf['forced_parse']==['k','e','e','e','e','s'];assert len(old['source_results'])==5 and all(r['supporting_tokens']==0 for r in old['source_results'].values())
    cor={'status':'RF_NULLABLE_OTHER_ENTRY_SOURCE_EXCLUSION_RETAINED','reader':'RF1b','whole_singleton_premises':premises,'whole_fourth_power_witnesses':ww,'prior_source_counts':old['source_results'],'proof':'Complete whole k/e/s require their code-entry expansions nonempty; freeUD fixes keeees, so XU^4Y remains with allpiecesnonempty even if otherentries expandempty.','new_source_census':False,'scope':'RF fixedsource/model conjunction only, rarepremises retained. Parsed-entry nulls are not globalworking-sign nulls; no transfer of numeric null-mass envelope.'};save(B/'artifacts/RF_NULLABLE_COROLLARY.json',cor)
    save(B/'artifacts/RESULT.json',{'status':'EXACT_FIXED_NULL_ERASURE_ENVELOPES','panels':results,'scope':'Fixed global working-sign deletion with nonempty residual per complete group; no identified nulls, values, historicalfit or language.'})
if __name__=='__main__':main()
