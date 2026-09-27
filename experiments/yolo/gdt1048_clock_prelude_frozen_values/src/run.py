#!/usr/bin/env python3
"""Replay fixed whole-prelude capacity without assigning any new meaning."""
import argparse, csv, hashlib, io, json, subprocess
from collections import Counter
from pathlib import Path
EXP=Path(__file__).resolve().parent.parent
ROOT=EXP.parents[2]
TARGET='f111r|f111r.48-f111r.50'
SOURCE='experiments/semantic_assumptions/results/source_separator_transcription.tsv'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
    lock=json.loads((EXP/'src/PREREG_LOCK.json').read_text())
    for x in lock['fixed_files']+lock['inputs']:
        assert sha(ROOT/x['path'])==x['sha256'],x['path']
    parent=json.loads((ROOT/lock['inputs'][0]['path']).read_text())
    cache=json.loads((ROOT/lock['inputs'][5]['path']).read_text())
    source10=json.loads((ROOT/lock['inputs'][2]['path']).read_text())['source_only_future_options'][0]
    assert hashlib.sha256(source10['complete_text'].encode()).hexdigest()==source10['utf8_sha256']
    old={x['form']:x for x in parent['lexicon']};assert len(old)==33
    baseline=json.loads((ROOT/'experiments/yolo/gdt1047_bare_value_left_host/artifacts/RESULT.json').read_text())
    assert sha(ROOT/SOURCE)==baseline['source_sha256']
    columns=['source_group_id','edition','page','locus','source_group_index','ivtff_group_raw','paragraph_start','paragraph_end','left_separator','right_separator']
    command=['./vmanus-exp','query-tsv',SOURCE,'--selector','page','--allow','f111r','--columns',','.join(columns),'--forbid-prefix','f84','--forbid-prefix','f84r']
    query=subprocess.run(command,cwd=ROOT,check=True,text=True,capture_output=True)
    raw=list(csv.DictReader(io.StringIO(query.stdout),delimiter='\t'))
    raw={r['source_group_id']:r for r in raw}
    full={};summary=[];positions=[]
    for e,ng in [('ZL3b',32),('IT2a',31)]:
        selected=[p for p in cache[e] if p['id']==TARGET];assert len(selected)==1
        p=selected[0];full[e]=p
        words=[w for l in p['lines'] for w in l['words']]
        assert len(words)==ng==p['groups']
        assert p['lines'][0]['start'] and p['lines'][-1]['end']
        c=Counter(words);known=sorted(set(c)&set(old));unknown=sorted(set(c)-set(old))
        assert len(unknown)>18,'Declared capacity outcome differs; do not assume failure.'
        summary.append({'edition':e,'groups':len(words),'types':len(c),'old_types':known,'old_positions':sum(c[w] for w in known),'new_types':unknown,'new_type_count':len(unknown),'new_positions':sum(c[w] for w in unknown),'new_value_cap':18,'excess':len(unknown)-18,'verdict':'FIXED_LEXICAL_CAPACITY_EXCEEDED'})
        index=0
        for line in p['lines']:
            assert len(line['words'])==len(line['source_ids'])
            for i,(word,sid) in enumerate(zip(line['words'],line['source_ids']),1):
                index+=1;r=raw[sid]
                assert r['ivtff_group_raw']==word,(sid,word,r['ivtff_group_raw'])
                assert int(r['source_group_index'])==i
                assert bool(int(r['paragraph_start']))==line['start']
                assert bool(int(r['paragraph_end']))==line['end']
                positions.append({'edition':e,'position':index,'source_group_id':sid,'locus':line['locus'],'raw':word,'paragraph_start':line['start'],'paragraph_end':line['end'],'left_separator':r['left_separator'],'right_separator':r['right_separator'],'fixed_value':old[word]['value'] if word in old else None,'fixed_type':old[word]['type'] if word in old else None,'status':'FROZEN_OLD_VALUE_UNBOUND_IN_NEW_SOURCE' if word in old else 'UNASSIGNED_NEW_TYPE'})
    result={'experiment_id':'GDT1048','status':'FIXED_LEXICAL_CAPACITY_EXCEEDED_BOTH_READERS','registration':lock['registered_utc'],'deadline':lock['deadline_utc'],'prereg_sha256':sha(EXP/'src/PREREG_LOCK.json'),'target':TARGET,'candidate_source':'Vitruvius IX.8.10 complete owned paragraph','summary':summary,'RF1b':'NO_MATCHING_SOURCE_MARKED_WHOLE_PARAGRAPH','new_values_authored':0,'new_productions':0,'new_bindings':0,'semantic_execution':False,'source_obligations_completed':0,'confirmed_words':0,'independent_confirmation_capacity':0,'prior_exposure':True,'new_access':False,'global_prior_limit':'Descriptive parent profiles are disclosed; no semantic likelihood calibrated.','source10_sha256':source10['utf8_sha256'],'guard_replay':{'command':command,'source_sha256':sha(ROOT/SOURCE),'projection_sha256':hashlib.sha256(query.stdout.encode()).hexdigest(),'stats':query.stderr.strip()},'ceiling':'Capacity failure of this fixed whole-value development offer only; not semantic contradiction or all-clock impossibility.'}
    outputs={'RESULT.json':result,'TARGET.json':full,'ALL_POSITIONS.json':positions,'FROZEN_LEXICON.json':parent['lexicon'],'SOURCE10.json':source10}
    for name,value in outputs.items():
        p=EXP/'artifacts'/name
        if args.check:assert json.loads(p.read_text())==value,name
        else:p.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'status':result['status'],'summary':summary},indent=2))
if __name__=='__main__':main()
