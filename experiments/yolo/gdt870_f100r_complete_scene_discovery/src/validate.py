"""Independent guarded byte replay and original-file identity; no raster decode."""
import argparse,csv,hashlib,io,json,subprocess
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
SOURCES={'RAW_GROUPS.tsv':('experiments/semantic_assumptions/results/source_separator_transcription.tsv','edition,locus,page,code,kind,source_group_index,source_group_count,left_separator,right_separator,ivtff_group_raw,clean_ascii_fragments,legacy_mapping_status'),'SOURCE_FRAME.tsv':('experiments/yolo/gdt391_local_object_relation_normalization/artifacts/gdt391_complete_unit_frame.tsv','page,locus,array_id,source_visual_detail,source_provenance,source_id,source_relation_state')}
def fetch(path,columns,allowed):
 args=['./vmanus-exp','query-tsv',path,'--selector','page','--columns',columns,'--forbid-prefix','f84','--forbid-prefix','f84r']
 for item in allowed:args.extend(['--allow',item])
 process=subprocess.run(args,cwd=ROOT,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 reader=csv.DictReader(io.StringIO(process.stdout.decode()),delimiter='\t');assert reader.fieldnames==columns.split(',');rows=list(reader)
 assert all(row['page'] in allowed and not row['page'].startswith('f84') for row in rows)
 stats=[json.loads(line[12:]) for line in process.stderr.decode().splitlines() if line.startswith('GUARD_STATS ')]
 assert len(stats)==1 and stats[0]['selected']==len(rows)
 return process.stdout,rows,stats[0]
def controls():
 path=E/'runtime/independent_guard_fixture.tsv';path.parent.mkdir(exist_ok=True);path.write_text('page\tpayload\ncontrol_b\tB\nf84\tFORBIDDEN\ncontrol_c\tC\ncontrol_a\tA\nf84r\tFORBIDDEN\n')
 raw,rows,_=fetch(str(path.relative_to(ROOT)),'page,payload',['control_a','control_b'])
 assert rows==[dict(page='control_b',payload='B'),dict(page='control_a',payload='A')];assert b'FORBIDDEN' not in raw
 return dict(status='PASS',independent_actual_guard_two_allow_values=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');a=p.parse_args()
 if a.controls:print(json.dumps(controls()));return
 recorded=json.loads((E/'artifacts/QUERY_STATS.json').read_text());checks=[]
 for name,(path,columns) in SOURCES.items():
  raw,rows,stats=fetch(path,columns,['f100r']);assert raw==(E/'artifacts'/name).read_bytes(),name
  entry=next(q for q in recorded['queries'] if q['artifact']==name)
  assert entry['stats']==stats and entry['rows']==len(rows) and entry['projection_sha256']==hashlib.sha256(raw).hexdigest()
  checks.append(dict(artifact=name,rows=len(rows),byte_parity=True))
 image=ROOT/'experiments/yolo/gdt861_extended_entity_native_comparison/runtime/1006248.jpg';assert image.stat().st_size==2278638
 h=hashlib.sha256()
 with image.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 assert h.hexdigest()=='6dcf72a0d7eac14da2232987c9cc1521e6d70c9f0f92d3eb39b55fc075520429'
 result=dict(status='PASS',sources=checks,image_sha256=h.hexdigest(),image_bytes=2278638,image_decoded=False,native_observations_validated=False)
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
