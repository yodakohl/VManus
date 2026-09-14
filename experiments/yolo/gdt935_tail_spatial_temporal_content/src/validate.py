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
    targets=set(model['targets']);comp={'cthy','shcthy','chcthey','shcthey','olchedy','qolchedy','solkeey'}
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
    prior=json.loads((ROOT/model['prior_extensions']).read_text())['models']
    inherited={k:{**base,**prior[k]['lexicon']} for k in model['models']}
    assert set(model['models'])=={'R','T'}
    for k,m in model['models'].items():assert set(m['lexicon'])==set(model['new_forms']) and not set(m['lexicon'])&set(inherited[k])
    align=read_tsv('ALIGNMENT.tsv');cases=read_tsv('CANDIDATE_OCCURRENCES.tsv')
    assert len(align)==2816 and len({(r['model'],r['source_group_id']) for r in align})==2816
    for r in align:
        orig=byid[r['source_group_id']];lex={**inherited[r['model']],**model['models'][r['model']]['lexicon']}
        assert all(r[k]==str(v) for k,v in orig.items())
        assert [r['gloss'],r['role']]==lex.get(orig['ivtff_group_raw'],['⟦'+orig['ivtff_group_raw']+'⟧','UNREAD'])
    tid={r['source_group_id'] for r in source if r['ivtff_group_raw'] in targets}
    assert len(tid)==60 and len(cases)==120
    assert {(r['model'],r['source_group_id']) for r in cases}=={(m,t) for m in model['models'] for t in tid}
    for r in cases:
        orig=byid[r['source_group_id']];lex={**inherited[r['model']],**model['models'][r['model']]['lexicon']}
        assert [r['gloss'],r['role']]==lex[orig['ivtff_group_raw']]
        assert r['raw']==orig['ivtff_group_raw']
        for k in ('edition','locus','left_separator','right_separator'):assert r[k]==orig[k]
    checks.append('All2816 group renderings and all120 target/candidate consequences; no lexical changes or silent normalization')
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
    for e,expected in [('ZL3b',[2,5,1,12,1,1]),('IT2a',[2,5,1,13,1,1]),('RF1b',[2,2,1,8,0,2])]:
        ct=Counter(r['ivtff_group_raw'] for r in source if r['edition']==e)
        assert [ct[t] for t in model['targets']]==expected
        assert result['counts'][e]['target_counts']=={t:ct[t] for t in model['targets']}
        rr=[r for r in source if r['edition']==e]
        assert result['counts'][e]['source_groups']==len(rr)
        assert result['counts'][e]['baseline_known']==sum(r['ivtff_group_raw'] in inherited['R'] for r in rr)
        assert result['counts'][e]['with_extension_known']==sum(r['ivtff_group_raw'] in set(inherited['R'])|set(model['new_forms']) for r in rr)
    assert result['target_pages']==['f21r','f77r'] and result['selected_translation'] is None
    assert result['confirmed_words']==result['independent_meaning_tests']==result['unexposed_confirmation_folios']==0
    assert result['new_form_occurrences']==21
    assert result['line26_known_groups']=={'ZL3b':{'total':6,'known':6},'IT2a':{'total':6,'known':6},'RF1b':{'total':6,'known':4}}
    local=read_tsv('LOCAL_CONTENT_BINDINGS.tsv')
    assert len(local)==6 and {(r['model'],r['edition']) for r in local}=={(m,e) for m in ['R','T'] for e in ['ZL3b','IT2a','RF1b']}
    field_specs={'subject_id':('f77r.25','shedy'),'accumulation_id':('f77r.25','shedar'),'prior_predicate_id':('f77r.25','daror'),'warm_id':('f77r.26','qoteedy'),'flow_id':('f77r.26','qokeedy'),'source_id':('f77r.26','qokaiin'),'rate_id':('f77r.26','chcthy'),'relation_id':('f77r.26','lchedy'),'goal_id':('f77r.26','qokaly')}
    for r in local:
        for f,(loc,word) in field_specs.items():
            matches=[o['source_group_id'] for o in lines[r['edition'],loc] if o['ivtff_group_raw']==word]
            assert len(matches)<=1 and r[f]==(matches[0] if matches else '')
        assert r['status']==('RAW_READING_UNRESOLVED' if r['edition']=='RF1b' else 'LEXICALLY_COMPLETE_HYPOTHESIS')
        assert r['earlier_than_flow_id']==(r['prior_predicate_id'] if r['model']=='T' and r['edition']!='RF1b' else '')
        assert r['physical_basin_identity']=='UNRESOLVED' and r['semantics_confirmed']=='False'
        assert r['relation_claim']==('APPOSITIONAL_GOAL' if r['model']=='R' else 'FLOW_LATER_THAN_PRIOR_DRAIN')
    checks.append('Six local role rows; R goal apposition/T later-event claim preserve raw availability, RF gaps and unresolved basin identity')
    spec=importlib.util.spec_from_file_location('gdt935_run',EXP/'src/run.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    for name,value in mod.build().items():assert (EXP/'artifacts'/name).read_text()==value,name
    checks.append('Aggregates independently recomputed; full deterministic replay; no meaning selection or confirmation')
    out={'status':'PASS','experiment':'GDT935','checks':checks,'source_groups':1408,'reader_loci':201,'target_occurrences':60,'candidate_occurrences':120,'semantics_validated':False,'independent_reviewer':False,'author':'root'}
    (EXP/'artifacts/VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
