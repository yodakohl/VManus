"""Exact registered f100r guarded source acquisition; no imaging or inference."""
import argparse,csv,hashlib,io,json,subprocess
from pathlib import Path
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]
REQUESTS=[('experiments/semantic_assumptions/results/source_separator_transcription.tsv','RAW_GROUPS.tsv',['edition','locus','page','code','kind','source_group_index','source_group_count','left_separator','right_separator','ivtff_group_raw','clean_ascii_fragments','legacy_mapping_status']),('experiments/yolo/gdt391_local_object_relation_normalization/artifacts/gdt391_complete_unit_frame.tsv','SOURCE_FRAME.tsv',['page','locus','array_id','source_visual_detail','source_provenance','source_id','source_relation_state'])]
def query(source,columns,allow):
 cmd=['./vmanus-exp','query-tsv',source,'--selector','page']
 for v in allow:cmd+=['--allow',v]
 cmd+=['--columns',','.join(columns),'--forbid-prefix','f84','--forbid-prefix','f84r']
 p=subprocess.run(cmd,cwd=ROOT,capture_output=True,check=True)
 rows=csv.DictReader(io.StringIO(p.stdout.decode()),delimiter='\t'); assert rows.fieldnames==columns
 data=list(rows); assert all(r['page'] in allow and not r['page'].startswith('f84') for r in data)
 stats=[json.loads(x.removeprefix('GUARD_STATS ')) for x in p.stderr.decode().splitlines() if x.startswith('GUARD_STATS ')]
 assert len(stats)==1 and stats[0]['selected']==len(data)
 return p.stdout,dict(command=cmd,stats=stats[0],rows=len(data),projection_sha256=hashlib.sha256(p.stdout).hexdigest())
def controls():
 p=E/'runtime/guard_fixture.tsv';p.parent.mkdir(exist_ok=True)
 p.write_text('page\tpayload\nfixture_a\talpha\nfixture_b\tbeta\nf84r\tSEALED\nfixture_c\tOUTSIDE\n')
 raw,meta=query(str(p.relative_to(ROOT)),['page','payload'],['fixture_a','fixture_b'])
 assert list(csv.DictReader(io.StringIO(raw.decode()),delimiter='\t'))==[{'page':'fixture_a','payload':'alpha'},{'page':'fixture_b','payload':'beta'}]
 assert b'SEALED' not in raw and b'OUTSIDE' not in raw
 return dict(status='PASS',actual_guard_two_allow_values=True,forbidden_and_unselected_absent=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');p.add_argument('--run',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args()
 if a.controls:
  result=controls();(E/'artifacts/CONTROLS.json').write_text(json.dumps(result,sort_keys=True)+'\n');print(json.dumps(result));return
 if not(a.run or a.check):p.error('Explicit --run or --check required after public GO')
 records=[]
 for source,name,columns in REQUESTS:
  raw,meta=query(source,columns,['f100r']);records.append(dict(artifact=name,**meta));dest=E/'artifacts'/name
  if a.check:assert dest.read_bytes()==raw,name
  else:dest.write_bytes(raw)
 payload=json.dumps(dict(status='SOURCE_ACQUISITION_COMPLETE',queries=records),sort_keys=True,indent=2)+'\n';dest=E/'artifacts/QUERY_STATS.json'
 if a.check:assert dest.read_text()==payload
 else:dest.write_text(payload)
 print(json.dumps(dict(status='REPLAY_PASS' if a.check else 'SOURCE_ACQUISITION_COMPLETE',rows=[r['rows'] for r in records])))
if __name__=='__main__':main()
