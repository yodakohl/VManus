import csv,hashlib,importlib.util,json
from datetime import datetime,timezone
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
P=E.parent/'gdt1028_galen_whole_preparation_and_desire'
def read(p):return json.loads(Path(p).read_text())
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def source():return read(E/'src/SOURCE.json')
def spec():return read(E/'src/SPEC.json')
def cases():return read(E/'src/CASES.json')
def table(p,rows):
    with Path(p).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def read_table(p):
    with Path(p).open() as f:return list(csv.DictReader(f,delimiter='\t'))
def check_lock():
    for p,h in read(E/'PREREG_LOCK.json')['files'].items():assert sha(R/p)==h,p
def load_parent(name):
    path=P/'src'/f'{name}.py';expected=read(P/'PREREG_LOCK.json')['files'][str(path.relative_to(R))]
    assert sha(path)==expected
    sp=importlib.util.spec_from_file_location('gdt1028_'+name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def parent_source():return read(P/'src/SOURCE.json')
def lexicon(s):
    d={e['form']:dict(e) for e in parent_source()['lexicon']};d.update({e['form']:dict(e) for e in s['new_lexicon']})
    change=s['explicit_new_branch_before_any_semantic_test']['changed_entry']
    d['qoky']['denotation']=change['new_denotation'];return d
def parent_main():return next(c for c in read(P/'src/SPEC.json')['candidates'] if c['id']=='INTRINSIC_GENERAL_BRIDGED_QUOTED_FOOD_TRANSFER')
