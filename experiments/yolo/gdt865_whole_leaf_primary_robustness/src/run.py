"""Frozen primary holdout sensitivity; never calls the legacy main function."""
import argparse,collections,concurrent.futures,hashlib,importlib.util,json,math,multiprocessing,re,sys,time
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
LEGACY=ROOT/'experiments/yolo/gdt808_exact_relation_slot_residual_bridge/src/run.py'
M=None;EVENTS=[]
MODELS={'M01_L_TO_L':'L','M02_DY_TO_DY':'DY'}
PRED_FIELDS='prediction_id model_id population source_axis target_axis event_id carrier target_tail true_label page physical_folio paragraph_id locus line_number token_index section language hand targetfree_line_length_bin variant topic_score topic_known template_score template_known form_score form_known slot_score slot_known union_nuisance_score union_nuisance_known union_augmented_score union_augmented_known form_base_score form_base_known position_score position_known mask_score mask_known raw_slot_score raw_slot_known nuisance_score augmented_score nuisance_without_position_score nuisance_plus_mask_score augmented_raw_score'.split()
FEATURE_NAMES={'topic':'TOPIC','template':'TEMPLATE','form_regime':'FORM_REGIME','slot_hole':'SLOT_HOLE','mask_status_audit':'MASK_STATUS','raw_slot_sensitivity':'RAW_SLOT'}
ATLAS_FIELDS='event_id carrier tail axis expanded_label surface page physical_folio paragraph_id locus line_number token_index targetfree_line_length_bin'.split()+[p+s for p in FEATURE_NAMES for s in ['_feature_count','_feature_sha256']]
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def save(name,x,runtime=False):
 p=E/('runtime' if runtime else 'artifacts')/name;p.parent.mkdir(exist_ok=True);p.write_text(enc(x))
def loadlegacy():
 global M
 spec=importlib.util.spec_from_file_location('gdt808_frozen_primary',LEGACY);M=importlib.util.module_from_spec(spec);sys.modules[spec.name]=M;spec.loader.exec_module(M)
def leaf(p):
 m=re.match(r'^(f[0-9]+)',p);assert m and not p.startswith('f84');return m[1]
def prediction(e,model,bundle):
 axis=MODELS[model];r=dict(prediction_id=f'{model}:{e.event_id}',model_id=model,population='CORE13',source_axis=axis,target_axis=axis,event_id=e.event_id,carrier=e.carrier,target_tail=e.tail,true_label=e.label,page=e.page,physical_folio=e.folio,paragraph_id=e.paragraph.paragraph_id,locus=e.locus,line_number=e.line_number,token_index=e.token_index,section=e.paragraph.section,language=e.paragraph.language,hand=e.paragraph.hand,targetfree_line_length_bin=e.targetfree_line_length_bin,variant='EXACT')
 for name,value in M.score_bundle(bundle,e,'EXACT').items():r[name if name.endswith('_known') else name+'_score']=value if name.endswith('_known') else M.f12(float(value))
 return r
def fold_task(key):
 model,carrier,face=key;source=[e for e in EVENTS if e.axis==MODELS[model]];test=sorted([e for e in source if e.carrier==carrier and e.folio==face],key=lambda e:(M.selector_sort_key(e.page),e.line_number,e.token_index,e.event_id));baseline=[e for e in source if e.carrier!=carrier and e.folio!=face];whole=[e for e in source if e.carrier!=carrier and leaf(e.page)!=leaf(face)]
 old=M.train_bundle(baseline,'EXACT',auxiliary=True);new=old if [e.event_id for e in baseline]==[e.event_id for e in whole] else M.train_bundle(whole,'EXACT',auxiliary=True)
 audit=dict(model_id=model,held_carrier=carrier,held_face=face,held_leaf=leaf(face),baseline_train_ids=[e.event_id for e in baseline],leaf_train_ids=[e.event_id for e in whole],test_ids=[e.event_id for e in test],baseline_train_count=len(baseline),leaf_train_count=len(whole),test_count=len(test),leaf_train_carriers=len({e.carrier for e in whole}),leaf_train_classes=sorted({e.label for e in whole}),carrier_excluded=all(e.carrier!=carrier for e in whole),whole_leaf_excluded=all(leaf(e.page)!=leaf(face) for e in whole),unchanged=len(baseline)==len(whole))
 return [prediction(e,model,old) for e in test],[prediction(e,model,new) for e in test],audit
def event_record(e):
 return dict(event_id=e.event_id,carrier=e.carrier,tail=e.tail,axis=e.axis,label=e.label,surface=e.surface,page=e.page,face=e.folio,folio=e.folio,leaf=leaf(e.page),locus=e.locus,line_number=e.line_number,token_index=e.token_index,paragraph_id=e.paragraph.paragraph_id,section=e.paragraph.section,language=e.paragraph.language,hand=e.paragraph.hand,targetfree_line_length_bin=e.targetfree_line_length_bin,features={k:sorted(v) for k,v in e.features.items()})
def macro(rows,field):
 values={}
 for carrier in sorted({r['carrier'] for r in rows}):
  rr=[r for r in rows if r['carrier']==carrier];v=M.auc([int(r['true_label']) for r in rr],[float(r[field]) for r in rr])
  if v is not None:values[carrier]=v
 return dict(carrier_macro_auc=math.fsum(values.values())/len(values) if values else None,carriers_scored=len(values),carriers_auc_above_half=sum(v>.5 for v in values.values()),per_carrier=values)
def summaries(old,new):
 metrics={};ranges={};decisions={}
 for model in MODELS:
  a=[r for r in old if r['model_id']==model];b=[r for r in new if r['model_id']==model];metrics[model]={};ranges[model]={}
  for channel,field in M.SCORE_FIELDS.items():
   aa=M.metrics(a,field);bb=M.metrics(b,field);byold={r['event_id']:r for r in a};per={}
   for c in sorted(aa['per_carrier']):
    rr=[r for r in b if r['carrier']==c];changes=[float(r[field])-float(byold[r['event_id']][field]) for r in rr];per[c]=dict(baseline_auc=aa['per_carrier'][c],leaf_auc=bb['per_carrier'].get(c),auc_delta=bb['per_carrier'][c]-aa['per_carrier'][c],mean_score_change=math.fsum(changes)/len(changes),mean_absolute_score_change=math.fsum(abs(x) for x in changes)/len(changes))
   metrics[model][channel]=dict(baseline=aa,leaf=bb,delta_macro_auc=bb['carrier_macro_auc']-aa['carrier_macro_auc'],paired_per_carrier=per)
  n=metrics[model]['NUISANCE']['leaf'];decisions[model]='PRIMARY_THRESHOLD_SURVIVES_WHOLE_LEAF_EXCLUSION' if n['carrier_macro_auc']>=.60 and n['carriers_auc_above_half']>=9 and n['carriers_scored']==13 else 'PRIMARY_THRESHOLD_NOT_RETAINED'
  for channel in ['NUISANCE','AUGMENTED','SLOT_HOLE']:
   field=M.SCORE_FIELDS[channel];deletions=[]
   for held in sorted({leaf(r['page']) for r in a}):
    aa=macro([r for r in a if leaf(r['page'])!=held],field);bb=macro([r for r in b if leaf(r['page'])!=held],field);delta=bb['carrier_macro_auc']-aa['carrier_macro_auc'] if aa['carrier_macro_auc'] is not None and bb['carrier_macro_auc'] is not None else None;deletions.append(dict(deleted_test_leaf=held,baseline=aa,leaf=bb,delta_macro_auc=delta))
   ranges[model][channel]=dict(deletions=deletions,baseline_range=[min(d['baseline']['carrier_macro_auc'] for d in deletions),max(d['baseline']['carrier_macro_auc'] for d in deletions)],leaf_range=[min(d['leaf']['carrier_macro_auc'] for d in deletions),max(d['leaf']['carrier_macro_auc'] for d in deletions)],delta_range=[min(d['delta_macro_auc'] for d in deletions),max(d['delta_macro_auc'] for d in deletions)])
 return metrics,ranges,decisions

def main():
 global EVENTS
 ap=argparse.ArgumentParser();ap.add_argument('--workers',type=int,default=16);ap.add_argument('--check',action='store_true');ap.add_argument('--controls',action='store_true');args=ap.parse_args();loadlegacy()
 if args.controls:
  assert leaf('f104r')==leaf('f104v')=='f104' and leaf('f86v3')=='f86';assert M.ALPHA==.5;print('CONTROLS PASS');return
 if args.check:
  old=json.loads((E/'artifacts/BASELINE_PREDICTIONS.json').read_text());new=json.loads((E/'artifacts/LEAF_PREDICTIONS.json').read_text());metrics,ranges,decisions=summaries(old,new)
  for n,v in [('METRICS.json',metrics),('LEAF_DELETE_RANGES.json',ranges)]:assert (E/'artifacts'/n).read_text()==enc(v),n
  assert json.loads((E/'artifacts/RESULT.json').read_text())['axis_decisions']==decisions;print('CACHED METRIC REPLAY PASS');return
 lock=json.loads((E/'src/PREREG_LOCK.json').read_text())
 for name,digest in lock.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
 started=time.time();pages=json.loads((ROOT/'experiments/yolo/gdt851_primitive_tandem_raw_group_discovery/src/SPEC.json').read_text())['allowed_selectors'];assert len(pages)==179 and not any(p.startswith('f84') for p in pages)
 legacy_pages=[row['page'] for row in M.read_tsv(M.ALLOWLIST)];assert len(legacy_pages)==179 and set(legacy_pages)==set(pages), '631/851 allowlist mismatch'
 raw35,all28,core13,thin9,overlap6=M.spec_sets();lines,paragraphs,bylocus,guardstats,token_rows=M.load_corpus();q152,_=M.build_q152(raw35,thin9,overlap6);all_events=M.collect_events(lines,paragraphs,bylocus,set(all28));EVENTS=[e for e in all_events if e.carrier in core13];assert len(all_events)==2208 and len(EVENTS)==1777 and collections.Counter(e.tail for e in EVENTS)==M.EXPECTED_CORE_TAILS
 observed={w for line in lines for w in line.tokens};end_classes=sorted({w[-1] for w in observed-q152 if w})
 for e in EVENTS:
  assert all(line.page==e.page for line in e.paragraph.lines), 'Cross-page paragraph context'
  e.features=M.build_event_features(e,q152,end_classes);e.targetfree_line_length_bin=M.length_bin(sum(w not in q152 for w in e.line.tokens))
 basepath=Path('experiments/yolo/gdt808_exact_relation_slot_residual_bridge/artifacts');published,ps=M.guarded_query(ROOT/basepath/'GDT808_HELD_PREDICTIONS.tsv',pages,PRED_FIELDS,'G865_BASELINE_PREDICTIONS');atlas,ats=M.guarded_query(ROOT/basepath/'GDT808_1777_CORE_EVENT_ATLAS.tsv',pages,ATLAS_FIELDS,'G865_EVENT_FEATURE_HASHES');published=[r for r in published if r['model_id'] in MODELS and r['population']=='CORE13' and r['variant']=='EXACT'];assert len(published)==1777 and len(atlas)==1777
 save('GUARD_REQUESTS.json',[dict(source=str(basepath/'GDT808_HELD_PREDICTIONS.tsv'),selectors=pages,columns=PRED_FIELDS,artifact_key='predictions'),dict(source=str(basepath/'GDT808_1777_CORE_EVENT_ATLAS.tsv'),selectors=pages,columns=ATLAS_FIELDS,artifact_key='atlas')]);save('SOURCE_HASHES.json',dict(legacy_code_sha256=hashlib.sha256(LEGACY.read_bytes()).hexdigest(),guarded_projection_sha256={name:hashlib.sha256(enc(value).encode()).hexdigest() for name,value in dict(normalized_lines=[dict(page=l.page,locus=l.locus,number=l.number,section=l.section,language=l.language,hand=l.hand,paragraph_start=l.paragraph_start,paragraph_end=l.paragraph_end,tokens=l.tokens,stable=l.stable,cross=l.cross) for l in lines],tokens=token_rows,published_predictions=published,event_atlas=atlas).items()}));save('GUARDED_BASELINE.json',dict(predictions=published,atlas=atlas),True);save('GUARD.json',guardstats+[ps,ats]);save('EVENT_FEATURES.json',[event_record(e) for e in EVENTS],True);save('EVENT_METADATA.json',[dict({k:v for k,v in event_record(e).items() if k!='features'},feature_hashes={prefix:M.value_fingerprint(e.features[name]) for prefix,name in FEATURE_NAMES.items()},feature_counts={prefix:len(e.features[name]) for prefix,name in FEATURE_NAMES.items()}) for e in EVENTS])
 amap={r['event_id']:r for r in atlas};issues=[]
 for e in EVENTS:
  row=amap[e.event_id];expected=dict(event_id=e.event_id,carrier=e.carrier,tail=e.tail,axis=e.axis,expanded_label=e.label,surface=e.surface,page=e.page,physical_folio=e.folio,paragraph_id=e.paragraph.paragraph_id,locus=e.locus,line_number=e.line_number,token_index=e.token_index,targetfree_line_length_bin=e.targetfree_line_length_bin)
  for prefix,name in FEATURE_NAMES.items():expected[prefix+'_feature_count']=len(e.features[name]);expected[prefix+'_feature_sha256']=M.value_fingerprint(e.features[name])
  for k,v in expected.items():
   if str(v)!=row[k]:issues.append(dict(event=e.event_id,field=k,expected=row[k],actual=str(v)))
 if issues:save('BASELINE_CHECK.json',dict(status='FEATURE_OR_COHORT_MISMATCH',issues=issues));save('RESULT.json',dict(status='BASELINE_MISMATCH_STOP'));return
 jobs=[];capacity=[]
 for model,axis in MODELS.items():
  source=[e for e in EVENTS if e.axis==axis];groups=sorted({(e.carrier,e.folio) for e in source});assert len(groups)==M.EXPECTED_MODEL_FOLDS[model]
  for c,f in groups:
   tr=[e for e in source if e.carrier!=c and leaf(e.page)!=leaf(f)]
   if {e.label for e in tr}!={0,1} or len({e.carrier for e in tr})!=12:capacity.append(dict(model=model,carrier=c,face=f,classes=sorted({e.label for e in tr}),carriers=len({e.carrier for e in tr})))
   jobs.append((model,c,f))
 if capacity:save('CAPACITY.json',dict(status='CAPACITY_STOP',failed_folds=capacity));save('RESULT.json',dict(status='CAPACITY_STOP'));return
 save('CAPACITY.json',dict(status='PASS',folds=len(jobs)));old=[];new=[];folds=[]
 with concurrent.futures.ProcessPoolExecutor(max_workers=max(1,min(32,args.workers)),mp_context=multiprocessing.get_context('fork')) as pool:
  for a,b,f in pool.map(fold_task,jobs,chunksize=1):old+=a;new+=b;folds.append(f)
 old.sort(key=lambda r:r['prediction_id']);new.sort(key=lambda r:r['prediction_id']);lookup={r['prediction_id']:r for r in published};assert len(lookup)==1777;issues=[]
 for row in old:
  for k in PRED_FIELDS:
   if str(row[k])!=lookup[row['prediction_id']][k]:issues.append(dict(prediction=row['prediction_id'],field=k,expected=lookup[row['prediction_id']][k],actual=str(row[k])))
 save('BASELINE_CHECK.json',dict(status='PASS' if not issues else 'PREDICTION_MISMATCH',feature_cohort_records_checked=1777,predictions_checked=len(old),fields_checked=PRED_FIELDS,issues=issues));save('BASELINE_PREDICTIONS.json',old);save('FOLDS_FULL.json',folds,True);save('FOLDS.json',[dict({k:v for k,v in f.items() if k not in ['baseline_train_ids','leaf_train_ids']},baseline_train_ids_sha256=hashlib.sha256(enc(f['baseline_train_ids']).encode()).hexdigest(),leaf_train_ids_sha256=hashlib.sha256(enc(f['leaf_train_ids']).encode()).hexdigest()) for f in folds])
 if issues:save('RESULT.json',dict(status='BASELINE_MISMATCH_STOP'));return
 unchanged=[f for f in folds if f['unchanged']];assert len(unchanged)==108;unids={f['model_id']+':'+i for f in unchanged for i in f['test_ids']};assert all(a==b for a,b in zip(old,new) if a['prediction_id'] in unids)
 save('LEAF_PREDICTIONS.json',new);metrics,ranges,decisions=summaries(old,new);save('METRICS.json',metrics);save('LEAF_DELETE_RANGES.json',ranges);save('RESULT.json',dict(status='COMPLETE_PRIMARY_WHOLE_LEAF_ROBUSTNESS_AUDIT',axis_decisions=decisions,events=1777,folds=963,unchanged_folds=108,baseline_serialized_parity=True,elapsed_seconds=round(time.time()-started,3)));print(enc(decisions))
if __name__=='__main__':main()
