"""Independent source/exhaustiveness audit plus deterministic replay, not meaning proof."""
from pathlib import Path
from collections import Counter,defaultdict
import csv,hashlib,json,importlib.util
EXP=Path(__file__).resolve().parents[1];ROOT=EXP.parents[2]

def read_tsv(name):return list(csv.DictReader((EXP/'artifacts'/name).open(),delimiter='\t'))
def main():
    checks=[]
    for name in ('PREREG_LOCK.json','MODEL_LOCK.json'):
        for p,h in json.loads((EXP/name).read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    checks.append('Discovery and model-stage locks, original source and base lexicons preserved')
    model=json.loads((EXP/'src/MODEL.json').read_text())
    source=json.loads((ROOT/model['source']).read_text())['groups']
    assert len(source)==1408 and len({r['source_group_id'] for r in source})==1408
    assert set(r['page'] for r in source)=={'f77r','f17r','f21r','f32v','f29v'}
    assert all(not r['page'].startswith('f84') and r['page']!='f116v' for r in source)
    byid={r['source_group_id']:r for r in source};lines=defaultdict(list)
    for r in source:lines[r['edition'],r['locus']].append(r)
    for rr in lines.values():rr.sort(key=lambda r:int(r['source_group_index']))
    targets=set(model['targets']);comp={'sheedy','sheey','lcheey','lsheey','chedy','qoteedy','qokain','lchedy'}
    concord=json.loads((EXP/'artifacts/CONCORDANCE.json').read_text())['occurrences']
    wanted={r['source_group_id'] for r in source if r['ivtff_group_raw'] in targets|comp}
    assert len(concord)==len(wanted) and {r['source_group_id'] for r in concord}==wanted
    for r in concord:
        orig=byid[r['source_group_id']]
        assert all(r[k]==v for k,v in orig.items())
        rr=lines[r['edition'],r['locus']];i=rr.index(orig)
        assert r['line_groups']==rr
        assert r['left_raw']==(rr[i-1]['ivtff_group_raw'] if i else '')
        assert r['right_raw']==(rr[i+1]['ivtff_group_raw'] if i+1<len(rr) else '')
        assert r['target']==(r['ivtff_group_raw'] in targets)
    checks.append('Every target and predetermined comparison form; complete original lines and neighbours')
    base=json.loads((ROOT/model['base_model']).read_text())['models']['M']['lexicon']
    inherited={k:dict(base) for k in model['models']}
    for prior_path in model['prior_extensions']:
        prior=json.loads((ROOT/prior_path).read_text())['models']
        for k in model['models']:inherited[k].update(prior[k]['lexicon'])
    assert set(model['models'])=={'R','T'}
    for k,m in model['models'].items():assert set(m['lexicon'])==set(model['new_forms']) and not set(m['lexicon'])&set(inherited[k])
    align=read_tsv('ALIGNMENT.tsv');cases=read_tsv('CANDIDATE_OCCURRENCES.tsv')
    assert len(align)==2816 and len({(r['model'],r['source_group_id']) for r in align})==2816
    for r in align:
        orig=byid[r['source_group_id']];lex={**inherited[r['model']],**model['models'][r['model']]['lexicon']}
        assert all(r[k]==str(v) for k,v in orig.items())
        assert [r['gloss'],r['role']]==lex.get(orig['ivtff_group_raw'],['⟦'+orig['ivtff_group_raw']+'⟧','UNREAD'])
    tid={r['source_group_id'] for r in source if r['ivtff_group_raw'] in targets}
    assert len(tid)==45 and len(cases)==90
    assert {(r['model'],r['source_group_id']) for r in cases}=={(m,t) for m in model['models'] for t in tid}
    for r in cases:
        orig=byid[r['source_group_id']];lex={**inherited[r['model']],**model['models'][r['model']]['lexicon']}
        assert [r['gloss'],r['role']]==lex[orig['ivtff_group_raw']]
        assert r['raw']==orig['ivtff_group_raw']
        for k in ('edition','locus','left_separator','right_separator'):assert r[k]==orig[k]
    checks.append('All2816 group renderings and all90 target/candidate consequences; no lexical changes or silent normalization')
    rendered_lines=0
    sep={'DEFINITE_SPACE':' ','UNCERTAIN_SMALL_SPACE':' / ','DRAWING_INTERRUPTION':' // '}
    for (e,locus),rr in lines.items():
        doc=(EXP/'artifacts'/f'READING_{e}.md').read_text()
        raw=rr[0]['ivtff_group_raw']+''.join(sep[r['left_separator']]+r['ivtff_group_raw'] for r in rr[1:])
        assert f'### {locus}\n\n`{raw}`\n' in doc,(e,locus)
        rendered_lines+=1
    assert rendered_lines==201
    # Specific edition differences must remain differences, including uncertain joins.
    assert next(r for r in source if r['source_group_id']=='ZL3b|f77r.25|G007')['left_separator']=='UNCERTAIN_SMALL_SPACE'
    assert Counter(r['edition'] for r in source if r['locus']=='f77r.23' and r['ivtff_group_raw']=='qokal')=={'RF1b':1}
    assert Counter(r['edition'] for r in source if r['locus']=='f77r.34' and r['ivtff_group_raw']=='chedy')=={'ZL3b':1,'IT2a':2,'RF1b':1}
    checks.append('All201 reader-loci and exact source separators; RF qokal and IT split remain distinct')
    result=json.loads((EXP/'artifacts/RESULT.json').read_text())
    for e,expected in [('ZL3b',[1,4,5,5]),('IT2a',[1,4,5,5]),('RF1b',[1,4,5,5])]:
        ct=Counter(r['ivtff_group_raw'] for r in source if r['edition']==e)
        assert [ct[t] for t in model['targets']]==expected
        assert result['counts'][e]['target_counts']=={t:ct[t] for t in model['targets']}
        rr=[r for r in source if r['edition']==e]
        assert result['counts'][e]['source_groups']==len(rr)
        assert result['counts'][e]['baseline_known']==sum(r['ivtff_group_raw'] in inherited['R'] for r in rr)
        assert result['counts'][e]['with_extension_known']==sum(r['ivtff_group_raw'] in set(inherited['R'])|set(model['new_forms']) for r in rr)
    assert result['target_pages']==['f29v','f77r'] and result['selected_translation'] is None
    assert result['confirmed_words']==result['independent_meaning_tests']==result['unexposed_confirmation_folios']==0
    assert result['new_form_occurrences']==45
    assert result['line37_known_groups']=={'ZL3b':{'total':7,'known':7},'IT2a':{'total':7,'known':7},'RF1b':{'total':7,'known':5}}
    local=read_tsv('LOCAL_CONTENT_BINDINGS.tsv')
    assert len(local)==6 and {(r['model'],r['edition']) for r in local}=={(m,e) for m in ['R','T'] for e in ['ZL3b','IT2a','RF1b']}
    field_specs={'topic_id':'teeolain','condition_marker_id':'chey','warm_id':'qoteedy','copula_id':'qokain','consequent_id':'cheedy','anaphor_id':'cheey','adjunct_id':'lchedy'}
    for r in local:
        for f,word in field_specs.items():
            matches=[o['source_group_id'] for o in lines[r['edition'],'f77r.37'] if o['ivtff_group_raw']==word]
            assert len(matches)<=1 and r[f]==(matches[0] if matches else '')
        assert r['status']==('RAW_READING_UNRESOLVED' if r['edition']=='RF1b' else 'LEXICALLY_COMPLETE_HYPOTHESIS')
        assert r['anaphor_referent_id']==r['topic_id']
        assert r['consequent_role']==('MOTION' if r['model']=='R' else 'REST_STATE')
        claim=('IF_WARM_THEN_MOTION_TOWARD_UNBOUND_GOAL' if r['model']=='R' else 'IF_WARM_THEN_REST_AT_UNBOUND_LATER_TIME') if r['edition']!='RF1b' else 'CONDITION_PROPERTY_AND_ADJUNCT_UNRESOLVED'
        assert r['conditional_claim']==claim
        assert all(r[f]=='False' for f in ['factual_warmth_inferred','factual_consequent_inferred','semantics_confirmed'])
    checks.append('Six explicit37 condition/anaphor/consequent rows, RF raw gaps, no factual warmth or consequent asserted')
    spec=importlib.util.spec_from_file_location('gdt936_run',EXP/'src/run.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    for name,value in mod.build().items():assert (EXP/'artifacts'/name).read_text()==value,name
    checks.append('Aggregates independently recomputed; full deterministic replay; no meaning selection or confirmation')
    out={'status':'PASS','experiment':'GDT936','checks':checks,'source_groups':1408,'reader_loci':201,'target_occurrences':45,'candidate_occurrences':90,'semantics_validated':False,'independent_reviewer':False,'author':'root'}
    (EXP/'artifacts/VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
