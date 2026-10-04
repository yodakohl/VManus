"""Exact answer accounting after the prediction lock."""
import collections as C
import statistics
from common import *


def metrics(rows):
    out={}
    for panel in ('NOVEL','NOVEL_OOV','SHARED','SELECTED','ALL'):
        pick=[r for r in rows if panel=='ALL' or (r['selected'] and (
            panel=='SELECTED' or panel=='NOVEL_OOV' and r['partition']=='NOVEL' and r['oov']
            or panel==r['partition']))]
        types=C.defaultdict(list)
        for r in pick:
            if r['native'] is not None:
                types[r['native']].append(r)
        out[panel]=dict(n=len(pick),types=len(types),
            correct={a:sum(r['correct'][a] for r in pick) for a in ARMS},
            type_accuracy={a:statistics.mean([statistics.mean(r['correct'][a] for r in group)
                                              for group in types.values()]) if types else None for a in ARMS})
    return out


def main():
    lock=load(EXP/'artifacts/PREDICTION_LOCK.json')
    for name,h in lock['files'].items(): assert sha(EXP/'artifacts'/name)==h
    gold=load(EXP/'artifacts/GOLD.json.gz');rows=[];bookmetrics={};records={}
    for book in BOOKS:
        p=load(EXP/f'artifacts/PREDICTIONS_{book}.json.gz')['arms']
        ref=load(EXP/f'artifacts/REFERENCE_{book}.json.gz')
        raw=set(ref['raw_types']);vocab={w for s in ref['segments'] for w in s}
        br=[]; rec=C.defaultdict(list)
        for g in gold[book]:
            pred={a:p[a]['predictions'][g['id']] for a in ARMS}
            r=dict(g,book=book,partition=('UNKNOWN_WRITTEN' if g['native'] is None else
                   'SHARED' if g['native'] in raw else 'NOVEL'),oov=g['gold'] is not None and g['gold'] not in vocab,
                   predictions=pred,correct={a:g['gold'] is not None and pred[a]==g['gold'] for a in ARMS})
            br.append(r)
            rec[g['record'] if g['record'] is not None else g['id']].append(r)
        rows.extend(br);bookmetrics[book]=metrics(br)
        records[book]=dict(total=len(rec),correct={a:sum(all(r['correct'][a] for r in group)
                                for group in rec.values()) for a in ARMS})
    primary={a:statistics.mean(bookmetrics[b]['NOVEL']['type_accuracy'][a] for b in BOOKS) for a in ARMS}
    oov={a:statistics.mean(bookmetrics[b]['NOVEL_OOV']['type_accuracy'][a] for b in BOOKS) for a in ARMS}
    wins={a:sum(bookmetrics[b]['NOVEL']['type_accuracy']['C']>bookmetrics[b]['NOVEL']['type_accuracy'][a]
               for b in BOOKS) for a in ('U','S')}
    gates=dict(accuracy=primary['C']>=.70,
               context_increment=primary['C']-primary['U']>=.03 and wins['U']>=4,
               order_increment=primary['C']-primary['S']>=.02 and wins['S']>=4,
               novel_oov=oov['C']>=.50)
    # Pooled type weighting keeps book identity; do not merge identical shared forms across books.
    pooled=metrics([dict(r,native=r['book']+'\0'+r['native'] if r['native'] is not None else None) for r in rows])
    result=dict(status='CONDITIONAL_SOURCE_RECOVERY_PASS' if all(gates.values()) else 'NO_USEFUL_OPEN_CONTEXT_RECOVERY',
                primary=primary,novel_oov=oov,wins=wins,gates=gates,books=bookmetrics,pooled=pooled,records=records,
                prediction_lock_sha256=sha(EXP/'artifacts/PREDICTION_LOCK.json'))
    save(EXP/'artifacts/SCORED_ROWS.json.gz',rows);save(EXP/'artifacts/RESULT.json',result)
    print(json.dumps({k:result[k] for k in ('status','primary','novel_oov','wins','gates')},indent=2))


if __name__=='__main__':
    main()
