import csv,json
from pathlib import Path
E=Path(__file__).resolve().parents[1]
def read(n):return json.loads((E/'artifacts'/n).read_text())
c=read('CANDIDATES.json');results={ed:{tuple(r['stems']):r for r in read(f'EVALUATION_{ed}.json')['candidates']} for ed in ['ZL3b','IT2a','RF1b']};rows=[]
for a,b in c:
 row=[a,b,a+'r '+b+'r',a+'l '+b+'l']
 for ed in results:
  r=results[ed][(a,b)];row += [r['cells'][x] for x in ['rr','rl','lr','ll']]+[','.join('f'+str(f) for f in r['leaves'])]
 rows.append(row)
with (E/'artifacts/CANDIDATE_RESULTS.tsv').open('w') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['stem1','stem2','RR','LL']+[ed+'_'+x for ed in results for x in ['RR','RL','LR','LL','leaves']]);w.writerows(rows)
text=['| RR / LL | ZL RR,RL,LR,LL | IT RR,RL,LR,LL | RF RR,RL,LR,LL | ZL leaves |','|---|---|---|---|---|']
for row in rows:text.append('| `'+row[2]+'` / `'+row[3]+'` | '+', '.join(map(str,row[4:8]))+' | '+', '.join(map(str,row[9:13]))+' | '+', '.join(map(str,row[14:18]))+' | '+(row[8] or 'none')+' |')
(E/'artifacts/CANDIDATE_TABLE.md').write_text('\n'.join(text)+'\n')
