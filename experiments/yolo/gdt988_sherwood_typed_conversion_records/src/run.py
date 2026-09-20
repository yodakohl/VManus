#!/usr/bin/env python3
"""Run only after public preregistration; all inherited target data are exposed."""
import json,csv,hashlib,itertools,time,datetime
from pathlib import Path
from collections import Counter
from matcher import solve,join,encode
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,obj):(A/n).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def main():
    lock=json.loads((E/'PREREG_LOCK.json').read_text())
    for path,want in lock['files'].items():assert sha(ROOT/path)==want,path
    s=json.loads((E/'src/SOURCE.json').read_text());start=time.monotonic()
    paragraphs=json.loads((ROOT/s['input_paragraphs']).read_text());cases=[];byid={};denoms={}
    for edition,ps in paragraphs.items():
        denoms[edition]=len(ps)
        for p in ps:
            assert not p['page'].startswith('f84') and p['page']!='f116v'
            words=[w for line in p['lines'] for w in line['words']]
            assert len(words)==p['groups']
            byid[(edition,p['id'])]=words
            eligible=all(line['anchor_eligible'] for line in p['lines'])
            for writer,trace in itertools.product(s['writers'],s['traces']):
                result=solve(s['traces'][trace],words,writer,s['limits']) if eligible else {'status':'UNKNOWN_SOURCE','reason':'one or more lines fail inherited literal/seam eligibility','codes':[],'nodes':0}
                row={'case':len(cases)+1,'edition':edition,'paragraph':p['id'],'page':p['page'],'leaf':p['leaf'],'writer':writer,'trace':trace,'predicted_groups':s['expected_groups'][writer],'observed_groups':len(words),**result}
                if eligible and len(words)==s['expected_groups'][writer]:row['observed_words']=words
                if result['codes']:
                    row['alignments']=[{'code':c,'complete_predicted_words':encode(s['traces'][trace],c,writer)} for c in result['codes']]
                cases.append(row)
    joints=[];attempts=0;joint_cutoff=False
    for edition,writer in itertools.product(paragraphs,s['writers']):
        left=[r for r in cases if r['edition']==edition and r['writer']==writer and r['trace']=='FAPESMO' and r['codes']]
        right=[r for r in cases if r['edition']==edition and r['writer']==writer and r['trace']=='FRISESOMORUM' and r['codes']]
        for a,b in itertools.product(left,right):
            if a['leaf']==b['leaf']:continue
            for ca,cb in itertools.product(a['codes'],b['codes']):
                if attempts>=s['limits']['joint_pairs']:joint_cutoff=True;break
                attempts+=1;c=join(ca,cb,writer)
                if c is not None:joints.append({'edition':edition,'writer':writer,'left_case':a['case'],'right_case':b['case'],'code':c,'FAPESMO_prediction':encode(s['traces']['FAPESMO'],c,writer),'FRISESOMORUM_prediction':encode(s['traces']['FRISESOMORUM'],c,writer)})
            if joint_cutoff:break
        if joint_cutoff:break
    statuses=Counter(r['status'] for r in cases)
    result={'experiment':'GDT988','paragraph_counts':denoms,'cases':len(cases),'status_counts':dict(sorted(statuses.items())),'breakdown':{e:{w:dict(sorted(Counter(r['status'] for r in cases if r['edition']==e and r['writer']==w).items())) for w in s['writers']} for e in paragraphs},'local_witness_cases':sum(bool(r['codes']) for r in cases),'joint_witnesses':len(joints),'joint_pairs_attempted':attempts,'joint_cutoff':joint_cutoff,'independent_meaning_confirmation_capacity':0,'confirmed_translated_words':0,'search_significance':None,'decision':'JOINT_CONDITIONAL_CANDIDATES' if joints else ('INCOMPLETE_COMPUTATION' if joint_cutoff or statuses['UNKNOWN_COMPUTATION'] else 'NO_LITERAL_COMPLETE_RECORD_FIT' if not any(r['codes'] for r in cases) else 'LOCAL_ONLY_NO_SHARED_CROSS_LEAF_CODE'),'scope':'Only the two fixed typed whole-record serializers; source-ineligible paragraphs remain unknown.'}
    dump('CASES.json',cases);dump('JOINT_CODES.json',joints);dump('RESULT.json',result)
    columns=['case','edition','paragraph','leaf','writer','trace','predicted_groups','observed_groups','status','reason','nodes']
    with (A/'CANDIDATES.tsv').open('w') as f:
        wr=csv.DictWriter(f,columns,delimiter='\t',extrasaction='ignore');wr.writeheader();wr.writerows(cases)
    with (A/'SOURCE_PREDICTIONS.tsv').open('w') as f:
        wr=csv.writer(f,delimiter='\t');wr.writerow(['writer','trace','group_position','required_atom_sequence'])
        for w,t in itertools.product(s['writers'],s['traces']):
            chunks=s['traces'][t] if w=='FUSED' else [[x] for c in s['traces'][t] for x in c]
            wr.writerows([w,t,i,' + '.join(c)] for i,c in enumerate(chunks,1))
    dump('EXECUTION_RECEIPT.json',{'started_after_lock':True,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-start,'input_sha256':sha(ROOT/s['input_paragraphs']),'prior_exposure':True,'new_admissions':0,'sealed_opened':False})
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
