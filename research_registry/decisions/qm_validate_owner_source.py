"""Reproduce a bounded selector-first source correction propagation audit."""
import argparse,csv,hashlib,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];D=R/'research_registry/decisions';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();enc=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args();s=json.loads((D/'qm_owner_source_spec.json').read_text());out=[];receipts=[]
for path,h in s['auxiliary_hashes'].items():assert sha(R/path)==h
for source in s['sources']:
 assert sha(R/source['path'])==source['sha256'];cmd=['./vmanus-exp','query-tsv',source['path'],'--selector',source['selector']]
 for value in s['allow_values']:cmd+=['--allow',value]
 cmd+=['--columns',','.join(source['columns'])]
 for prefix in s['forbidden_prefixes']:cmd+=['--forbid-prefix',prefix]
 q=subprocess.run(cmd,cwd=R,check=True,text=True,capture_output=True);stats=[json.loads(x[12:])for x in q.stderr.splitlines()if x.startswith('GUARD_STATS ')];assert len(stats)==1 and stats[0]['selected']==74
 rows=list(csv.DictReader(q.stdout.splitlines(),delimiter='\t'));assert len(rows)==74 and all(row['page']=='f67r2'for row in rows)
 selected={row[source['locus_field']]:row for row in rows if row[source['locus_field']]in s['target_loci']};assert set(selected)==set(s['target_loci'])
 for locus in s['target_loci']:out.append({'source_name':source['name'],'source_path':source['path'],'source_sha256':source['sha256'],'locus':locus,'selected_fields':selected[locus]})
 receipts.append({'source':source['path'],'command':cmd,'guard_stats':stats[0],'projection_sha256':hashlib.sha256(q.stdout.encode()).hexdigest(),'retained_target_rows':3})
packet=json.loads((D/'qk_v75_f67_applications.json').read_text());source=R/packet['source_file'];assert sha(source)==packet['source_sha256'];lines=source.read_text().splitlines();line=lines[packet['source_line']-1];records=packet['records'];assert [x['locus']for x in records]==[f'f67r2.{i}'for i in range(1,75)]
for x in records:
 assert x['original_line']==packet['source_line'] and line[x['start_offset']:x['end_offset']]==x['exact_source_record'];assert x['exact_source_record']==f"[{x['locus']} | {x['namespace']}] {x['exact_source_description']}"
assert packet['coverage_verified']['prefix']+' '.join(x['exact_source_record']for x in records)==line
corrections=json.loads((R/'experiments/yolo/gdt876_f67r2_long_record_placement/artifacts/CORRECTIONS.json').read_text())['records'];assert len(corrections)==3 and all(x['agreed_written_region']=='RIGHT_BELOW_HORIZONTAL'for x in corrections)
for locus,expected in [('f67r2.72','A1_LEFT_OUTER_RING_TEXT'),('f67r2.73','A1_RIGHT_OUTER_RING_TEXT'),('f67r2.74','A1_PAIRED_WHEEL_LEGEND_UNRESOLVED')]:
 rr=[x['selected_fields']for x in out if x['locus']==locus];assert rr[0]['selected_visible_owner']==rr[1]['local_namespace_owner']==expected;assert rr[0]['visible_basis']==rr[1]['visible_basis'] and rr[0]['owner_status']==rr[1]['owner_status']
projection=''.join(enc(x)+'\n'for x in out);receipt=json.dumps(receipts,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
if args.write:(D/'qm_owner_projection.jsonl').write_text(projection);(D/'qm_guard_receipts.json').write_text(receipt)
else:assert (D/'qm_owner_projection.jsonl').read_text()==projection and (D/'qm_guard_receipts.json').read_text()==receipt
v={'status':'PASS','guarded_sources':2,'selected_source_rows':148,'retained_target_rows':6,'distinct_target_loci':3,'inherited_wrong_definite_placements':2,'exact_historical_context_applications':74,'new_manuscript_observations':0,'semantic_truth_validated':False,'scope':'Exact source inheritance and lossless authored-application extraction only; native observations remain GDT876.'};(D/'qm_source_validation.json').write_text(json.dumps(v,sort_keys=True,indent=2)+'\n');print(json.dumps(v))
