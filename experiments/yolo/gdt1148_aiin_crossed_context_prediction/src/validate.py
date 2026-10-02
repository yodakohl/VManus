#!/usr/bin/env python3
"""Independent registered-rule audit. Does not import the root runner."""
import csv,gzip,hashlib,json,math,re,sys
sys.dont_write_bytecode=True
from collections import Counter,defaultdict
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
REPO=BASE.parents[2]
PURE=re.compile(r'[a-z]+')
TARGET=re.compile(r'(.*?)a(i{1,3})n')
ECHO=re.compile(r'.*ai+n')

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(gzip.decompress(path.read_bytes())) if path.suffix=='.gz' else json.loads(path.read_text())
def mean(xs): return math.fsum(xs)/len(xs) if xs else None

def reconstruct(inputs,reader):
    events=[]; audits=defaultdict(list); counts=Counter(); allids=[]
    for pin in inputs:
        if not re.search(r'SOURCE_(DISCOVERY|EVALUATION)_'+reader+r'\.json$',pin['path']): continue
        packet=read(REPO/pin['path'])
        partition='DISCOVERY' if 'DISCOVERY' in pin['path'] else 'EVALUATION'
        for line in packet['lines']:
            meta=line['metadata']; counts['all_lines']+=1
            if meta['kind']!='P': continue
            counts['prose_lines']+=1
            rows=[dict(zip(packet['group_columns'],g)) for g in line['groups']]
            indices={int(g['source_group_index']):g for g in rows}
            assert len(indices)==len(rows)
            assert [int(g['source_group_index']) for g in rows]==list(range(1,len(rows)+1))
            n=int(meta['source_group_count']); assert n==len(rows)
            for g in rows:
                sid=g['source_group_id']; raw=g['ivtff_group_raw']; idx=int(g['source_group_index'])
                allids.append(sid); counts['prose_groups']+=1
                if not PURE.fullmatch(raw):
                    counts['uncertain_groups']+=1
                    if 'ain' in raw or 'aiin' in raw: audits['uncertain_literal'].append(sid)
                    continue
                m=TARGET.fullmatch(raw)
                if not m:
                    if 'aiin' in raw: audits['other_pure_aiin'].append(sid)
                    continue
                prefix,ii=m.groups(); tail='a'+ii+'n'; leaf=int(re.match(r'f([0-9]+)',meta['page']).group(1))
                position='SINGLE' if n==1 else 'FINAL' if idx==n else 'PENULTIMATE' if idx==n-1 else 'EARLIER'
                contexts={}; reasons={}
                for side,step in [('L',-1),('R',1)]:
                    near=indices.get(idx+step)
                    if near is None: word=None; reason='EDGE'
                    else:
                        seam=(near['right_separator'],g['left_separator']) if side=='L' else (g['right_separator'],near['left_separator'])
                        w=near['ivtff_group_raw']
                        if seam!=('DEFINITE_SPACE','DEFINITE_SPACE'): word=None; reason='SEAM'
                        elif not PURE.fullmatch(w): word=None; reason='UNCERTAIN'
                        elif ECHO.fullmatch(w): word=None; reason='MASKED_FAMILY'
                        else: word=w; reason='ELIGIBLE'
                    contexts[side]=word; reasons[side]=reason
                e={'id':sid,'raw':raw,'prefix':prefix,'tail':tail,'leaf':leaf,'fold':leaf%5,
                   'cell':(meta['section'],meta['currier'],meta['hand'],position),
                   'L':contexts['L'],'R':contexts['R'],'reasons':reasons,'partition':partition,'metadata':meta,'native':g}
                if tail=='aiiin': audits['aiiin'].append(e)
                else: e['y']=int(tail=='aiin'); events.append(e)
    assert len(allids)==len(set(allids)), 'duplicate source positions across snapshots'
    return events,dict(audits),dict(counts)

def score(events):
    # Materialize each genuinely permitted training set independently of the runner.
    fitted={}; predictions=[]
    for event in events:
        key=(event['prefix'],event['fold'])
        if key not in fitted:
            train=[t for t in events if t['prefix']!=key[0] and t['fold']!=key[1]]
            assert all(t['prefix']!=key[0] and t['leaf']%5!=key[1] for t in train)
            cells=defaultdict(list); sides={s:defaultdict(list) for s in ('L','R')}
            for t in train:
                cells[t['cell']].append(t['y'])
                for s in ('L','R'):
                    if t[s] is not None: sides[s][(t['cell'],t[s])].append(t['y'])
            fitted[key]=(train,cells,sides,(sum(t['y'] for t in train)+1)/(len(train)+2))
        train,cells,sides,p0=fitted[key]; cell=event['cell']; ys=cells[cell]
        b=(sum(ys)+20*p0)/(len(ys)+20); probs={'B':b}; support={}
        for s in ('L','R'):
            ys2=sides[s].get((cell,event[s]),[]) if event[s] is not None else []
            probs[s]=(sum(ys2)+20*b)/(len(ys2)+20)
            support[s]=len(ys2)
        probs['C']=(probs['L']+probs['R'])/2
        losses={k:-math.log(p if event['y'] else 1-p) for k,p in probs.items()}
        predictions.append({'event':event,'probabilities':probs,'losses':losses,
          'predicted_forms':{k:event['prefix']+('aiin' if p>=.5 else 'ain') for k,p in probs.items()},
          'training_n':len(train),'training_y':sum(t['y'] for t in train),'p0':p0,'cell_n':len(ys),'cell_y':sum(ys),
          'side_support':support})
    return predictions

def summarize(predictions,bare):
    selected=[p for p in predictions if (p['event']['prefix']=='')==bare]
    leaves=defaultdict(list); prefixes=defaultdict(list); forms=defaultdict(set)
    for p in selected:
        e=p['event']; leaves[e['leaf']].append(p); prefixes[e['prefix']].append(p); forms[e['prefix']].add(e['y'])
    dual=sum(v=={0,1} for v in forms.values()); ys={p['event']['y'] for p in selected}
    capacity=(len(selected)>=30 and len(leaves)>=5 and ys=={0,1}) if bare else (len(selected)>=100 and len(leaves)>=5 and dual>=2)
    losses={k:mean([mean([p['losses'][k] for p in ps]) for ps in leaves.values()]) for k in ('B','L','R','C')}
    gains={k:(losses['B']-losses[k] if losses['B'] is not None else None) for k in ('L','R','C')}
    return {'events':len(selected),'leaves':len(leaves),'prefixes':len(prefixes),'dual_prefixes':dual,'capacity':capacity,
            'leaf_loss':losses,'leaf_gain':gains,
            'event_gain':mean([p['losses']['B']-p['losses']['C'] for p in selected]),
            'prefix_gain':mean([mean([p['losses']['B']-p['losses']['C'] for p in ps]) for ps in prefixes.values()])}


STATUS={'EDGE':'LINE_EDGE','SEAM':'UNCERTAIN_SEAM','UNCERTAIN':'UNCERTAIN_NEIGHBOUR','MASKED_FAMILY':'SERIES_ECHO_MASKED','ELIGIBLE':'ELIGIBLE'}
def event_record(e,reader):
    m=e['metadata'];g=e['native']
    return {'edition':reader,'id':e['id'],'page':m['page'],'locus':m['locus'],
      'index':int(g['source_group_index']),'source_group_count':int(m['source_group_count']),
      'raw':e['raw'],'stem':e['prefix'],'tail':e['tail'],'y':len(e['tail'])-3,
      'leaf':e['leaf'],'cell':list(e['cell']),
      'left':e['L'],'left_status':STATUS[e['reasons']['L']],
      'right':e['R'],'right_status':STATUS[e['reasons']['R']]}

def prediction_record(p,reader):
    out=event_record(p['event'],reader);out['fold']=p['event']['fold']
    out['left_training_support']=p['side_support']['L'];out['right_training_support']=p['side_support']['R']
    for k in ('B','L','R','C'):
        out['p_'+k]=p['probabilities'][k];out['loss_'+k]=p['losses'][k];out['prediction_'+k]=p['predicted_forms'][k]
    return out

def main():
    checks=[];mismatches=[];max_float_error=0.0
    def check(name,ok,detail=None):
        checks.append({'name':name,'pass':bool(ok),**({'detail':detail} if detail is not None else {})})
    def equal(a,b,path=''):
        nonlocal max_float_error
        if isinstance(a,float) and isinstance(b,(int,float)) and not isinstance(b,bool):
            delta=abs(a-b);max_float_error=max(max_float_error,delta);ok=math.isfinite(b) and delta<=1e-12
        elif isinstance(a,dict) and isinstance(b,dict):
            ok=set(a)==set(b)
            if ok: ok=all(equal(a[k],b[k],path+'/'+str(k)) for k in a)
        elif isinstance(a,list) and isinstance(b,list):
            ok=len(a)==len(b)
            if ok: ok=all(equal(x,y,path+'/'+str(i)) for i,(x,y) in enumerate(zip(a,b)))
        else: ok=type(a)==type(b) and a==b
        if not ok and len(mismatches)<20: mismatches.append(path)
        return ok
    source=read(BASE/'src/SOURCE.json'); lock=read(BASE/'src/PREREG_LOCK.json')
    watched=[BASE/f for f in ('METHOD.md','PREREGISTRATION.md','src/SOURCE.json','src/PREREG_LOCK.json','src/run.py')]
    watched += [BASE/'artifacts'/f for f in ('EVENTS.json.gz','FOLDS.json.gz','PREDICTIONS.json.gz','RESULT.json','PREDICTION_TABLE.tsv','PREFIX_RESULTS.tsv','LEAF_RESULTS.tsv')]
    watched += [REPO/p['path'] for p in source['inputs']]
    before={str(p.relative_to(REPO)):sha(p) for p in watched}
    check('registration_byte_lock',all(sha(BASE/k)==v for k,v in lock['hashes'].items()))
    check('all_11_source_and_predecessor_pins',all(sha(REPO/p['path'])==p['sha256'] for p in source['inputs']))
    spec=read(REPO/source['inputs'][0]['path']);allowed=set(spec['allowed_selectors'])
    check('source_allowlist_and_closed_reserves',source['sealed']==['f84','f84r'] and source['reserves']=='CLOSED' and not {'f84','f84r','f116v'}&allowed)
    packets=[p for p in source['inputs'] if re.search(r'SOURCE_(DISCOVERY|EVALUATION)_(ZL3b|IT2a|RF1b)\.json$',p['path'])]
    check('all_six_exact_snapshots',len(packets)==6)
    check('snapshot_native_scope',all(line['metadata']['page'] in allowed and not line['metadata']['page'].startswith('f84') for pin in packets for line in read(REPO/pin['path'])['lines']))
    root_events=read(BASE/'artifacts/EVENTS.json.gz');root_predictions=read(BASE/'artifacts/PREDICTIONS.json.gz');root_folds=read(BASE/'artifacts/FOLDS.json.gz');root_result=read(BASE/'artifacts/RESULT.json')
    expected_readers={};compact={};expected_predictions={};expected_events={};expected_folds={};expected_tables={'LEAF_RESULTS.tsv':{},'PREFIX_RESULTS.tsv':{}}
    for reader in ('ZL3b','IT2a','RF1b'):
        events,audits,counts=reconstruct(source['inputs'],reader);predictions=score(events)
        all_events=events+audits.get('aiiin',[])
        records={e['id']:event_record(e,reader) for e in all_events};expected_events.update(records)
        selected_root={e['id']:e for e in root_events if e['edition']==reader}
        check(reader+'_complete_inventory_native_fields_cells_context_masks',len(selected_root)==sum(e['edition']==reader for e in root_events) and equal(records,selected_root,reader+'/events'))
        prs={p['event']['id']:prediction_record(p,reader) for p in predictions};expected_predictions.update(prs)
        actual_prs={p['id']:p for p in root_predictions if p['edition']==reader}
        check(reader+'_every_B_L_R_C_probability_loss_prediction_support',len(actual_prs)==sum(p['edition']==reader for p in root_predictions) and equal(prs,actual_prs,reader+'/predictions'))
        groups=defaultdict(list)
        for e in events:groups[(e['prefix'],e['fold'])].append(e)
        fold_rows={}
        for (prefix,fold),tests in groups.items():
            train=[e for e in events if e['prefix']!=prefix and e['fold']!=fold]
            key=(reader,prefix,fold)
            fold_rows[key]={'edition':reader,'stem':prefix,'fold':fold,'train_events':len(train),'test_events':len(tests),
              'train_leaves':sorted({e['leaf'] for e in train}),'test_leaves':sorted({e['leaf'] for e in tests}),'train_stems':sorted({e['prefix'] for e in train})}
        actual_folds={(f['edition'],f['stem'],f['fold']):f for f in root_folds if f['edition']==reader}
        check(reader+'_every_fold_full_prefix_and_leaf_exclusion',len(actual_folds)==sum(f['edition']==reader for f in root_folds) and equal(fold_rows,actual_folds,reader+'/folds'))
        expected_folds.update(fold_rows)
        inventory={'P_groups':counts['prose_groups'],'uncertain_groups':counts.get('uncertain_groups',0),
          'ain':sum(e['tail']=='ain' for e in events),'aiin':sum(e['tail']=='aiin' for e in events),'aiiin':len(audits.get('aiiin',[])),
          'uncertain_literal_ain_or_aiin':len(audits.get('uncertain_literal',[])),'other_pure_containing_aiin':len(audits.get('other_pure_aiin',[]))}
        strata={};small={}
        for stratum,bare in [('BARE',True),('NONBARE',False)]:
            ps=[p for p in predictions if (p['event']['prefix']=='')==bare]
            byleaf=defaultdict(list);byprefix=defaultdict(list)
            for p in ps:byleaf[p['event']['leaf']].append(p);byprefix[p['event']['prefix']].append(p)
            both=sorted(k for k,v in byprefix.items() if {p['event']['y'] for p in v}=={0,1})
            s=summarize(predictions,bare)
            vals={'events':len(ps),'leaves':len(byleaf),'prefixes':len(byprefix),'prefixes_with_both_tails':both,
              'ain':sum(p['event']['y']==0 for p in ps),'aiin':sum(p['event']['y']==1 for p in ps),'capacity':s['capacity'],
              'left_supported_events':sum(p['side_support']['L']>0 for p in ps),'right_supported_events':sum(p['side_support']['R']>0 for p in ps),
              'context_status_counts':{side:dict(Counter(STATUS[p['event']['reasons'][k]] for p in ps)) for side,k in [('left','L'),('right','R')]}}
            for k in ('B','L','R','C'):
                vals['event_loss_'+k]=mean([p['losses'][k] for p in ps]);vals['accuracy_'+k]=mean([float(p['predicted_forms'][k]==p['event']['raw']) for p in ps])
            for k in ('L','R','C'):
                vals['leaf_macro_gain_'+k]=mean([mean([p['losses']['B']-p['losses'][k] for p in group]) for group in byleaf.values()])
                vals['event_gain_'+k]=mean([p['losses']['B']-p['losses'][k] for p in ps])
                vals['prefix_macro_gain_'+k]=mean([mean([p['losses']['B']-p['losses'][k] for p in group]) for group in byprefix.values()])
            for name,field,gs in [('LEAF_RESULTS.tsv','leaf',byleaf),('PREFIX_RESULTS.tsv','stem',byprefix)]:
                for value,group in gs.items():
                    row={'edition':reader,'stratum':stratum,field:value,'events':len(group)}
                    for k in ('C','L','R'):row['gain_'+k]=mean([p['losses']['B']-p['losses'][k] for p in group])
                    expected_tables[name][(reader,stratum,value)]=row
            strata[stratum]=vals
            small[stratum]={k:vals[k] for k in ('events','leaves','prefixes','ain','aiin','capacity','leaf_macro_gain_C','leaf_macro_gain_L','leaf_macro_gain_R')}
        expected_readers[reader]={'inventory':inventory,'strata':strata};compact[reader]={'inventory':inventory,'strata':small,'folds':len(fold_rows),'prose_lines':counts['prose_lines']}
        check(reader+'_all_inventory_capacity_strata_cells_and_gains',equal(expected_readers[reader],root_result['readers'][reader],reader+'/result'))
    check('all_events_predictions_folds_accounted',len(root_events)==len(expected_events) and len(root_predictions)==len(expected_predictions) and len(root_folds)==len(expected_folds))
    # TSVs are separately reconstructed rather than certified by JSON agreement alone.
    for name,expected in expected_tables.items():
        field='leaf' if name.startswith('LEAF') else 'stem';actual={}
        with (BASE/'artifacts'/name).open(newline='') as f:
            rows=list(csv.DictReader(f,delimiter='\t'))
        for row in rows:
            if field=='leaf':row[field]=int(row[field])
            row['events']=int(row['events'])
            for k in ('C','L','R'):row['gain_'+k]=float(row['gain_'+k])
            actual[(row['edition'],row['stratum'],row[field])]=row
        check(name+'_every_independent_aggregate',len(actual)==len(rows) and equal(expected,actual,name))
    with (BASE/'artifacts/PREDICTION_TABLE.tsv').open(newline='') as f:table=list(csv.DictReader(f,delimiter='\t'))
    expected_table={}
    keys=('edition','id','raw','stem','leaf','fold','left','right','p_B','p_L','p_R','p_C','prediction_C','left_training_support','right_training_support')
    for sid,p in expected_predictions.items():expected_table[sid]={k:('' if p[k] is None else p[k]) for k in keys}
    actual_table={}
    for row in table:
        for k in ('leaf','fold','left_training_support','right_training_support'):row[k]=int(row[k])
        for k in ('p_B','p_L','p_R','p_C'):row[k]=float(row[k])
        actual_table[row['id']]=row
    check('prediction_TSV_every_probability_and_native_reference',len(table)==len(actual_table) and equal(expected_table,actual_table,'prediction_table'))
    decisions={}
    for st in ('BARE','NONBARE'):
        deciding=[expected_readers[r]['strata'][st] for r in ('ZL3b','IT2a')]
        decisions[st]='INSUFFICIENT_CAPACITY' if not all(v['capacity'] for v in deciding) else 'TRANSFER_SUPPORTED_LIMITED' if all(v['leaf_macro_gain_C']>=.01 for v in deciding) else 'NO_MATERIAL_TRANSFER'
    flags={k:v=='TRANSFER_SUPPORTED_LIMITED' for k,v in decisions.items()}
    decision='JOINT_BARE_BOUND_TRANSFER' if all(flags.values()) else 'BARE_ONLY' if flags['BARE'] else 'BOUND_ONLY' if flags['NONBARE'] else 'NO_JOINT_TRANSFER'
    expected_result={'experiment':'GDT1148','decision':decision,'stratum_decisions':decisions,'readers':expected_readers,'confirmed_words':0,'independent_meaning_confirmation_capacity':0,'significance':'NOT_CLAIMED'}
    check('complete_result_fixed_stratum_and_family_gates',equal(expected_result,root_result,'result'))
    check('all_bound_inputs_runner_and_results_unchanged',all(sha(REPO/p)==h for p,h in before.items()))
    out={'experiment':'GDT1148','accounting_pass':all(c['pass'] for c in checks),'checks':checks,'independent_decision':decision,'stratum_decisions':decisions,
      'validator_sha256':sha(Path(__file__)),'bound_hashes':before,'reader_summary':compact,
      'compared_counts':{'inventory_events':len(expected_events),'binary_predictions':len(expected_predictions),'crossed_folds':len(expected_folds),'prefix_table_rows':len(expected_tables['PREFIX_RESULTS.tsv']),'leaf_table_rows':len(expected_tables['LEAF_RESULTS.tsv'])},
      'absolute_float_tolerance':1e-12,'maximum_observed_float_difference':max_float_error,'mismatch_paths':mismatches,
      'scope_limits':['All six old GDT915 snapshots are exposed; this is not blind or reserve confirmation.','Alternate readers are not independent manuscripts.','aiiin is inventoried separately and never included in binary training or scoring.','Capacity and negative transfer apply to this fixed whole-neighbor encoding and smoothing only.','No significance, morpheme meaning, attachment direction, English word meaning, or scientific semantic PASS is certified.']}
    (BASE/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'accounting_pass':out['accounting_pass'],'checks':len(checks),'failed':[c['name'] for c in checks if not c['pass']],'decision':decision,'compared_counts':out['compared_counts'],'max_float_difference':max_float_error}))
    return 0 if out['accounting_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
