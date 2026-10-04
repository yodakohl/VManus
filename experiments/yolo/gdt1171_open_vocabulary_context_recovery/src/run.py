"""One exact supplied-rule source comparison. No answer file is opened here."""
import argparse
import collections as C
import concurrent.futures
import functools
import math
import random
import subprocess
from common import *


class Model:
    def __init__(self, records, alphabet, arm):
        self.alphabet = alphabet
        self.counts = {}
        rng = random.Random(1171)
        for words in records:
            words = list(words)
            if arm == 'S':
                rng.shuffle(words)
            streams = [w + ' ' for w in words] if arm == 'U' else [' '.join(words) + ' ']
            for stream in streams:
                h = START
                for ch in stream:
                    assert ch in alphabet
                    for length in range(5):
                        key = h[-length:] if length else ''
                        self.counts.setdefault(key, C.Counter())[ch] += 1
                    h = (h + ch)[-4:]
        self.totals = {h:sum(c.values()) for h,c in self.counts.items()}
        self.advance = functools.lru_cache(maxsize=400000)(self._advance)

    def _advance(self, history, text):
        score = 0.
        for char in text:
            h = history
            while h not in self.counts:
                h = h[1:]
            score += math.log((self.counts[h].get(char,0)+.1)/(self.totals[h]+.1*len(self.alphabet)))
            history = (history+char)[-4:]
        return history, score


def decode(words, model, classes):
    nodes = [(None, None, '')]
    states = {START:(0.,0)}
    peak = 1
    for word in words:
        emissions = [(alternatives(ch,classes),word['id']) for ch in word['native']]
        emissions.append(([' '],None))
        for outputs, owner in emissions:
            next_states = {}
            for history in sorted(states):
                prior, node = states[history]
                for out in outputs:
                    h, value = model.advance(history,out)
                    value += prior
                    if h not in next_states or value > next_states[h][0]:
                        nodes.append((node,owner,out))
                        next_states[h] = (value,len(nodes)-1)
            states = next_states
            peak = max(peak,len(states))
            if len(states)>100000 or len(nodes)>20000000:
                raise RuntimeError('Fixed exact-search resource stop; no beam fallback')
    end = min(states,key=lambda h:(-states[h][0],h))
    score,node = states[end]
    output = {w['id']:[] for w in words}
    while node:
        node,owner,text = nodes[node]
        if owner is not None:
            output[owner].append(text)
    return {k:''.join(reversed(v)) for k,v in output.items()}, score, peak


def fold(book):
    data = load(EXP/f'artifacts/INPUT_{book}.json.gz')
    reference = load(EXP/f'artifacts/REFERENCE_{book}.json.gz')['segments']
    rules = load(EXP/'artifacts/RULES.json')
    alphabet = set(' ')
    alphabet.update(''.join(w for s in reference for w in s))
    for w in data:
        for ch in w['native'] or '':
            alphabet.update(''.join(alternatives(ch,rules)))
    assert '\x02' not in alphabet
    alphabet = sorted(alphabet)
    result = dict(book=book, alphabet=alphabet, arms={})
    for arm in ARMS:
        model = Model(reference,alphabet,arm)
        predictions = {w['id']:None for w in data}
        units = [[w] for w in data if w['native'] is not None] if arm=='U' else segments(data,'native')
        scores,peak = [],1
        for unit in units:
            p,s,k = decode(unit,model,rules)
            predictions.update(p);scores.append(s);peak=max(peak,k)
        result['arms'][arm] = dict(predictions=predictions, unit_scores=scores,
                                   peak_states=peak, model_hash=objhash(model.counts))
        model.advance.cache_clear()
        print(book,arm,'complete',flush=True)
    save(EXP/f'artifacts/PREDICTIONS_{book}.json.gz',result)
    return book


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--release',required=True)
    args=parser.parse_args()
    assert not (EXP/'artifacts/PREDICTION_LOCK.json').exists(),'Existing predictions are immutable'
    lock=load(EXP/'artifacts/PREREG_LOCK.json')
    for path,h in lock['files'].items():
        assert sha(ROOT/path)==h,path
    assert subprocess.check_output(['git','rev-parse',args.release]).decode().strip()==args.release
    prefix=EXP.relative_to(ROOT).as_posix()
    for path,h in lock['files'].items():
        blob=subprocess.check_output(['git','show',args.release+':'+path])
        import hashlib
        assert hashlib.sha256(blob).hexdigest()==h,path
    with concurrent.futures.ProcessPoolExecutor(max_workers=6) as pool:
        assert sorted(pool.map(fold,BOOKS))==sorted(BOOKS)
    save(EXP/'artifacts/PREDICTION_LOCK.json',dict(prereg_commit=args.release,
         prereg_lock_sha256=sha(EXP/'artifacts/PREREG_LOCK.json'),
         files={f'PREDICTIONS_{b}.json.gz':sha(EXP/f'artifacts/PREDICTIONS_{b}.json.gz') for b in BOOKS}))
    print('All predictions locked; no held answers opened by this runner.')


if __name__=='__main__':
    main()
