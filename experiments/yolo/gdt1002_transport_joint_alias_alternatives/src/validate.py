"""Independent complete source census, cvc5 flow checks, and old bit replay."""
import argparse,collections,csv,hashlib,importlib.util,itertools,json,subprocess,sys
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def load(p,name):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cvc5-python',default=sys.executable);args=ap.parse_args()
    for p,h in read(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    cfg=read(E/'src/SPEC.json');g=read(R/cfg['grammar']);lex={x['raw']:x['symbol'] for x in read(R/cfg['source_draft'])['lexicon']};panel=read(A/'PANEL.json');pred=read(A/'PREDICTIONS.json');rows=read(A/'ROWS.json');result=read(A/'RESULT.json')
    selected=read(R/cfg['selection'])['additional_coherent_witnesses'];assert [p['id'] for p in panel]==selected and len(panel)==5
    targets={ed+'|'+p['id']:p for ed,ps in read(R/cfg['source_paragraphs']).items() for p in ps}
    for p in panel:
        src=targets[p['id']];assert p['words']==[w for l in src['lines'] for w in l['words']] and p['source_ids']==[x for l in src['lines'] for x in l['source_ids']]
        assert p['groups']==len(p['words']) and p['strict_anchor_eligible']==all(l['anchor_eligible'] for l in src['lines']) and p['leaf']==src['leaf']
        assert p['old_positions']==[dict(position=i+1,raw=w,value=lex[w]) for i,w in enumerate(p['words']) if w in lex]
        assert not p['page'].startswith('f84') and p['page']!='f116v'
    expected=[*itertools.combinations(range(5),2),tuple(range(5))];assert len(rows)==len(pred)==len(expected)==11
    checks=load(R/'experiments/yolo/gdt994_frozen_transport_whole_transfer/src/validate.py','fixed994');bit=load(R/'experiments/yolo/gdt993_complete_transport_consequence_audit/src/validate.py','fixed993bit');variants={c['id']:c['variant'] for c in read(R/cfg['old_cases']) if c['id'] in cfg['retained_variants']}
    finite=[];semantic=0;ground=0
    for row,pr,inds in zip(rows,pred,expected):
        assert row['indices']==pr['indices']==list(inds)
        for k in pr:assert row[k]==pr[k]
        ps=[panel[i] for i in inds];freq=collections.Counter(w for p in ps for w in set(p['words'])-lex.keys());assert pr['shared_unknown_words']==sorted(w for w,n in freq.items() if n>1)
        assert pr['members']==[p['id'] for p in ps] and pr['strict_all']==all(p['strict_anchor_eligible'] for p in ps)
        job=dict(paragraphs=ps,lexicon=lex,grammar=g,timeout=cfg['query_milliseconds'])
        def ask(j):
            out=subprocess.run([args.cvc5_python,str(E/'src/independent.py')],input=json.dumps(j),capture_output=True,text=True,timeout=35,check=True);return json.loads(out.stdout)
        other=ask(job);rec=dict(id=row['id'],primary=row['status'],independent=other)
        if row['status']=='UNSAT':assert other['status']=='unsat'
        elif row['status']=='SAT':assert other['status']!='unsat'
        if row['status']=='SAT' and row['exhaustive']:
            assert len(row['witnesses'])==1;rec['alternative_check']=ask(dict(**job,blocked=row['witnesses'][0]));assert rec['alternative_check']['status']=='unsat'
        finite.append(rec)
        for witness in row['witnesses']:
            aliases=witness['aliases'];assert set(aliases)==set(w for p in ps for w in p['words'])-lex.keys();full={**lex,**aliases}
            for p,parsed in zip(ps,witness['parses']):
                cursor=0;kinds=[]
                for c in parsed:
                    assert c['start']==cursor and c['end']==cursor+len(g['patterns'][c['kind']]);actual=[full[w] for w in p['words'][c['start']:c['end']]];assert c['symbols']==actual
                    for val,slot in zip(actual,g['patterns'][c['kind']]):assert val in (g['types'][slot[1:]] if slot.startswith('@') else [slot])
                    cursor=c['end'];kinds.append(c['kind'])
                assert cursor==len(p['words']) and kinds[0]=='INITIAL' and kinds[-1]=='CONCLUSION'
                assert all(kinds.count(k)==1 for k in ('INITIAL','GOAL','SAFETY','CAPACITY','CONCLUSION'));ground+=1
            assert [v['variant_id'] for v in witness['replays']]==list(variants)
            for replay in witness['replays']:
                v=variants[replay['variant_id']];assert replay['variant']==v
                for p,parsed,rec in zip(ps,witness['parses'],replay['paragraphs']):
                    semantic+=1;assert rec['id']==p['id'];error=checks.binding_error(parsed,v)
                    if error:assert rec['status']=='BINDING_CONTRADICTION' and rec['error']==error;continue
                    paths,hazards,refs=bit.replay(parsed,v);named={s for c in parsed for s in c['symbols'] if s in ('W','G','C')}
                    for path in paths:
                        for state in [path,*path['trace']]:state['positions']={k:x for k,x in state['positions'].items() if k in named|{'M','B'}}
                    assert paths==rec['paths'] and hazards==rec['program']['hazards'] and refs==rec['program']['references']
                    assert rec['status']==('COHERENT' if any(t['consistent'] for t in paths) else 'CONTRADICTED')
                assert replay['joint_coherent']==all(r['status']=='COHERENT' for r in replay['paragraphs'])
            assert witness['joint_coherent']==any(r['joint_coherent'] for r in witness['replays'])
        assert row['coherent_witnesses']==sum(w['joint_coherent'] for w in row['witnesses'])
    assert result['syntax_status_counts']==dict(collections.Counter(r['status'] for r in rows)) and result['systems_with_coherent_saved_witness']==[r['id'] for r in rows if r['coherent_witnesses']]
    with (A/'CANDIDATES.tsv').open() as f:table=list(csv.DictReader(f,delimiter='\t'))
    assert len(table)==11
    for t,r in zip(table,rows):assert t['id']==r['id'] and t['status']==r['status'] and int(t['witnesses'])==len(r['witnesses']) and int(t['coherent_witnesses'])==r['coherent_witnesses']
    out=dict(status='PASS',systems_checked=11,paragraph_witnesses_ground_checked=ground,semantic_replays_checked=semantic,finite_checks=finite,independent_unknowns=sum(x['independent']['status']=='unknown' for x in finite),scope='Independent flow encoding and bit execution; not historical word/source truth',confirmed_words=0)
    (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
