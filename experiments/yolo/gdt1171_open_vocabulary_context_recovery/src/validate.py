"""Independent counts, Viterbi replay, rule membership and exact accounting."""
import argparse
import collections as C
import concurrent.futures
import itertools
import math
import random
import re
import statistics
from common import *


def counts_for(reference,arm):
    rng=random.Random(1171); table=C.defaultdict(C.Counter)
    for segment in reference:
        sequence=list(segment)
        if arm=='S': rng.shuffle(sequence)
        samples=[word+' ' for word in sequence] if arm=='U' else [' '.join(sequence)+' ']
        for sample in samples:
            padded=START+sample
            for j in range(4,len(padded)):
                for n in range(5): table[padded[j-n:j]][padded[j]]+=1
    return dict(table)


def step(table,size,history,string):
    likelihood=0.
    for char in string:
        keys=[history[k:] for k in range(len(history)+1)]
        ctx=next(key for key in keys if key in table)
        counts=table[ctx]
        likelihood+=math.log((counts.get(char,0)+.1)/(sum(counts.values())+.1*size))
        history=(history+char)[-4:]
    return history,likelihood


def replay(words,table,size,rules):
    # Full edge layers, separate from runner's global node pool.
    import functools
    advance=functools.lru_cache(maxsize=100000)(lambda h,t:step(table,size,h,t))
    levels=[]; current={START:0.}
    for word in words:
        choices=[(sorted(set(rules[ch]['alternatives'])) if ch in rules else [ch],word['id'])
                 for ch in word['native']]+[([' '],None)]
        for options,owner in choices:
            after={};links={}
            for h in sorted(current):
                for s in options:
                    dest,weight=advance(h,s);score=current[h]+weight
                    if dest not in after or score>after[dest]:
                        after[dest]=score;links[dest]=(h,owner,s)
            levels.append(links);current=after
    h=min(current,key=lambda key:(-current[key],key));score=current[h]
    emitted={w['id']:[] for w in words}
    for links in reversed(levels):
        h,owner,s=links[h]
        if owner is not None: emitted[owner].append(s)
    return {k:''.join(v[::-1]) for k,v in emitted.items()},score


def fixtures():
    import run as production  # ONLY synthetic fixtures; full validator never calls its model/decoder.
    rules={'X':{'alternatives':['','a','ab','a']},'Y':{'alternatives':['b','ba']}}
    ref=[['ab','ba'],['a','bb'],['aa','ab']]
    alphabet=list('ab ');checks=0
    for arm in ARMS:
        model=production.Model(ref,alphabet,arm);table=counts_for(ref,arm)
        assert dict(model.counts)==table;checks+=1
        for h in list(table)+['bbbb']:
            probs=[math.exp(step(table,len(alphabet),h,c)[1]) for c in alphabet]
            assert abs(sum(probs)-1)<1e-12
        checks+=1
        words=[dict(id='a',native='XY'),dict(id='b',native='Y')]
        units=[[w] for w in words] if arm=='U' else [words]
        for unit in units:
            got,score,_=production.decode(unit,model,rules)
            other,value=replay(unit,table,len(alphabet),rules)
            assert got==other and abs(score-value)<1e-12
            perword=[sorted(set(''.join(t) for t in itertools.product(*[
                rules[ch]['alternatives'] for ch in w['native']]))) for w in unit]
            best=-math.inf
            for seq in itertools.product(*perword):
                h=START;total=0.
                for word in seq:
                    h,s=step(table,len(alphabet),h,word+' ');total+=s
                best=max(best,total)
            assert abs(best-score)<1e-12
            assert production.decode(unit,model,rules)[0]==got;checks+=3
        assert math.isfinite(step(table,len(alphabet),START,'baba ')[1]);checks+=1
    # Across-word histories can distinguish the rank of unseen words: boundary changes remain measurable.
    assert counts_for(ref,'C')!=counts_for(ref,'U')
    save(EXP/'artifacts/FIXTURE_VALIDATION.json',dict(status='PASS',checks=checks+1,
         scope='invented fixtures only; exhaustive alternatives, normalization, empty outputs and repeatability'))
    print('Synthetic independent checks:',checks+1)


def validate_fold(book):
    data=load(EXP/f'artifacts/INPUT_{book}.json.gz')
    ref=load(EXP/f'artifacts/REFERENCE_{book}.json.gz')['segments']
    rules=load(EXP/'artifacts/RULES.json')
    saved=load(EXP/f'artifacts/PREDICTIONS_{book}.json.gz')
    alpha={' '}
    for record in ref:
        for word in record: alpha.update(word)
    for word in data:
        for ch in word['native'] or '':
            for alternative in rules.get(ch,{'alternatives':[ch]})['alternatives']: alpha.update(alternative)
    assert saved['alphabet']==sorted(alpha)
    for arm in ARMS:
        table=counts_for(ref,arm)
        assert objhash(table)==saved['arms'][arm]['model_hash']
        units=[[w] for w in data if w['native'] is not None] if arm=='U' else segments(data,'native')
        pred={w['id']:None for w in data};scores=[]
        for unit in units:
            p,s=replay(unit,table,len(alpha),rules);pred.update(p);scores.append(s)
        assert pred==saved['arms'][arm]['predictions'],(book,arm)
        assert len(scores)==len(saved['arms'][arm]['unit_scores'])
        assert all(abs(a-b)<1e-8 for a,b in zip(scores,saved['arms'][arm]['unit_scores']))
        for w in data:
            if w['native'] is not None:
                pattern=''.join('(?:'+'|'.join(re.escape(s) for s in rules.get(ch,{'alternatives':[ch]})['alternatives'])+')'
                                for ch in w['native'])
                assert re.fullmatch(pattern,pred[w['id']]) is not None
        print(book,arm,'independent replay PASS',flush=True)
    return dict(book=book,groups=len(data),arms=3)


def independent_metrics(rows):
    output={}
    for panel in ('NOVEL','NOVEL_OOV','SHARED','SELECTED','ALL'):
        picked=[]
        for r in rows:
            if panel=='ALL': picked.append(r)
            elif r['selected']:
                if panel=='SELECTED' or panel==r['partition'] or (panel=='NOVEL_OOV' and r['partition']=='NOVEL' and r['oov']): picked.append(r)
        grouped=C.defaultdict(list)
        for r in picked:
            if r['native'] is not None: grouped[r['native']].append(r)
        output[panel]={'n':len(picked),'types':len(grouped),'correct':{},'type_accuracy':{}}
        for a in ARMS:
            output[panel]['correct'][a]=sum(r['correct'][a] for r in picked)
            output[panel]['type_accuracy'][a]=statistics.mean([sum(r['correct'][a] for r in group)/len(group)
                                                for group in grouped.values()]) if grouped else None
    return output


def full():
    prereg=load(EXP/'artifacts/PREREG_LOCK.json')
    for p,h in prereg['files'].items(): assert sha(ROOT/p)==h,p
    lock=load(EXP/'artifacts/PREDICTION_LOCK.json')
    for p,h in lock['files'].items(): assert sha(EXP/'artifacts'/p)==h,p
    with concurrent.futures.ProcessPoolExecutor(max_workers=6) as pool: checks=list(pool.map(validate_fold,BOOKS))
    # Prepared source projection replay, reusing the pinned projector but not prepare.py.
    import sys
    sys.path.insert(0,str(PACKET));import feasibility
    original,_=feasibility.source_groups()
    gold=load(EXP/'artifacts/GOLD.json.gz')
    expanded={}
    for b,groups in original.items():
        expanded[b]=[dict(w,gold=w['expanded'] if '\uFFFC' not in w['expanded'] else None) for w in groups]
        byid={w['id']:w for w in groups}
        for r in gold[b]:
            w=byid[r['id']]
            assert r['gold']==(w['expanded'] if '\uFFFC' not in w['expanded'] else None)
            assert r['native']==(None if None in w['native'] else ''.join(w['native']))
        inp=load(EXP/f'artifacts/INPUT_{b}.json.gz')
        assert inp==[{k:r[k] for k in ('id','record','locator','selected','native')} for r in gold[b]]
    for b in BOOKS:
        ref=load(EXP/f'artifacts/REFERENCE_{b}.json.gz')
        assert ref['segments']==[[w['gold'] for w in segment] for other in BOOKS if other!=b
                                  for segment in segments(expanded[other],'gold')]
        assert ref['raw_types']==sorted({r['native'] for other in BOOKS if other!=b
                                        for r in gold[other] if r['native'] is not None})
    rows=load(EXP/'artifacts/SCORED_ROWS.json.gz');result=load(EXP/'artifacts/RESULT.json')
    assert len(rows)==sum(len(g) for g in gold.values())==98720
    assert sum(r['selected'] for r in rows)==11724
    for book in BOOKS:
        ref=load(EXP/f'artifacts/REFERENCE_{book}.json.gz');native=set(ref['raw_types']);vocab={w for s in ref['segments'] for w in s}
        predictions=load(EXP/f'artifacts/PREDICTIONS_{book}.json.gz')['arms']
        rr=[r for r in rows if r['book']==book]
        assert [r['id'] for r in rr]==[g['id'] for g in gold[book]]
        records=C.defaultdict(list)
        for r,g in zip(rr,gold[book]):
            assert all(r[k]==v for k,v in g.items())
            assert r['partition']==('UNKNOWN_WRITTEN' if g['native'] is None else 'SHARED' if g['native'] in native else 'NOVEL')
            assert r['oov']==(g['gold'] is not None and g['gold'] not in vocab)
            for a in ARMS:
                assert r['predictions'][a]==predictions[a]['predictions'][r['id']]
                assert r['correct'][a]==(g['gold'] is not None and r['predictions'][a]==g['gold'])
            records[r['record'] if r['record'] is not None else r['id']].append(r)
        assert result['books'][book]==independent_metrics(rr)
        assert result['records'][book]==dict(total=len(records),correct={a:sum(all(r['correct'][a] for r in group) for group in records.values()) for a in ARMS})
    pooled=independent_metrics([dict(r,native=r['book']+'\0'+r['native'] if r['native'] is not None else None) for r in rows])
    assert pooled==result['pooled']
    p={a:statistics.mean(result['books'][b]['NOVEL']['type_accuracy'][a] for b in BOOKS) for a in ARMS}
    o={a:statistics.mean(result['books'][b]['NOVEL_OOV']['type_accuracy'][a] for b in BOOKS) for a in ARMS}
    wins={a:sum(result['books'][b]['NOVEL']['type_accuracy']['C']>result['books'][b]['NOVEL']['type_accuracy'][a] for b in BOOKS) for a in ('U','S')}
    gates=dict(accuracy=p['C']>=.70,context_increment=p['C']-p['U']>=.03 and wins['U']>=4,
               order_increment=p['C']-p['S']>=.02 and wins['S']>=4,novel_oov=o['C']>=.50)
    assert (p,o,wins,gates)==(result['primary'],result['novel_oov'],result['wins'],result['gates'])
    assert result['status']==('CONDITIONAL_SOURCE_RECOVERY_PASS' if all(gates.values()) else 'NO_USEFUL_OPEN_CONTEXT_RECOVERY')
    save(EXP/'artifacts/VALIDATION.json',dict(status='PASS',folds=checks,predicted_groups=98720*3,
         scored_groups=len(rows),selected=11724,result_sha256=sha(EXP/'artifacts/RESULT.json'),
         scope='independent model counts, all Viterbi selections, compatibility and metric arithmetic; shared source projector'))
    print('Full independent validation PASS')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--fixtures',action='store_true')
    if parser.parse_args().fixtures: fixtures()
    else: full()
