from pathlib import Path
from datetime import datetime,timezone
from collections import Counter,defaultdict
import gzip,json,hashlib,time
from model import models,direct,select
D=Path('experiments/yolo/gdt1237_one_compound_letter_exceptions');A=D/'artifacts'


def main():
    started=time.monotonic();s=json.loads((D/'src/SPEC.json').read_text());lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
    for p,h in lock['files'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
    groups=json.loads(gzip.decompress(Path(s['source']).read_bytes()));M=models(s['signs']);assert len(M)==946
    (A/'CODEBOOKS.json').write_text(json.dumps(M,indent=2)+'\n')
    result={'status':'COMPLETE_EXCEPTION_ACTIVITY_DIAGNOSTIC','outcome_utc':datetime.now(timezone.utc).isoformat(),'readers':{}}
    for reader in s['readers']:
        rows=groups[reader];counts=Counter(tuple(r['units'])for r in rows);ids=defaultdict(list);pages=defaultdict(set)
        for r in rows:ids[tuple(r['units'])].append(r['id']);pages[tuple(r['units'])].add(r['page'])
        W=sorted(counts,key=lambda w:(len(w),w));by_sign={g:[i for i,w in enumerate(W)if g in w]for g in s['signs']}
        word_table=[{'units':list(w),'count':counts[w],'pages':sorted(pages[w]),'source_ids':ids[w]}for w in W]
        records=[]
        for m in M:
            failed=[];active=[];uses=0;g=m['missing_singleton']
            for i in by_sign[g]:
                n=direct(W[i],m)
                if n is None:failed.append(i)
                else:
                    assert n>0;active.append(i);uses+=n*counts[W[i]]
            records.append({**m,'failed_type_indices':failed,'active_type_indices':active,
                            'failed_tokens':sum(counts[W[i]]for i in failed),'failed_types':len(failed),
                            'active_tokens':sum(counts[W[i]]for i in active),'active_types':len(active),
                            'compound_occurrences':uses,'unchanged_singleton_tokens':sum(counts[w]for w in W if g not in w)})
            if time.monotonic()-started>s['runtime_seconds']:raise TimeoutError('runner runtime cap')
        packet={'words':word_table,'models':records}
        (A/('ACCOUNT_'+reader+'.json.gz')).write_bytes(gzip.compress(json.dumps(packet,separators=(',',':')).encode(),mtime=0))
        result['readers'][reader]={'tokens':len(rows),'types':len(W),'summary':select(records,len(rows),s['activity_percentages'])}
    (A/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print({reader:{'minimum':v['summary']['active_at_least_one'],'activity':v['summary']['activity_percentages']}for reader,v in result['readers'].items()})

if __name__=='__main__':main()
