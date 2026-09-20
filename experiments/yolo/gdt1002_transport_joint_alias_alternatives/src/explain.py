"""Post-run short certificates and retention of already-known disjoint positives."""
import itertools,json,importlib.util
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def load(p,name):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
cfg=read(E/'src/SPEC.json');g=read(R/cfg['grammar']);panel=read(A/'PANEL.json');rows=read(A/'ROWS.json');lex={x['raw']:x['symbol'] for x in read(R/cfg['source_draft'])['lexicon']}
assert panel[0]['words'][29]=='oty' and panel[1]['words'][36]=='oty'
assert g['patterns']['CONCLUSION'][-2]=='ATTENDED_BY'
assert [(k,i) for k,p in g['patterns'].items() for i,t in enumerate(p) if t=='ATTENDED_BY']==[('CONCLUSION',4)]
assert len(panel[1]['words'])-2!=36
assert panel[1]['words'][-1]=='chor' and panel[2]['words'][-4]=='chor'
assert g['patterns']['CONCLUSION'][-1]=='@Agent' and g['types']['Agent']==['M'] and g['patterns']['CONCLUSION'][-4]=='UNHARMED'
proofs=[dict(system='P0-1',word='oty',first=dict(member=panel[0]['id'],position=30,forced_value='ATTENDED_BY'),second=dict(member=panel[1]['id'],position=37,required_only_position=47),contradiction='ATTENDED_BY appears only in the mandatory final conclusion, at position47 in the second paragraph.'),dict(system='P1-2',word='chor',first=dict(member=panel[1]['id'],position=48,forced_value='M'),second=dict(member=panel[2]['id'],position=33,forced_value='UNHARMED'),contradiction='The same whole word is forced to two distinct fixed terminal values by the two mandatory conclusions.')]
old={r['id']:r for r in read(R/'experiments/yolo/gdt997_transport_finite_completion_capacity/artifacts/ROWS.json')};bit=load(R/'experiments/yolo/gdt993_complete_transport_consequence_audit/src/validate.py','fixedbit');check=load(R/'experiments/yolo/gdt994_frozen_transport_whole_transfer/src/validate.py','fixedcheck')
retained=[]
for row in rows:
    if len(row['indices'])!=2 or row['shared_unknown_words']:continue
    members=[old[p] for p in row['members']];merged={}
    for member in members:
        for w,v in member['shared']['aliases'].items():assert w not in merged or merged[w]==v;merged[w]=v
    events=[]
    for vi in range(4):
        v=members[0]['cases'][vi]['variant'];both=[]
        for p,member in zip([panel[i] for i in row['indices']],members):
            parsed=member['shared']['parse'];assert all([({**lex,**merged})[w] for w in p['words'][c['start']:c['end']]]==c['symbols'] for c in parsed)
            assert check.binding_error(parsed,v) is None
            paths,hazards,refs=bit.replay(parsed,v);assert any(x['consistent'] for x in paths)
            both.append(dict(member=member['id'],coherent=True,source='unchanged GDT997 first witness'))
        events.append(dict(variant=v,members=both))
    retained.append(dict(system=row['id'],aliases=merged,parses=[m['shared']['parse'] for m in members],replays=events,lexical_overlap_capacity=0))
assert len(retained)==6
result=dict(status='PASS',scope='Post-run explanations and preservation of inherited disjoint witnesses; not a new fit or independent confirmation',short_unsat_certificates=proofs,all_five_inherits= [p['system'] for p in proofs],inherited_disjoint_compatible_systems=retained)
(A/'EXPLANATIONS.json').write_text(json.dumps(result,separators=(',',':'))+'\n')
lines=['# All sampled joint readings','','All values are frozen hypothetical terminal meanings. Whole-paragraph semantic failures are retained.']
for r in rows:
    lines+=['',f"## {r['id']} — {r['status']}",'',f"Shared unknown spellings: {', '.join(r['shared_unknown_words']) or 'none; lexical transfer capacity zero'}."]
    for wi,w in enumerate(r['witnesses']):
        lines+=['',f"### Witness{wi+1}",'',f"Joint coherent: {w['joint_coherent']}; ambiguity: {r['code_ambiguity']}."]
        for pi,parsed in zip(r['indices'],w['parses']):
            p=panel[pi];lines+=['',p['id'],'','| Complete written clause | Fixed hypothetical terminal values |','|---|---|']
            lines += [f"| {' '.join(p['words'][c['start']:c['end']])} | {c['kind']}: {' '.join(c['symbols'])} |" for c in parsed]
        lines+=['','All four variants and every failed state/assertion are in ROWS.json.']
lines+=['','## Six inherited disjoint positives','','All six pairs with no shared new spellings retain the compatible GDT997 first witnesses. Their complete merged maps/parses are in EXPLANATIONS.json. The new solver samples above do not invalidate these older positives; no common new word value is tested by the disjoint combinations.']
(A/'READINGS.md').write_text('\n'.join(lines)+'\n');print(json.dumps(dict(status='PASS',short_certificates=2,inherited_disjoint_positive_systems=6)))
