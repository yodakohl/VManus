"""Source-free exhaustive check of the necessary even-AAA overlap ladder."""
import itertools,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
streams=0;witnesses=0;phases=set();lengths=set();odd_tail_hits=0
for inv in itertools.permutations(range(4)):
    for n in range(15):
        for out in itertools.product(range(2),repeat=n):
            source=[]
            for i in range(0,n-1,2):source.extend(divmod(inv[2*out[i]+out[i+1]],2))
            if n%2:source.append(out[-1])
            streams+=1
            for L in [2,4]:
                for start in range(n-3*L+1):
                    a=out[start:start+L]
                    if out[start+L:start+2*L]!=a or out[start+2*L:start+3*L]!=a:continue
                    w1=source[start:start+L];w2=source[start+L:start+2*L];w3=source[start+2*L:start+3*L]
                    assert w1[1:]==w2[1:] and w2[:-1]==w3[:-1]
                    if start%2==0:assert w1==w2==w3
                    phases.add(start%2);lengths.add(L);witnesses+=1
                    odd_tail_hits+=int(n%2==1 and start+3*L==n)
assert phases=={0,1} and lengths=={2,4} and odd_tail_hits>0
# Inverse pair swap at offset1: source00,10,11 can underlie output01,01,01.
out=[0,0,1,0,1,0,1,1];source=[]
for x,y in zip(out[::2],out[1::2]):source.extend([y,x])
ww=[source[1:3],source[3:5],source[5:7]]
assert ww==[[0,0],[1,0],[1,1]]
r={'status':'PASS','pair_bijections':24,'all_binary_streams_max_length':14,'stream_bijection_cases':streams,
 'even_AAA_windows_checked':witnesses,'phases':sorted(phases),'even_lengths':sorted(lengths),'odd_terminal_AAA_windows':odd_tail_hits,
 'nonidentical_source_example':{'output_with_flanks':out,'source_with_flanks':source,'three_source_words':ww},
 'scope':'Finite source-free validation supports algebraic proof; not native data or universal proof by enumeration.'}
(P/'artifacts/THEORY_VALIDATION.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
