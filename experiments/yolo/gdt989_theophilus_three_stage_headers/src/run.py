#!/usr/bin/env python3
import collections,csv,datetime,hashlib,json,re
from pathlib import Path
from matcher import solve,encode
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]; A=E/'artifacts'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x): (A/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def number(line): return int(line['locus'].rsplit('.',1)[1])
def headers(s):
    index={}
    for phase in ('DISCOVERY','EVALUATION'):
        for edition in ('ZL3b','IT2a','RF1b'):
            src=json.loads((ROOT/(s['header_input_prefix']+phase+'_'+edition+'.json')).read_text())
            for line in src['lines']:
                m=line['metadata'];assert not m['page'].startswith('f84') and m['page']!='f116v'
                k=(edition,m['page'],m['locus']); assert k not in index
                index[k]=(m,[dict(zip(src['group_columns'],g)) for g in line['groups']])
    return index
def head(p,edition,index):
    l=p['lines'][0]; k=(edition,p['page'],l['locus']); expected=l['source_ids'][0]
    if k not in index:return dict(eligible=False,reason='MISSING_LINE',expected_source_id=expected)
    m,gs=index[k]
    if not gs:return dict(eligible=False,reason='MISSING_GROUP',expected_source_id=expected)
    g=gs[0]; reasons=[]
    if g['source_group_id']!=expected: reasons.append('SOURCE_ID_MISMATCH')
    if int(g['source_group_index'])!=1: reasons.append('NOT_FIRST_GROUP')
    if not re.fullmatch('[a-z]+',g['ivtff_group_raw']): reasons.append('NONLITERAL_HEADER')
    if len(gs)>1:
        if int(gs[1]['source_group_index'])!=2 or g['right_separator']!='DEFINITE_SPACE' or gs[1]['left_separator']!='DEFINITE_SPACE':reasons.append('UNCERTAIN_RIGHT_SEAM')
    elif int(m['source_group_count'])!=1:reasons.append('MISSING_NEXT_GROUP')
    return dict(eligible=not reasons,reason='LITERAL_HEADER_DEFINITE_SEAM' if not reasons else '+'.join(reasons),expected_source_id=expected,group=g,next_group=gs[1] if len(gs)>1 else None,source_group_count=int(m['source_group_count']))
def main():
    lock=json.loads((E/'PREREG_LOCK.json').read_text())
    for p,h in lock['files'].items(): assert sha(ROOT/p)==h,p
    s=json.loads((E/'src/SOURCE.json').read_text()); ps=json.loads((ROOT/s['paragraph_input']).read_text()); ix=headers(s)
    allheads={};bundles=[];cases=[];equivalence=collections.defaultdict(list)
    for ed,rows in ps.items():
        pages=collections.defaultdict(list)
        for p in rows:
            assert not p['page'].startswith('f84') and p['page']!='f116v'
            allheads[ed+'|'+p['id']]=head(p,ed,ix);pages[p['page']].append(p)
        for page,parts in sorted(pages.items()):
            parts.sort(key=lambda p:p['lines'][0]['row'])
            for start in range(max(0,len(parts)-8)):
                seq=parts[start:start+9];bid=len(bundles)+1
                hs=[allheads[ed+'|'+p['id']] for p in seq]
                gaps=[dict(after=seq[j]['id'],before=seq[j+1]['id'],last_locus=seq[j]['lines'][-1]['locus'],next_locus=seq[j+1]['lines'][0]['locus']) for j in range(8) if number(seq[j]['lines'][-1])+1!=number(seq[j+1]['lines'][0])]
                observed=[h.get('group',{}).get('ivtff_group_raw') for h in hs]
                bundles.append(dict(bundle=bid,edition=ed,page=page,leaf=seq[0]['leaf'],paragraphs=[p['id'] for p in seq],heads=observed,source_ids=[h['expected_source_id'] for h in hs],header_records=hs,gaps=gaps))
                for w in s['writers']:
                    if gaps:r=dict(status='UNKNOWN_GAP',reason='NONCONSECUTIVE_SOURCE_LOCI',codes=[])
                    elif not all(h['eligible'] for h in hs):r=dict(status='UNKNOWN_HEADER',reason='INELIGIBLE_FIRST_GROUP_OR_SEAM',codes=[])
                    else:r=solve(observed,w)
                    case=dict(case=len(cases)+1,bundle=bid,edition=ed,page=page,leaf=seq[0]['leaf'],writer=w,**r);cases.append(case)
                    for c in r['codes']:
                        prediction=encode(c,w);key=json.dumps([w,c,prediction],sort_keys=True)
                        equivalence[key].append(case['case'])
    classes=[dict(writer=json.loads(k)[0],code=json.loads(k)[1],predicted_heads=json.loads(k)[2],owner_cases=v) for k,v in sorted(equivalence.items())]
    status=collections.Counter(c['status'] for c in cases)
    result=dict(experiment='GDT989',paragraph_counts={e:len(v) for e,v in ps.items()},header_eligibility={e:dict(collections.Counter(h['reason'] for k,h in allheads.items() if k.startswith(e+'|'))) for e in ps},bundles=len(bundles),cases=len(cases),status_counts=dict(status),breakdown={e:dict(collections.Counter(c['status'] for c in cases if c['edition']==e)) for e in ps},physical_leaves=len({b['leaf'] for b in bundles}),readable_contiguous_bundles=sum(c['writer']==s['writers'][0] and c['status'] in ('HEADER_FIT','CONTRADICTION') for c in cases),candidate_codes=sum(len(c['codes']) for c in cases),consequence_classes=len(classes),decision='HEADER_CANDIDATES_REQUIRE_COMPLETE_BODY' if classes else 'NO_READABLE_NINE_HEADER_FIT',independent_confirmation_capacity=0,confirmed_translated_words=0,search_significance=None)
    prediction_classes=collections.defaultdict(list)
    for c in classes:prediction_classes[tuple(c['predicted_heads'])].append(dict(writer=c['writer'],code=c['code'],owner_cases=c['owner_cases']))
    save('PREDICTION_CLASSES.json',[dict(predicted_heads=list(k),indistinguishable_codes=v) for k,v in sorted(prediction_classes.items())])
    save('HEADERS.json',allheads);save('BUNDLES.json',bundles);save('CASES.json',cases);save('CONSEQUENCE_CLASSES.json',classes);save('RESULT.json',result)
    with (A/'CANDIDATES.tsv').open('w') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['case','edition','page','leaf','bundle','writer','paragraphs','observed_heads','source_ids','status','reason','candidate_codes','cuts','rejected_cuts','duplicate_positions'])
        for c in cases:
            b=bundles[c['bundle']-1];w.writerow([c['case'],c['edition'],c['page'],c['leaf'],c['bundle'],c['writer'],';'.join(b['paragraphs']),' '.join(x or '<missing>' for x in b['heads']),';'.join(b['source_ids']),c['status'],c['reason'],json.dumps(c['codes'],sort_keys=True),c.get('cuts',0),json.dumps(c.get('rejected_cuts',{}),sort_keys=True),json.dumps(c.get('duplicate_positions',[]))])
    with (A/'SOURCE_PREDICTIONS.tsv').open('w') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['writer','chapter','name','stage','predicted_header'])
        for writer in s['writers']:
            for ch in s['chapters']:
                atoms=([ch['stage'],ch['name']] if writer=='STAGE_PREFIX' else [ch['name'],ch['stage']]) if ch['stage'] else [ch['name']]
                w.writerow([writer,ch['chapter'],ch['name'],ch['stage'] or '', '+'.join(atoms)])
    save('EXECUTION_RECEIPT.json',dict(completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),registered_utc=lock['registered_utc'],prior_exposure=True,new_admissions=0,reserves_opened=False))
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
