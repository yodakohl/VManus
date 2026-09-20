import argparse,collections,csv,datetime,hashlib,importlib.util,itertools,json,time
from pathlib import Path
from solver import solve
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def write(n,x):(A/n).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def load(p,name):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def prepare(cfg):
    retained=read(R/cfg['selection'])['additional_coherent_witnesses'];assert len(retained)==5
    lex={x['raw']:x['symbol'] for x in read(R/cfg['source_draft'])['lexicon']};panel=[]
    for ed,ps in read(R/cfg['source_paragraphs']).items():
        for p in ps:
            ident=ed+'|'+p['id']
            if ident not in retained:continue
            assert not p['page'].startswith('f84') and p['page']!='f116v'
            words=[w for l in p['lines'] for w in l['words']]
            panel.append(dict(id=ident,edition=ed,page=p['page'],paragraph=p['id'],leaf=p['leaf'],groups=len(words),words=words,source_ids=[x for l in p['lines'] for x in l['source_ids']],strict_anchor_eligible=all(l['anchor_eligible'] for l in p['lines']),old_positions=[dict(position=i+1,raw=w,value=lex[w]) for i,w in enumerate(words) if w in lex]))
    panel.sort(key=lambda p:retained.index(p['id']));assert len(panel)==5
    systems=[]
    for inds in [*itertools.combinations(range(5),2),tuple(range(5))]:
        counts=collections.Counter(w for i in inds for w in set(panel[i]['words'])-lex.keys());shared=sorted(w for w,n in counts.items() if n>1)
        systems.append(dict(id='P'+'-'.join(str(i) for i in inds),indices=list(inds),members=[panel[i]['id'] for i in inds],shared_unknown_words=shared,lexical_overlap_capacity=len(shared),strict_all=all(panel[i]['strict_anchor_eligible'] for i in inds),prediction='ONE_GLOBAL_ALIAS_PER_NEW_SPELLING_ALL_COMPLETE_PARAGRAPHS_FIXED_GRAMMAR',independent_meaning_capacity=0))
    write('PANEL.json',panel);write('PREDICTIONS.json',systems)
    print(json.dumps(dict(prepared=len(systems),paragraphs=len(panel),shared_pairs=sum(bool(s['shared_unknown_words']) for s in systems if len(s['indices'])==2))))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prepare',action='store_true');args=ap.parse_args();cfg=read(E/'src/SPEC.json')
    if args.prepare:prepare(cfg);return
    for p,h in read(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    panel=read(A/'PANEL.json');systems=read(A/'PREDICTIONS.json');g=read(R/cfg['grammar']);lex={x['raw']:x['symbol'] for x in read(R/cfg['source_draft'])['lexicon']};old=read(R/cfg['old_cases']);variants=[x for x in old if x['id'] in cfg['retained_variants']];model=load(R/cfg['model'],'fixed993')
    rows=[];started=datetime.datetime.now(datetime.timezone.utc).isoformat();tm=time.monotonic()
    for pred in systems:
        ps=[panel[i] for i in pred['indices']];row=dict(**pred,**solve(ps,lex,g,cfg['query_milliseconds']))
        for witness in row['witnesses']:
            replays=[]
            for v in variants:
                results=[]
                for p,parsed in zip(ps,witness['parses']):
                    rec=dict(id=p['id'])
                    try:
                        program=model.compile_reading(parsed,v['variant']);paths=model.execute(program,v['variant']);rec.update(program=program,paths=paths,status='COHERENT' if any(t['consistent'] for t in paths) else 'CONTRADICTED')
                    except ValueError as ex:rec.update(status='BINDING_CONTRADICTION',error=str(ex),paths=[])
                    results.append(rec)
                replays.append(dict(variant_id=v['id'],variant=v['variant'],paragraphs=results,joint_coherent=all(r['status']=='COHERENT' for r in results)))
            witness['replays']=replays;witness['joint_coherent']=any(r['joint_coherent'] for r in replays)
        row['coherent_witnesses']=sum(w['joint_coherent'] for w in row['witnesses']);rows.append(row)
        print(json.dumps({k:row[k] for k in ('id','status','queries','coherent_witnesses','code_ambiguity')}),flush=True)
    write('ROWS.json',rows)
    result=dict(status='JOINT_ALTERNATIVES_AUDITED',systems=len(rows),syntax_status_counts=dict(collections.Counter(r['status'] for r in rows)),systems_with_coherent_saved_witness=[r['id'] for r in rows if r['coherent_witnesses']],shared_pair_systems=[r['id'] for r in rows if len(r['indices'])==2 and r['shared_unknown_words']],all_five_status=rows[-1]['status'],semantic_exhaustion_claim=False,confirmed_words=0,independent_meaning_capacity=0,significance=False,reserve_accesses=0)
    write('RESULT.json',result);write('EXECUTION_RECEIPT.json',dict(started_utc=started,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),wall_seconds=time.monotonic()-tm))
    with (A/'CANDIDATES.tsv').open('w',newline='') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['id','members','shared_unknown_words','strict_all','status','witnesses','coherent_witnesses','ambiguity','independent_meaning_capacity'])
        for r in rows:w.writerow([r['id'],';'.join(r['members']),';'.join(r['shared_unknown_words']),r['strict_all'],r['status'],len(r['witnesses']),r['coherent_witnesses'],r['code_ambiguity'],0])
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
