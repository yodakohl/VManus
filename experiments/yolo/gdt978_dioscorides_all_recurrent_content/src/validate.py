"""Ground certificate checker; no solver import, no search or target repair."""
import argparse,collections,csv,gzip,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
OLD=R/'experiments/yolo/gdt976_dioscorides_shared_referent_projection';LAST=R/'experiments/yolo/gdt977_dioscorides_leaf_breadth_projection'
SOURCE=R/'experiments/yolo/gdt963_dioscorides_complete_content_code/src/SOURCE.json'
def loadgz(p):
 with gzip.open(p,'rt') as f:return json.load(f)
def source_check(source,model):
 errors=[];counts=collections.Counter(a for r in source['records'] for a in r['atoms']);recur={a for a,n in counts.items() if n>1};original={r['id']:r for r in source['records']}
 if set(model['recurrent_atoms'])!=recur or len(model['recurrent_atoms'])!=len(recur):errors.append('recurrent_type_inventory')
 if [r['id'] for r in model['records']]!=[r['id'] for r in source['records']]:errors.append('record_order')
 singletons=0;gapcount=0;seams=0;events=0
 for record in model['records']:
  seq=original[record['id']]['atoms'];cursor=0;gaps={g['id']:g for g in record['gaps']};used=[];previous_atom=False
  if record['counts']!=dict(collections.Counter(seq)) or record['source_atoms']!=len(seq):errors.append('source_counts')
  for term in record['terms']:
   if 'atom' in term:
    if cursor>=len(seq) or seq[cursor]!=term['atom'] or term['source_index']!=cursor or term['atom'] not in recur:errors.append('atom_order')
    cursor+=1;events+=1;seams+=int(previous_atom);previous_atom=True
   else:
    gap=gaps[term['gap']];indices=gap['source_indices'];used.append(gap['id'])
    if not indices or indices!=list(range(cursor,cursor+len(indices))) or gap['minimum']!=len(indices):errors.append('gap_indices')
    if any(i>=len(seq) or counts[seq[i]]!=1 for i in indices):errors.append('gap_contains_recurrence')
    if cursor+len(indices)<len(seq) and counts[seq[cursor+len(indices)]]==1:errors.append('nonmaximal_gap')
    cursor+=len(indices);singletons+=len(indices);gapcount+=1;previous_atom=False
  if cursor!=len(seq) or set(used)!=set(gaps) or len(used)!=len(gaps):errors.append('record_coverage')
 for key,value in [('recurrent_occurrences',events),('source_occurrences',sum(counts.values())),('singleton_occurrences',singletons),('singleton_runs',gapcount),('adjacent_recurrent_pairs',seams)]:
  if model.get(key)!=value:errors.append('count:'+key)
 return errors

def witness_check(model,domains,row,part=None,base=None):
 errors=[];code=row.get('code',{});gaps=row.get('gaps',{});assign=row.get('assignments',{})
 if set(code)!=set(model['recurrent_atoms']) or any(not isinstance(v,str) or not v for v in code.values()):return ['code_inventory_or_empty'],[]
 words=sorted(code.values())
 if any(b.startswith(a) for a,b in zip(words,words[1:])):errors.append('prefix_collision')
 expected_gaps={g['id']:g for rec in model['records'] for g in rec['gaps']}
 if set(gaps)!=set(expected_gaps):return errors+['gap_inventory'],[]
 if any(not isinstance(v,str) or len(v)<expected_gaps[k]['minimum'] for k,v in gaps.items()):errors.append('gap_minimum')
 if set(assign)!=set(domains):return errors+['role_inventory'],[]
 leaves=[];alignments=[]
 for rec in model['records']:
  rid=rec['id'];matches=[x for x in domains[rid] if x['page']==assign[rid]['page']]
  if len(matches)!=1:errors.append('page_domain');continue
  target=matches[0];leaves.append(target['physical_leaf'])
  if assign[rid]['physical_leaf']!=target['physical_leaf']:errors.append('leaf_identity')
  cursor=0;rendered=''
  for term in rec['terms']:
   label=term.get('atom',term.get('gap'));value=code[label] if 'atom' in term else gaps[label]
   positions=[term['source_index']] if 'atom' in term else expected_gaps[label]['source_indices']
   alignments.append(dict(record=rid,page=target['page'],kind='RECURRENT_CODE' if 'atom' in term else 'UNRESOLVED_SINGLETON_RUN',source_indices=positions,label=label,start=cursor,end=cursor+len(value),text=value));rendered+=value;cursor+=len(value)
  if rendered!=target['text']:errors.append('whole_page_reconstruction:'+rid)
 if len(leaves)!=4 or len(set(leaves))!=4:errors.append('four_distinct_leaves')
 if part is not None:
  if assign['I.1']['page']!=part['iris_page']:errors.append('partition_identity')
  matches=[i for i in part['base_ids'] if base[i]['iris_code']==code['IRIS'] and base[i]['xiphion_code']==code['XIPHION'] and base[i]['xiphion_page']==assign['IV.20']['page']]
  if matches!=[row.get('witnessed_base_id')]:errors.append('old_case_identity')
 return errors,alignments

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-only',action='store_true');args=ap.parse_args()
 source=json.loads(SOURCE.read_text());model=json.loads((E/'src/SOURCE_MODEL.json').read_text());errors=source_check(source,model)
 if args.source_only:
  out=dict(status='PASS_SOURCE_ONLY' if not errors else 'FAIL',errors=errors,source_occurrences=model['source_occurrences'],recurrent_occurrences=model['recurrent_occurrences'],recurrent_types=len(model['recurrent_atoms']),singleton_runs=model['singleton_runs'],zero_gap_seams=model['adjacent_recurrent_pairs'],target_text_opened=False)
  (E/'artifacts/SOURCE_VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out));return int(bool(errors))
 lock=json.loads((E/'PREREG_LOCK.json').read_text())
 for path,h in lock['files'].items():
  if hashlib.sha256((R/path).read_bytes()).hexdigest()!=h:errors.append('registration_hash:'+path)
 pred=json.loads((E/'artifacts/PARTITION_PREDICTIONS.json').read_text());rows=loadgz(E/'artifacts/PARTITION_RESULTS.json.gz');base=loadgz(OLD/'artifacts/CANDIDATES.json.gz');prior=loadgz(LAST/'artifacts/CASES.json.gz');dom=json.loads((OLD/'artifacts/DOMAINS.json').read_text());result=json.loads((E/'artifacts/RESULT.json').read_text());spec=json.loads((E/'src/SPEC.json').read_text())
 expected=collections.defaultdict(list)
 for i,(c,old) in enumerate(zip(base,prior)):
  if old['status']=='PARTIAL_FOUR_ATOM_WITNESS':expected[c['edition'],c['iris_page']].append(i)
 if [(p['edition'],p['iris_page'],p['base_ids']) for p in pred]!=[(ed,page,ids) for (ed,page),ids in sorted(expected.items())]:errors.append('partition_completeness')
 if [r['id'] for r in rows]!=list(range(len(pred))) or len(rows)!=spec['expected_partitions']:errors.append('result_partition_coverage')
 if any(x['page'].startswith('f84') or x['page']=='f116v' for rs in dom.values() for xs in rs.values() for x in xs):errors.append('forbidden_target')
 statuses={'SAT_RECURRENT_PROJECTION','UNSAT_SOLVER','UNSAT_EMPTY_DOMAIN','UNSAT_NONEMPTY_LENGTH','UNKNOWN_SOLVER','UNKNOWN_PROCESS_WALL','UNKNOWN_GLOBAL_WALL','ERROR_SOLVER_PROCESS','ERROR_RUNNER'};readings=[]
 for part,row in zip(pred,rows):
  if row['status'] not in statuses:errors.append('unknown_status')
  if row['status'] in {'SAT_RECURRENT_PROJECTION','UNSAT_SOLVER','UNKNOWN_SOLVER'} and row.get('version')!=spec['cvc5_version']:errors.append('solver_version')
  if row['status']=='SAT_RECURRENT_PROJECTION':
   es,al=witness_check(model,dom[part['edition']],row,part,base);errors.extend(str(part['id'])+':'+x for x in es);readings.extend(dict(partition=part['id'],**a) for a in al)
 partition_of={i:p['id'] for p in pred for i in p['base_ids']};expected_table=[]
 for i,c in enumerate(base):
  pid=partition_of.get(i);row=rows[pid] if pid is not None else None;status='INHERITED_GDT977_CONTRADICTION'
  if row:
   if row['status'].startswith('UNSAT'):status='EXCLUDED_BY_RECURRENT_PARTITION'
   elif row['status']=='SAT_RECURRENT_PROJECTION':status='WITNESSED_RECURRENT_CODE' if row['witnessed_base_id']==i else 'UNCLASSIFIED_IN_SAT_PARTITION'
   else:status='UNRESOLVED_'+row['status']
  expected_table.append([str(i),*[c[k] for k in ['edition','iris_page','xiphion_page','iris_code','xiphion_code']],str(pid) if pid is not None else '',status])
 with (E/'artifacts/BASE_CASE_RESULTS.tsv').open() as f:table=list(csv.reader(f,delimiter='\t'))
 if table[1:]!=expected_table:errors.append('base_case_table')
 counts=dict(collections.Counter(x['status'] for x in rows));status='RECURRENT_PARTIAL_WITNESS_FOUND' if counts.get('SAT_RECURRENT_PROJECTION') else 'ALL_RECURRENT_PARTITIONS_EXCLUDED' if all(x['status'].startswith('UNSAT') for x in rows) else 'BOUNDED_RECURRENT_SEARCH_UNRESOLVED'
 fields=dict(status=status,partitions=len(rows),partition_counts=counts,base_counts=dict(collections.Counter(x[-1] for x in expected_table)),tested_base_rows=len(partition_of),original_base_rows=len(base),recurrent_types=78,recurrent_occurrences=358,singleton_occurrences=255,zero_gap_recurrent_seams=208,full_code_tested=False,confirmed_words=0,independent_confirmation_leaves=0,reserve_access=False)
 errors.extend('RESULT:'+k for k,v in fields.items() if result.get(k)!=v)
 out=dict(status='PASS' if not errors else 'FAIL',errors=errors,checked_partitions=len(rows),checked_base_rows=len(base),checked_sat_witnesses=counts.get('SAT_RECURRENT_PROJECTION',0),solver_unsat_count=counts.get('UNSAT_SOLVER',0),independent_unsat_proof=False,source_counts_checked=True,claim_ceiling='Ground reconstruction/source/coverage check; solver UNKNOWN/UNSAT not independently decided; no semantic evidence')
 (E/'artifacts/WITNESS_ALIGNMENTS.json').write_text(json.dumps(readings,ensure_ascii=False,indent=2)+'\n');(E/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return int(bool(errors))
if __name__=='__main__':raise SystemExit(main())
