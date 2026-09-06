import argparse,collections,importlib.util,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def save(name,x,check=False):
 path=E/'artifacts'/name
 if check:assert path.read_text()==enc(x),name
 else:path.write_text(enc(x))
def pack(rows,s):
 by=collections.defaultdict(list)
 for r in rows:by[r['edition'],r['locus']].append(r)
 output={ed:[] for ed in s['editions']};gc=s['group_columns']
 for (ed,locus),rr in sorted(by.items()):
  rr.sort(key=lambda x:int(x['source_group_index']));meta={k:v for k,v in rr[0].items() if k not in gc}
  assert all({k:v for k,v in r.items() if k not in gc}==meta for r in rr)
  output[ed].append(dict(metadata=meta,groups=[[r[k] for k in gc] for r in rr]))
 return output
def analyze(lines,ed):
 windows=[];hits=[];den={p:collections.Counter(candidate=0,eligible=0,nonprimitive_tandem=0,primitive_tandem=0) for p in [1,2,3]}
 for li,line in enumerate(lines):
  gs=line['groups'];words=[r[2] for r in gs]
  for p in [1,2,3]:
   for start in range(len(gs)-2*p+1):
    seg=gs[start:start+2*p];eligible=all(int(b[1])==int(a[1])+1 and a[4]==b[3]=='DEFINITE_SPACE' for a,b in zip(seg,seg[1:]));ww=words[start:start+2*p]
    tandem=eligible and ww[:p]==ww[p:];primitive=tandem and not any(all(ww[i]==ww[i-q] for i in range(q,len(ww))) for q in range(1,p))
    windows.append([li,start,p,int(eligible),int(tandem),int(primitive)])
    den[p]['candidate']+=1;den[p]['eligible']+=eligible;den[p]['nonprimitive_tandem']+=tandem and not primitive;den[p]['primitive_tandem']+=primitive
    if primitive:
     m=line['metadata'];hits.append(dict(edition=ed,locus=m['locus'],page=m['page'],folio=re.match(r'f[0-9]+',m['page']).group(),period=p,start_index=seg[0][1],source_ids=[x[0] for x in seg],groups=ww,line_array_index=li))
 return windows,hits,den
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args();s=json.loads((E/'src/SPEC.json').read_text())
 if a.check:source={ed:json.loads((E/'artifacts'/f'SOURCE_{ed}.json').read_text())['lines'] for ed in s['editions']}
 else:
  path=ROOT/'experiments/yolo/gdt829_repeated_passage_reflow_capacity/src/run.py';sp=importlib.util.spec_from_file_location('guard_reader',path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);rows,guard=m.query(s);source=pack(rows,s)
  save('GUARD.json',guard)
  for ed in s['editions']:save(f'SOURCE_{ed}.json',dict(group_columns=s['group_columns'],lines=source[ed]))
 allhits=[];summary={};higher=[]
 for ed in s['editions']:
  windows,hits,den=analyze(source[ed],ed);save(f'WINDOWS_{ed}.json',dict(columns=['line_array_index','zero_based_stored_group_start','period','eligible','tandem','primitive'],rows=windows),a.check);allhits+=hits
  summary[ed]={str(p):dict(den[p],folios=sorted({h['folio'] for h in hits if h['period']==p})) for p in [1,2,3]}
  for i in sorted({h['line_array_index'] for h in hits if h['period']>1}):higher.append(dict(edition=ed,line=source[ed][i]))
 save('HITS.json',allhits,a.check);save('HIGHER_PERIOD_LINES.json',dict(group_columns=s['group_columns'],lines=higher),a.check)
 result=dict(status='COMPLETE_PRIMITIVE_TANDEM_DISCOVERY_NO_MECHANISM_TEST',summary=summary,hit_rows=len(allhits),higher_period_source_lines=len(higher));save('RESULT.json',result,a.check);print(enc(result))
if __name__=='__main__':main()
