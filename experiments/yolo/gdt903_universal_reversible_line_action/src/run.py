#!/usr/bin/env python3
import gzip,hashlib,json,re,time
from pathlib import Path
from fold import fold
BASE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    started=time.monotonic();sp=BASE/'artifacts/SOURCE_LINES.json'
    assert sha(sp)=='bd8b58523e4e49754f4e49e3901f00ecef748679d90ac46184e453294c8753c2'
    rows=json.loads(sp.read_text());assert len(rows)==413 and len({r['locus'] for r in rows})==413
    assert all(not r['page'].startswith('f84') and int(re.match(r'f(\d+)',r['page']).group(1))%2 for r in rows)
    words=[r['literal'] for r in rows];alphabet=sorted(set(''.join(words)));assert alphabet==list('acdefghiklmnopqrstxy')
    out={'schema':'GDT903_UNIVERSAL_REVERSIBLE_ACTION_RESULT_V1','source_sha256':sha(sp),'code_sha256':sha(BASE/'src/fold.py'),'runner_sha256':sha(Path(__file__)),'alphabet':alphabet,'line_count':413,'reference_locus':'f19r.8','budget_seconds':600}
    try:
        r,log=fold(words,alphabet,started+600);out.update(r)
        lp=BASE/'artifacts/FOLD_LOG.json.gz';lp.write_bytes(gzip.compress((json.dumps(log,separators=(',',':'))+'\n').encode(),mtime=0));out['fold_log_sha256']=sha(lp)
        core=r['core'];out['core_rank']=len(core['edges'])-core['vertices']+1
        out['core_complete_cover']=len(core['edges'])==len(alphabet)*core['vertices']
        out['subgroup_index']=core['vertices'] if out['core_complete_cover'] else 'INFINITE'
        out['status']='ALL_STATE_COUNTS_ONLY_TRIVIAL_ORBIT' if r['full_group'] else 'PROPER_SUBGROUP_EXPLICIT_FINITE_COMPATIBILITY'
    except TimeoutError:out['status']='UNKNOWN_BUDGET'
    out['elapsed_seconds']=time.monotonic()-started;out['claim_ceiling']='Exact fixed literal/wholeline/reversible/commonendpoint conjunction; arbitrary finite witness is not an identified historical model or meaning.'
    (BASE/'artifacts/FOLD_RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['status','elapsed_seconds','initial_vertices','initial_edges','union_count','core_rank','subgroup_index'] if k in out}))
if __name__=='__main__':main()
