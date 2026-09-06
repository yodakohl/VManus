"""Replay a retrospective count audit; optional guarded reacquisition."""
import argparse,collections,csv,hashlib,io,json,re,subprocess
from pathlib import Path
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]
def read(p):return json.loads(p.read_text())
def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
 p=argparse.ArgumentParser();p.add_argument('--reacquire',action='store_true');p.add_argument('--check',action='store_true');args=p.parse_args()
 a=read(E/'src/SOURCE_AUDIT.json');spec=read(E/'src/SPEC.json')
 for path,h in a['input_sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
 paths=['experiments/yolo/gdt624_productive_quality_shell_grid/artifacts/PAGE_ALLOWLIST.tsv','experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv']
 # Selector-only closed inventories contain no text payload.
 pages=[set((ROOT/path).read_text().splitlines()[1:]) for path in paths]
 assert pages[0]==pages[1] and len(pages[0])==179 and not any(x.startswith('f84') for x in pages[0])
 hits=read(ROOT/'experiments/yolo/gdt845_extended_form_grid_discovery/artifacts/HITS.json')
 rx=re.compile(spec['raw_pattern']); current=collections.Counter((r['page'],r['locus'],r['ivtff_group_raw']) for r in hits if r['edition']=='ZL3b' and rx.fullmatch(r['ivtff_group_raw']))
 expected_oldonly=collections.Counter((r['page'],r['locus'],r['surface']) for r in a['case_evidence'])
 assert sum(current.values())==816 and sum(expected_oldonly.values())==13
 previous=read(ROOT/'experiments/yolo/gdt624_productive_quality_shell_grid/artifacts/RESULT.json')
 assert previous['grid']['occurrences']==829
 if args.reacquire:
  provenance=read(E/'src/QUERY_PROVENANCE.json'); queried=[]
  for q in provenance['initial_queries']:
   cmd=['./vmanus-exp','query-tsv',q['source'],'--selector',q['selector']]
   for page in sorted(q.get('allow_values',pages[0])):cmd+=['--allow',page]
   cmd+=['--columns',q['columns'],'--forbid-prefix','f84','--forbid-prefix','f84r']
   done=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True)
   stats=[json.loads(x.removeprefix('GUARD_STATS ')) for x in done.stderr.splitlines() if x.startswith('GUARD_STATS ')]
   assert stats==[q['guard_stats']]
   queried.append(list(csv.DictReader(io.StringIO(done.stdout),delimiter='\t')))
  legacy=collections.Counter((r['page'],r['locus'],r['surface']) for r in queried[0])
  assert legacy-current==expected_oldonly and not current-legacy
  for case in a['case_evidence']:
   selected=[r for r in queried[1] if r['edition']=='ZL3b' and r['locus']==case['locus'] and case['surface'] in r['clean_ascii_fragments']]
   assert selected==case['source_groups']
 result={'status':'COUNT_DIFFERENCE_FULLY_RECONCILED','design':spec['design'],'old_count':829,'exact_raw_count':sum(current.values()),'old_only':13,'raw_only':0,'category_counts':{k:len(v) for k,v in a['causes'].items()},'source_hashes_verified':True,'claim_ceiling':'Source counting correction only; inline metadata is not glyph uncertainty. Default replay uses cached initial source audit.'}
 target=E/'artifacts/RESULT.json'
 if args.check:assert read(target)==result
 else:dump(target,result)
 print(result['status']+(' REACQUISITION_VERIFIED' if args.reacquire else ' CACHED_REPLAY'))
if __name__=='__main__':main()
