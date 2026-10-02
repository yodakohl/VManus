#!/usr/bin/env python3
"""Fixed paragraph candidate enumeration, never execution through unknown text."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
P = Path(__file__).resolve().parents[1]
ROOT = P.parents[2]
def read(p): return json.loads(p.read_text())
def write(name, data): (P/'artifacts'/name).write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n')
def main():
    source=read(P/'src/SOURCE.json')
    for x in source['inputs']:
        assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256'], x['path']
    for name, digest in read(P/'src/PREREG_LOCK.json')['hashes'].items():
        assert hashlib.sha256((P/name).read_bytes()).hexdigest()==digest
    selection=read(P/'artifacts/SELECTION.json'); loci=selection['loci']
    corepath=ROOT/'experiments/yolo/gdt1137_material_process_type_return/src/core.py'
    spec=importlib.util.spec_from_file_location('fixed1137',corepath); core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
    tree=ast.parse(corepath.with_name('author.py').read_text()); lexicon={}
    for n in tree.body:
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('CORE_WORDS','EXTENSION') for t in n.targets): lexicon.update(ast.literal_eval(n.value))
    assert len(lexicon)==23
    native={}; results={}
    for edition in ('ZL3b','IT2a','RF1b'):
        snap=read(ROOT/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_EVALUATION_{edition}.json')
        rows=sorted([r for r in snap['lines'] if r['metadata']['page']=='f76r' and r['metadata']['locus'] in loci],key=lambda r:int(r['metadata']['source_row_index']))
        assert [r['metadata']['locus'] for r in rows]==loci
        native[edition]={'group_columns':snap['group_columns'],'lines':rows}
        groups=[]; producers=[]; qcases=[]
        for row in rows:
            gs=[]
            for raw in row['groups']:
                g=dict(zip(snap['group_columns'],raw));g.update(locus=row['metadata']['locus'],kind=row['metadata']['kind'],position=len(groups),known=dict(zip(snap['group_columns'],raw))['ivtff_group_raw'] in lexicon)
                gs.append(g);groups.append(g)
            def joined(a,b):
                return int(b['source_group_index'])==int(a['source_group_index'])+1 and a['right_separator']==b['left_separator']=='DEFINITE_SPACE'
            for i,g in enumerate(gs):
                if g['ivtff_group_raw']!='qokedy': continue
                case={'q':g,'status':'RIGHT_OUTSIDE_LICENSES','span':[]}
                if i+1==len(gs):case['status']='LINE_END'
                else:
                    right=gs[i+1];rw=right['ivtff_group_raw'];case['right']=right
                    if rw in core.LICENSES:
                        if not joined(g,right):case['status']='UNCERTAIN_RIGHT_SEAM'
                        elif rw in ('chedy','shedy'):
                            case.update(status='UNARY_PRODUCT',span=[g,right],product=core.qokedy(core.lexical_nominal(rw),g['source_group_id']))
                        elif i==0:case['status']='MISSING_LEFT_DY'
                        else:
                            left=gs[i-1];case['left']=left
                            if left['ivtff_group_raw'] not in ('chedy','shedy'):case['status']='LEFT_OUTSIDE_DY'
                            elif not joined(left,g):case['status']='UNCERTAIN_LEFT_SEAM'
                            else:
                                product=core.qokedy(core.lexical_nominal(left['ivtff_group_raw']),g['source_group_id'])
                                case.update(status='BINARY_PRODUCT',span=[left,g,right],product=product,assertion=core.source_predicate(product,core.lexical_nominal(rw)))
                qcases.append(case)
                if 'product' in case:producers.append(case)
        def unknown(a,b):return [g for g in groups if a<g['position']<b and not g['known']]
        returns=[];che=core.lexical_nominal('chedy')
        for g in groups:
            if g['ivtff_group_raw']!='solchedy':continue
            prior=[p for p in producers if p['span'][-1]['position']<g['position']]
            later=[p for p in producers if p['span'][-1]['position']>=g['position']]
            matching=[p for p in prior if p['product']['material']==che['material'] and p['product']['operations']==che['operations']]
            eligible=[p for p in prior[:-1] if p in matching]
            status='EARLIER_TYPED_CANDIDATE' if eligible else ('LATEST_COMPATIBLE_ONLY_IN_KNOWN_PROJECTION' if matching else 'NO_MATCHING_KNOWN_PRODUCER')
            returns.append({'selector':g,'status':status,'earlier_producers':[p['q']['source_group_id'] for p in prior], 'matching_producers':[p['q']['source_group_id'] for p in matching],'earlier_typed_candidates':[p['q']['source_group_id'] for p in eligible],'later_excluded':[p['q']['source_group_id'] for p in later], 'unknown_before':unknown(-1,g['position']), 'witnesses':[{'producer':p['q']['source_group_id'],'span':p['span'],'unknown_between':unknown(p['span'][-1]['position'],g['position'])} for p in prior]})
        consumers=[]
        for g in groups:
            if g['ivtff_group_raw']=='qody':consumers.append({'consumer':g,'prior_return_candidates':[{'selector_id':r['selector']['source_group_id'],'status':r['status'],'unknown_between':unknown(r['selector']['position'],g['position'])} for r in returns if r['selector']['position']<g['position']]})
        from collections import Counter
        results[edition]={'groups':groups,'coverage':{'total':len(groups),'known':sum(g['known'] for g in groups),'unknown':sum(not g['known'] for g in groups),'known_form_counts':dict(Counter(g['ivtff_group_raw'] for g in groups if g['known']))},'qokedy_cases':qcases,'returns':returns,'consumers':consumers,'boundary_differences':[{'locus':r['metadata']['locus'],'ZL':[selection['metadata'][i][k] for k in ('paragraph_start','paragraph_end')],edition:[r['metadata'][k] for k in ('paragraph_start','paragraph_end')]} for i,r in enumerate(rows) if any(r['metadata'][k]!=selection['metadata'][i][k] for k in ('paragraph_start','paragraph_end'))]}
    write('NATIVE_SOURCE.json',native);write('CASES.json',results)
    summary={'experiment':'GDT1147','decision':'NEW_WRITTEN_REFERENCE_CANDIDATE' if any(r['status']=='EARLIER_TYPED_CANDIDATE' for v in results.values() for r in v['returns']) else 'FIXED_CONSTRUCTION_CONTEXT_INCOMPLETE','scope':loci,'confirmed_words':0,'independent_confirmation_capacity':0,'full_execution':False,'readers':{e:{'coverage':v['coverage'],'qokedy':len(v['qokedy_cases']),'products':sum('product' in q for q in v['qokedy_cases']),'returns':[{'locus':r['selector']['locus'],'id':r['selector']['source_group_id'],'status':r['status'],'earlier_typed_candidates':r['earlier_typed_candidates'],'unknown_before':len(r['unknown_before'])} for r in v['returns']],'consumers':len(v['consumers']),'boundary_differences':v['boundary_differences']} for e,v in results.items()}}
    write('RESULT.json',summary)
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
