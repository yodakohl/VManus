import csv,hashlib,json,re,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];BASE=Path(__file__).resolve().parents[1];ART=BASE/'artifacts'
def main():
 s=json.loads((BASE/'src/SPEC.json').read_text())
 for p,h in s['inputs'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
 assert hashlib.sha256((ART/'METADATA.tsv').read_bytes()).hexdigest()==json.loads((ART/'METADATA_RECEIPT.json').read_text())['sha256']
 db=sqlite3.connect(':memory:');db.execute('create table m(e,l,k,i integer,p)');db.execute('create table w(e,l,i integer,v,a,b,primary key(e,l,i))')
 for r in csv.DictReader((ART/'METADATA.tsv').open(),delimiter='\t'):db.execute('insert into m values(?,?,?,?,?)',(r['edition'],r['locus'],r['kind'],int(r['source_group_index']),r['paragraph_start']))
 for r in csv.DictReader((ROOT/'experiments/yolo/gdt1170_repetition_context_neutral_copy/artifacts/GUARDED.tsv').open(),delimiter='\t'):
  if r['kind']=='P':db.execute('insert into w values(?,?,?,?,?,?)',(r['edition'],r['locus'],int(r['source_group_index']),r['ivtff_group_raw'],r['left_separator'],r['right_separator']))
 doubles=db.execute("select a.e,a.v,a.l,a.i from w a join w b on b.e=a.e and b.l=a.l and b.i=a.i+1 and b.v=a.v join w p on p.e=a.e and p.l=a.l and p.i=a.i-1 join w n on n.e=a.e and n.l=a.l and n.i=a.i+2 where a.a='DEFINITE_SPACE' and a.b='DEFINITE_SPACE' and b.a='DEFINITE_SPACE' and b.b='DEFINITE_SPACE' and p.b='DEFINITE_SPACE' and n.a='DEFINITE_SPACE' order by a.e,a.l,a.i").fetchall()
 starts=db.execute("select w.e,w.v,w.l,w.i from w join m z on z.l=w.l and z.e='ZL3b' and z.i=1 and z.k='P' and z.p='1' join m t on t.l=w.l and t.e='IT2a' and t.i=1 and t.k='P' and t.p='1' where w.i=1 and w.a='LINE_START' and w.b in ('DEFINITE_SPACE','LINE_END') order by w.e,w.l,w.i").fetchall()
 expected={e:{'doublets':{},'starts':{}} for e in s['readers']}
 for k,rows in [('doublets',doubles),('starts',starts)]:
  for e,w,l,i in rows:
   if re.fullmatch('[a-z]+',w):expected[e][k].setdefault(w,[]).append({'locus':l,'index':i})
 assert expected==json.loads((ART/'EVENTS.json').read_text())
 result=json.loads((ART/'RESULT.json').read_text())
 for e,v in expected.items():
  d,p=v['doublets'],v['starts'];c=sorted(d.keys()&p.keys());o=result['readers'][e]
  assert o=={'doublet_types':len(d),'doublet_events':sum(map(len,d.values())),'start_types':len(p),'start_events':sum(map(len,p.values())),'conflicting_types':c,'status':'CONTRADICTED' if c else ('NO_COUNTERCASE' if d and p else 'NO_CAPACITY')}
 witnesses=json.loads((ART/'WITNESSES.json').read_text());assert len(witnesses)==sum(len(v['conflicting_types']) for v in result['readers'].values())
 for w in witnesses:
  e,f=w['edition'],w['form'];assert w['doublet']==expected[e]['doublets'][f][0] and w['start']==expected[e]['starts'][f][0]
  for name,event in [('doublet_line','doublet'),('start_line','start')]:
   actual=db.execute('select i,v,a,b from w where e=? and l=? order by i',(e,w[event]['locus'])).fetchall()
   assert actual==[(int(r['source_group_index']),r['ivtff_group_raw'],r['left_separator'],r['right_separator']) for r in w[name]]
 out={'status':'PASS','method':'Independent SQLite joins; same author/source; no image or semantic validation','witnesses':len(witnesses)}
 (ART/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
