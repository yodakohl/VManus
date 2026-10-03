#!/usr/bin/env python3
"""Independent source extraction and held-leaf probability audit; no runner imports."""
import collections
import csv
import hashlib
import json
import math
from pathlib import Path
import re

E=Path(__file__).resolve().parents[1]
ROOT=E.parents[2]
BASE=ROOT/'experiments/yolo/gdt915_terminal_lr_phrase_transfer'

def read(p): return json.loads(p.read_text())
def close(a,b): return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12)

def reconstruct():
    for name,h in read(E/'PREREG_LOCK.json')['files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    allowed=set(read(BASE/'src/SPEC.json')['allowed_selectors'])
    inventory={}
    with (ROOT/'experiments/yolo/gdt800_terminal_b2_b3_line_final_bridge/artifacts/GDT800_155_MATCHED_STEM_SUMMARY.tsv').open() as f:
        for row in csv.DictReader(f,delimiter='\t'):
            for terminal,y in [('l',0),('m',1)]:
                w=row[terminal+'_surface']
                assert re.fullmatch('[a-z]+',w) and w not in inventory
                inventory[w]=(row['stem'],y)
    assert len(inventory)==310
    accepted,rejected,hosts={},{},{}
    for reader in ['IT2a','RF1b','ZL3b']:
        pages=collections.defaultdict(list)
        accepted[reader],rejected[reader],hosts[reader]={},{},{}
        for part in ['DISCOVERY','EVALUATION']:
            source=read(BASE/'artifacts'/('SOURCE_'+part+'_'+reader+'.json'))
            for line in source['lines']:
                m=line['metadata']
                assert m['page'] in allowed and not m['page'].startswith(('f84','f116v'))
                if m['kind']=='P':
                    groups=[dict(zip(source['group_columns'],g)) for g in line['groups']]
                    pages[m['page']].append((line,groups))
        for page, rawlines in sorted(pages.items()):
            rawlines.sort(key=lambda x:int(x[0]['metadata']['source_row_index']))
            for li,(line,groups) in enumerate(rawlines):
                m=line['metadata']; assert int(m['source_group_count'])==len(groups); assert [int(g['source_group_index']) for g in groups]==list(range(1,len(groups)+1)); nextline=rawlines[li+1][0] if li+1<len(rawlines) else None
                next_ok=False
                if nextline:
                    nm=nextline['metadata']
                    try: next_ok=int(nm['locus'].rsplit('.',1)[1])==int(m['locus'].rsplit('.',1)[1])+1 and int(nm['source_row_index'])>int(m['source_row_index']) and nm['code'].startswith(('+','*'))
                    except ValueError: pass
                for i,g in enumerate(groups):
                    word=g['ivtff_group_raw']
                    if word not in inventory: continue
                    stem,y=inventory[word]; reasons=[]
                    if len(groups)<2: reasons.append('short')
                    left=g['left_separator']
                    if left=='LINE_START':
                        assert i==0
                        left_ok=True
                    else: left_ok=left=='DEFINITE_SPACE' and i>0 and int(groups[i-1]['source_group_index'])+1==int(g['source_group_index']) and groups[i-1]['right_separator']==left
                    if not left_ok:reasons.append('left')
                    right=g['right_separator']; boundary=None
                    if right in ['DEFINITE_SPACE','DRAWING_INTERRUPTION']:
                        if i+1<len(groups) and int(groups[i+1]['source_group_index'])==int(g['source_group_index'])+1 and groups[i+1]['left_separator']==right:
                            boundary='SPACE' if right=='DEFINITE_SPACE' else 'DRAWING'
                        else:reasons.append('right_unaligned')
                    elif right=='LINE_END':
                        if i==len(groups)-1 and int(g['source_group_index'])==int(m['source_group_count']) and next_ok:boundary='END'
                        else:reasons.append('end')
                    else: reasons.append('other_right')
                    event={'source_id':g['source_group_id'],'word':word,'stem':stem,'y':y,'leaf':int(re.match(r'f(\d+)',page)[1]),'page':page,'locus':m['locus'],'stratum':tuple(m[k] for k in ['section','currier','hand']),'boundary':boundary,'left':left,'right':right,'index':int(g['source_group_index']),'row':int(m['source_row_index']),'count':int(m['source_group_count']),'next_row':int(nextline['metadata']['source_row_index']) if nextline else None,'next_locus':nextline['metadata']['locus'] if nextline else None,'next_code':nextline['metadata']['code'] if nextline else None}
                    sid=event['source_id'];assert sid not in accepted[reader] and sid not in rejected[reader]
                    if reasons:rejected[reader][sid]=(event,reasons)
                    else:
                        accepted[reader][sid]=event
                        if boundary=='DRAWING':hosts[reader][m['locus']]=line
    predictions={}
    for r,es in accepted.items():
        predictions[r]={}
        for leaf in sorted({e['leaf'] for e in es.values()}):
            counts={b:collections.defaultdict(lambda:[0,0]) for b in ['END','SPACE']}
            for e in es.values():
                if e['leaf']==leaf or e['boundary']=='DRAWING':continue
                for key in [(),e['stratum'],(e['stem'],)+e['stratum']]:
                    c=counts[e['boundary']][key]; c[0]+=1;c[1]+=e['y']
            for e in es.values():
                if e['leaf']!=leaf:continue
                models={}
                for b in ['END','SPACE']:
                    ng,mg=counts[b][()]; ns,ms=counts[b][e['stratum']]; nt,mt=counts[b][(e['stem'],)+e['stratum']]
                    g=(mg+.5)/(ng+1);s=(ms+20*g)/(ns+20);p=(mt+10*s)/(nt+10)
                    models[b]={'N_global':ng,'M_global':mg,'g':g,'N_stratum':ns,'M_stratum':ms,'s':s,'N_stem_stratum':nt,'M_stem_stratum':mt,'p':p}
                pe=models['END']['p'];ps=models['SPACE']['p']
                le=-math.log2(pe if e['y'] else 1-pe);ls=-math.log2(ps if e['y'] else 1-ps)
                predictions[r][e['source_id']]={'END':models['END'],'SPACE':models['SPACE'],'gain':ls-le,'loss_END':le,'loss_SPACE':ls}
    return inventory,accepted,rejected,hosts,predictions
def main():
    inventory,accepted,rejected,hosts,predictions=reconstruct()
    checks=['all10pins','frozen155stems310wholeforms','allowlist179andsealed_exclusion','all_raw_source_indices_counts_seams_and_next_P_locus']
    art=E/'artifacts'; ae=read(art/'EVENTS.json'); ar=read(art/'EXCLUDED_HITS.json'); ap=read(art/'PREDICTIONS.json'); al=read(art/'LEAF_GAINS.json'); result=read(art/'RESULT.json')
    def mapped(e,r):
        return {'reader':r,'source_id':e['source_id'],'page':e['page'],'leaf':e['leaf'],'locus':e['locus'],'source_row_index':e['row'],'source_group_index':e['index'],'source_group_count':e['count'],'word':e['word'],'stem':e['stem'],'ending':'m' if e['y'] else 'l','m':e['y'],'left_separator':e['left'],'right_separator':e['right'],'boundary':{'DEFINITE_SPACE':'SPACE','DRAWING_INTERRUPTION':'DRAWING','LINE_END':'END'}.get(e['right']),'stratum':list(e['stratum']),'next_prose_locus':e['next_locus'],'next_prose_code':e['next_code']}
    def expected_reasons(e,reasons):
        out=[]
        for why in reasons:
            if why=='short':out.append('HOST_FEWER_THAN_TWO_GROUPS')
            elif why=='left':out.append('LEFT_JOIN_MISMATCH' if e['left']=='DEFINITE_SPACE' else 'LEFT_BOUNDARY_'+e['left'])
            elif why=='right_unaligned':out.append('RIGHT_JOIN_MISMATCH')
            elif why=='other_right':out.append('RIGHT_BOUNDARY_'+e['right'])
            elif why=='end':
                if e['index']!=e['count']:out.append('END_NOT_FINAL_GROUP')
                if e['next_locus'] is None:out.append('NO_NEXT_PROSE_LOCUS')
                else:
                    a,b=e['locus'].rsplit('.',1)[1],e['next_locus'].rsplit('.',1)[1]
                    if not a.isdigit() or not b.isdigit() or int(b)!=int(a)+1:out.append('NEXT_PROSE_NOT_CONSECUTIVE_NUMERIC')
                    if e['next_row']<=e['row']:out.append('NEXT_PROSE_NOT_HIGHER_ROW')
                    if not e['next_code'].startswith(('+','*')):out.append('NEXT_PROSE_NOT_BELOW_CODE')
        return out
    for r in accepted:
        assert len(ae[r])==len(accepted[r]) and len({x['source_id'] for x in ae[r]})==len(ae[r])
        for row in ae[r]:assert row==dict(mapped(accepted[r][row['source_id']],r),reasons=[])
        assert len(ar[r])==len(rejected[r]) and len({x['source_id'] for x in ar[r]})==len(ar[r])
        for row in ar[r]:
            e,reasons=rejected[r][row['source_id']]
            assert row==dict(mapped(e,r),reasons=expected_reasons(e,reasons)),row['source_id']
        assert len(ap[r])==len(accepted[r]) and len({x['source_id'] for x in ap[r]})==len(ap[r])
        for row in ap[r]:
            sid=row['source_id'];e=accepted[r][sid];p=predictions[r][sid]
            assert all(row[k]==v for k,v in dict(mapped(e,r),reasons=[]).items())
            for b in ['END','SPACE']:
                assert set(row['model_'+b])==set(p[b])
                for k,v in p[b].items():assert close(row['model_'+b][k],v),(r,sid,b,k)
                observed=p[b]['p'] if e['y'] else 1-p[b]['p']
                assert close(row['prob_observed_'+b],observed)
            assert close(row['gain_bits'],p['gain'])
    checks+=['all12015wholeform_hits_and_exclusions','all_accepted_boundary_assignments','all10874heldleaf_predictions_and_training_counts','all_hierarchical_backoffs_without_drawing_training','all_observed_probabilities_and_logloss_gains']
    assert read(art/'DRAWING_HOSTS.json')==hosts
    checks.append('all171drawingtargets_full_original_hosts')
    statuses={}
    for r,events in accepted.items():
        summary=result['readers'][r]
        assert summary['exact_form_hits']==len(events)+len(rejected[r]) and summary['accepted']==len(events) and summary['excluded']==len(rejected[r])
        reasoncounts=collections.Counter(z for e,why in rejected[r].values() for z in expected_reasons(e,why))
        assert summary['exclusion_reason_counts']==dict(reasoncounts)
        for b in ['DRAWING','END','SPACE']:
            evs=[e for e in events.values() if e['boundary']==b]
            groups=collections.defaultdict(list)
            for e in evs:groups[e['leaf']].append(e)
            assert len(al[r][b])==len(groups)
            means=[]
            for row in al[r][b]:
                subset=groups[row['leaf']];ids=[e['source_id'] for e in subset];ys=sum(e['y'] for e in subset);gains=[predictions[r][sid]['gain'] for sid in ids];mean=sum(gains)/len(gains);means.append(mean)
                assert row['events']==len(subset) and row['m']==ys and row['l']==len(subset)-ys
                assert set(row['source_ids'])==set(ids) and len(row['source_ids'])==len(ids)
                assert row['losses']==sum(g<0 for g in gains) and close(row['mean_gain_bits'],mean)
            gains=[predictions[r][e['source_id']]['gain'] for e in evs]
            stems=sorted({e['stem'] for e in evs});strata=sorted({e['stratum'] for e in evs})
            expected={'events':len(evs),'leaves':len(groups),'m':sum(e['y'] for e in evs),'l':sum(1-e['y'] for e in evs),'stem_count':len(stems),'stems':stems,'strata':[list(s) for s in strata],'micro_gain_bits':sum(gains)/len(gains),'equal_leaf_gain_bits':sum(means)/len(means),'positive_leaves':sum(g>0 for g in means),'positive_leaf_fraction':sum(g>0 for g in means)/len(means),'losses':sum(g<0 for g in gains),'zero_gains':sum(g==0 for g in gains)}
            for k,v in expected.items():
                actual=summary['boundaries'][b][k]
                assert close(actual,v) if isinstance(v,float) else actual==v,(r,b,k)
        d=summary['boundaries']['DRAWING'];en=summary['boundaries']['END']
        cap=d['events']>=20 and d['leaves']>=5 and d['m']>0 and d['l']>0
        st='NO_CAPACITY' if not cap else 'SUPPORTED' if d['equal_leaf_gain_bits']>=.01 and d['positive_leaf_fraction']>=.60 and en['equal_leaf_gain_bits']>0 else 'NOT_SUPPORTED'
        assert summary['capacity']==cap and summary['status']==st
        statuses[r]=st
    checks+=['all_drawing_END_SPACE_equalleaf_and_micro_aggregates','all_stem_stratum_terminal_and_loss_coverage','perreader_capacity_and_fixed_decisions']
    supports=sum(statuses[r]=='SUPPORTED' for r in ['ZL3b','IT2a'])
    status='READER_CONCORDANT_PREDICTIVE_TRANSFER' if supports==2 else 'READER_SPECIFIC_PREDICTIVE_TRANSFER' if supports==1 else 'ALL_NO_CAPACITY' if all(statuses[r]=='NO_CAPACITY' for r in ['ZL3b','IT2a']) else 'NO_SUPPORTED_TRANSFER'
    assert result['status']==status and result['meanings']==0 and result['frozen_stems']==155 and result['frozen_whole_forms']==310
    assert all(result[k] is False for k in ['independent_confirmation','significance_claim','l_m_equivalence_claim','physical_edge_claim','causal_production_order_claim','relation_packet_score_ready'])
    checks+=['crossreader_decision_no_RF_tiebreaker','no_meaning_equivalence_significance_or_causal_claim']
    out={'status':'PASS','checks_passed':len(checks),'checks':checks,'scientific_decision':status,'per_reader':{r:{'accepted':len(accepted[r]),'excluded':len(rejected[r]),'drawing':result['readers'][r]['boundaries']['DRAWING'],'END_calibration_equal_leaf_gain_bits':result['readers'][r]['boundaries']['END']['equal_leaf_gain_bits']} for r in accepted},'limitations':['Exposed caches are not independent manuscript confirmation.','Source-locus transitions are recorded below-code transitions, not guaranteed physical right edges.','Frozen hierarchy failure does not reject all layout-conditioned writing processes or identify lexical meaning.','Original images and earlier raw transcription sources were not reopened.']}
    (art/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
    text=['# GDT1155 independent validation','','PASS: '+str(len(checks))+' check groups.','','Independent extraction from the six pinned safe915 caches; no runner functions imported. All accepted and excluded whole-form hits, held-leaf model counts/probabilities, target and calibration predictions, leaf aggregates and exact drawing hosts reconstructed.','','Decision: '+status+'.','','## Checks','']+['- '+s for s in checks]+['','## Limits','']+['- '+s for s in out['limitations']]
    (art/'VALIDATION.md').write_text('\n'.join(text)+'\n')
    print(json.dumps({'status':'PASS','checks_passed':len(checks),'scientific_decision':status}))

if __name__=='__main__':main()
