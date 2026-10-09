#!/usr/bin/env python3
from pathlib import Path
from collections import Counter
import hashlib,json,re,math
import run,writers as w
D=Path(__file__).resolve().parents[1];A=D/'artifacts'
PAT=re.compile(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]')
def signs(word):
 gs=PAT.findall(word);assert ''.join(gs)==word;return gs

def main():
 result=json.loads((A/'RESULT.json').read_text());source=json.loads(run.SOURCE.read_text());dic=w.train(source)
 assert [e['source_word'] for e in json.loads((A/'DICTIONARY.json').read_text())['entries']]==dic
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((run.ROOT/p).read_bytes()).hexdigest()==h,p
 for mode in 'ABC':
  for col,rs in source.items():
   blocks=(A/f'{mode}_{col}.txt').read_text().strip().split('\n\n');assert len(blocks)==len(rs)
   reader=w.Reader(mode,dic);rewrite=w.Writer(mode,dic);segments=[]
   for block,r in zip(blocks,rs):
    printed=block.split();decoded=reader.paragraph([signs(z) for z in printed]);assert decoded==r['words']
    assert rewrite.paragraph(decoded)==printed,'Noncanonical or external-boundary dependent'
    segments.extend(line.split() for line in block.splitlines())
   flat=[x for line in segments for x in line][:8000];lengths=[len(signs(x)) for x in flat];c=Counter(flat);m=result['metrics'][mode][col]
   assert sum(lengths)/8000==m['mean_length'] and len(c)==m['types']
   assert sum(sorted(c.values(),reverse=True)[:10])/8000==m['top10_share']
   measured=run.m.measure(segments)
   for key,value in measured.items():
    if isinstance(value,float):assert math.isclose(value,m[key],rel_tol=0,abs_tol=1e-12),(key,value,m[key])
    else:assert value==m[key],key
 assert not result['passing_models']
 # Reference dynamics, unsupported digit, and literal-boundary ambiguity guards.
 reader=w.Reader('C',dic)
 try:reader.paragraph([['q','cfh','cfh']])
 except (AssertionError,IndexError):pass
 else:raise AssertionError('Unused long rank accepted')
 assert w.unspell(w.spelling('einen'))=='einen'
 out={'status':'PASS','scope':'All published full texts decode and reencode from their visible groups only; independent counts/alphabet; dictionary train source; fixed files','scientific_result':'ALL_COMPLETE_WRITERS_FAIL_FULL_SCREEN','complete_roundtrips':sum(len(rs) for rs in source.values())*3}
 (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
