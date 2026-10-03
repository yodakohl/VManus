#!/usr/bin/env python3
"""Independent GDT1159 source extraction and exhaustive assignment audit."""
import collections,csv,gzip,hashlib,itertools,json,math,unicodedata
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
COLLECTIONS=['b4','b6','br1','bs1','gr1','w1']
ROLE_TAGS={'title','opener','instruction','ingredient','tool','dish','name','closer','kitchenTip','householdTip','servingTip','time','dietetics','alternative','ref','unclear'}
MAPS=np.array(list(itertools.product(range(5),repeat=7)),dtype=np.int8)
MASKS=np.stack([np.sum((MAPS==c)*(1<<np.arange(7)),axis=1) for c in range(1,5)],axis=1)
PAIR=list(itertools.combinations(range(4),2))
def read(p):return json.loads(p.read_text())
def local(tag):return tag.rsplit('}',1)[-1]
def close(a,b):return np.allclose(a,b,rtol=1e-10,atol=1e-12)
def load_sources():
    for f,h in read(E/'artifacts/REGISTRATION_LOCK.json')['files'].items():assert hashlib.sha256((E/f).read_bytes()).hexdigest()==h
    with (ROOT/'gdt176_corema_collection_manifest.tsv').open() as f:manifest={r['collection_id']:r for r in csv.DictReader(f,delimiter='\t')}
    out={}
    for coll in COLLECTIONS:
        path=ROOT/'.gdt176/corema'/(coll+'.recipes.xml');blob=path.read_bytes();assert hashlib.sha256(blob).hexdigest()==manifest[coll]['sha256'] and len(blob)==int(manifest[coll]['size_bytes'])
        root=ET.fromstring(blob);recipes=[]
        for ri,recipe in enumerate((node for node in root.iter() if node.get('type')=='recipe'),1):
            rid=recipe.get('{http://www.w3.org/XML/1998/namespace}id',f'{coll}.ordinal{ri}');events=[];excluded=[]
            role_nodes=[node for node in recipe.iter() if local(node.tag) in ROLE_TAGS]
            for ordinal,node in enumerate(role_nodes,1):
                if local(node.tag)!='ingredient':continue
                commodity=node.get('commodity','').strip();ana=node.get('ana','').strip();text=unicodedata.normalize('NFC',''.join(node.itertext())).strip();reasons=[]
                if not commodity:reasons.append('NO_COMMODITY')
                if any(child is not node and child.get('commodity','').strip() for child in node.iter()):reasons.append('COMMODITY_DESCENDANT')
                if ana:reasons.append('NONEMPTY_ANA')
                if len(text.split())!=1:reasons.append('NOT_ONE_TOKEN')
                record={'source_id':f'{coll}|{rid}|{ordinal}','collection':coll,'recipe_id':rid,'recipe_ordinal':ri,'element_ordinal':ordinal,'form':text,'original_span':''.join(node.itertext()),'english_label':node.get('en',''),'q':commodity,'ana':ana,'reasons':reasons}
                (excluded if reasons else events).append(record)
            titles=[' '.join(unicodedata.normalize('NFC',node.get('en') or node.get('key') or ''.join(node.itertext())).split()).casefold() for node in recipe.iter() if local(node.tag)=='title']
            recipes.append({'recipe_id':rid,'recipe_ordinal':ri,'events':events,'excluded':excluded,'titles':titles})
        assert len(recipes)==int(manifest[coll]['recipe_count']);out[coll]=recipes
    return out

def construct_folds(source):
    folds=[]
    for held in COLLECTIONS:
        train=[r for c in COLLECTIONS if c!=held for r in source[c]];target=source[held]
        qcount=collections.Counter(q for r in train for q in {e['q'] for e in r['events']})
        fcount=collections.Counter(f for r in target for f in {e['form'] for e in r['events']})
        concepts=sorted(qcount,key=lambda q:(-qcount[q],q))[:4];forms=sorted(fcount,key=lambda f:(-fcount[f],f.encode('utf8')))[:7]
        assert len(concepts)==4 and len(forms)==7
        A=np.array([[int(q in {e['q'] for e in r['events']}) for q in concepts] for r in train],dtype=np.int8)
        B=np.array([[int(f in {e['form'] for e in r['events']}) for f in forms] for r in target],dtype=np.int8)
        gold=[collections.Counter(e['q'] for r in target for e in r['events'] if e['form']==f) for f in forms]
        fractions=np.array([[0.]+[g[q]/sum(g.values()) for q in concepts] for g in gold]);counts=np.array([[0]+[g[q] for q in concepts] for g in gold]);oov=np.array([sum(v for q,v in g.items() if q not in concepts) for g in gold])
        accuracy=np.mean(fractions[np.arange(7),MAPS],axis=1);weighted=np.sum(counts[np.arange(7),MAPS],axis=1)/sum(sum(g.values()) for g in gold)
        folds.append({'held':held,'concepts':concepts,'forms':forms,'A':A,'B':B,'gold':gold,'accuracy':accuracy,'weighted':weighted,'oov':oov,'fractions':fractions})
    return folds

def costs(A,B):
    rowbits=np.sum(B*(1<<np.arange(7)),axis=1);hist=np.bincount(rowbits,minlength=128)
    intersect=((np.arange(128)[:,None]&np.arange(128)[None,:])!=0)
    union=intersect@hist/len(B)
    p=A.mean(axis=0);p2=np.array([np.mean(A[:,i]*A[:,j]) for i,j in PAIR])
    target=union[MASKS]
    marginal=np.mean((target-p)**2,axis=1)
    pairerror=np.zeros(len(MAPS))
    for k,(i,j) in enumerate(PAIR):
        joint=union[MASKS[:,i]]+union[MASKS[:,j]]-union[MASKS[:,i]|MASKS[:,j]]
        pairerror+=(joint-p2[k])**2/6
    return marginal,marginal+pairerror

def summary(cost,fold):
    minimum=float(cost.min());maximum=float(cost.max());opt=np.flatnonzero(cost<=minimum+1e-12);envelope=np.flatnonzero(cost<=minimum+.01*(maximum-minimum)+1e-12)
    return {'min':minimum,'max':maximum,'optima':opt,'envelope':envelope,'macro':float(fold['accuracy'][opt].mean()),'weighted':float(fold['weighted'][opt].mean()),'alternatives':[sorted(set(MAPS[opt,j].tolist())) for j in range(7)],'envelope_alternatives':[sorted(set(MAPS[envelope,j].tolist())) for j in range(7)]}

def shuffle_world(B,foldindex,world):
    rng=np.random.default_rng(1159000+1000*foldindex+world);rows=[set(np.flatnonzero(row).tolist()) for row in B];changed=0
    for _ in range(100*len(rows)):
        a,b=rng.choice(len(rows),2,replace=False);common=rows[a]&rows[b];difference=sorted(rows[a]^rows[b]);na=len(rows[a]-common)
        if na==0 or na==len(difference):continue
        ix=set(rng.choice(len(difference),size=na,replace=False).tolist());part={v for i,v in enumerate(difference) if i in ix}
        changed+=int((common|part)!=rows[a]);rows[a]=common|part;rows[b]=common|(set(difference)-part)
    out=np.array([[int(c in row) for c in range(7)] for row in rows],dtype=np.int8)
    assert np.array_equal(out.sum(axis=0),B.sum(axis=0)) and np.array_equal(out.sum(axis=1),B.sum(axis=1))
    return out,changed

def scalar_cost(A,B,mapping):
    source=[sum(int(row[c]) for row in A)/len(A) for c in range(4)]
    mapped=[[int(any(row[j] and mapping[j]==c+1 for j in range(7))) for c in range(4)] for row in B]
    marginal=sum((sum(row[c] for row in mapped)/len(mapped)-source[c])**2 for c in range(4))/4
    extra=sum((sum(row[a]*row[b] for row in mapped)/len(mapped)-sum(int(row[a])*int(row[b]) for row in A)/len(A))**2 for a,b in PAIR)/6
    return marginal,marginal+extra
FOLDS=None
def init_null(folds):
    global FOLDS
    FOLDS=folds

def null_job(job):
    fi,wi=job;fold=FOLDS[fi];B,changed=shuffle_world(fold['B'],fi,wi);cs=costs(fold['A'],B);models=[summary(c,fold) for c in cs]
    return {'fold':fi,'world':wi,'B':B,'changed_trades':changed,'models':models,'delta':models[1]['macro']-models[0]['macro']}

def full_reconstruction():
    from concurrent.futures import ProcessPoolExecutor
    source=load_sources();folds=construct_folds(source);observed=[]
    for fold in folds:
        cs=costs(fold['A'],fold['B']);observed.append([summary(c,fold) for c in cs])
        ids=sorted(set([0,1,78124,*np.linspace(0,78124,13,dtype=int).tolist(),*(int(s['optima'][0]) for s in observed[-1])]))
        for mid in ids:assert close(scalar_cost(fold['A'],fold['B'],MAPS[mid]),[c[mid] for c in cs])
    with ProcessPoolExecutor(max_workers=16,initializer=init_null,initargs=(folds,)) as pool:
        nulls=list(pool.map(null_job,[(fi,wi) for fi in range(6) for wi in range(1,200)]))
    return source,folds,observed,nulls
def exact_macro(fold,optimum_ids):
    from fractions import Fraction
    value=Fraction(0)
    for j,gold in enumerate(fold['gold']):
        labels=collections.Counter(MAPS[optimum_ids,j].tolist())
        for c,q in enumerate(fold['concepts'],1):
            value+=Fraction(labels[c]*gold[q],len(optimum_ids)*sum(gold.values())*7)
    return value
def main():
    import base64
    from fractions import Fraction
    source,folds,observed,nulls=full_reconstruction();art=E/'artifacts'
    def artifact(name):
        p=art/name;return json.loads(gzip.decompress(p.read_bytes())) if name.endswith('.gz') else read(p)
    def decode_bitmap(text,n):return np.unpackbits(np.frombuffer(base64.b64decode(text),dtype=np.uint8),bitorder='little')[:n]
    assert MAPS.shape==(78125,7) and len({tuple(row) for row in MAPS})==78125
    assert np.all(MAPS[0]==0) and np.all(MAPS[-1]==4)
    projection=artifact('SOURCE_PROJECTION.json.gz');predictors=artifact('PREDICTOR_INPUTS.json');gold=artifact('GOLD.json');ao=artifact('OBSERVED.json.gz')
    reasonmap={'NO_COMMODITY':'EMPTY_COMMODITY','COMMODITY_DESCENDANT':'COMMODITY_BEARING_DESCENDANT','NONEMPTY_ANA':'NONEMPTY_ANA','NOT_ONE_TOKEN':'NOT_ONE_WHITESPACE_TOKEN'}
    checks=['registered_method_hashes_and_six_manifest_XML_hashes','all78125many_to_one_maps_including_OTHER_and_unused_slots']
    counts={}
    for coll,recipes in source.items():
        actual=projection['collections'][coll];assert len(actual)==len(recipes)
        count=collections.Counter(recipes=len(recipes))
        for a,p in zip(actual,recipes):
            assert a['collection']==coll and a['recipe_id']==p['recipe_id'] and a['recipe_ordinal']==p['recipe_ordinal']
            assert a['normalized_titles']==sorted(set(t for t in p['titles'] if t))
            for kind in ['events','excluded']:
                assert len(a[kind])==len(p[kind])
                for ar,pr in zip(a[kind],p[kind]):
                    expected={'source_id':f"{coll}|{pr['recipe_id']}|E{pr['element_ordinal']:04d}",'recipe_id':pr['recipe_id'],'element_ordinal':pr['element_ordinal'],'original_span':pr['original_span'],'surface':pr['form'],'concept':pr['q'],'english_label':pr['english_label'],'ana':pr['ana'],'reasons':[reasonmap[x] for x in pr['reasons']]}
                    assert ar==expected,(coll,ar['source_id'])
                    count['ingredient_elements']+=1;count['eligible' if kind=='events' else 'excluded']+=1
                    for reason in expected['reasons']:count['reason:'+reason]+=1
        counts[coll]=dict(count);assert projection['counts'][coll]==counts[coll]
    checks+=['all_recipe_denominators_including_zero_eligible','all_XML_spans_commodity_descendants_ana_single_token_and_exclusions','NFC_only_forms_source_element_ordinals_and_title_overlap_metadata']
    for fi,fold in enumerate(folds):
        coll=fold['held'];a=predictors[fi];g=gold[fi]
        assert set(a)=={'fold_index','held_collection','capacity','train_incidence','held_incidence'}
        assert a['fold_index']==fi and a['held_collection']==coll and a['capacity'] is True
        assert np.array_equal(a['train_incidence'],fold['A']) and np.array_equal(a['held_incidence'],fold['B'])
        assert g['concepts']==fold['concepts'] and [f['surface'] for f in g['forms']]==fold['forms']
        assert g['concept_recipe_presence']==dict(zip(fold['concepts'],fold['A'].sum(axis=0).tolist()))
        train=[(c,r) for c in COLLECTIONS if c!=coll for r in source[c]]
        assert g['training_recipe_ids']==[c+'|'+r['recipe_id'] for c,r in train] and g['held_recipe_ids']==[coll+'|'+r['recipe_id'] for r in source[coll]]
        total=sum(len(r['events']) for r in source[coll]);selected=sum(sum(x.values()) for x in fold['gold'])
        assert g['total_held_eligible_occurrences']==total and g['selected_form_occurrences']==selected and g['unselected_form_occurrences']==total-selected
        train_titles={t for c,r in train for t in r['titles'] if t};test_titles={t for r in source[coll] for t in r['titles'] if t}
        assert g['shared_normalized_titles']==sorted(train_titles&test_titles) and g['held_recipes_with_shared_title']==sum(bool(set(r['titles'])&train_titles) for r in source[coll])
        for j,f in enumerate(g['forms']):
            es=[e for r in source[coll] for e in r['events'] if e['form']==fold['forms'][j]]
            assert f['gold_counts']==dict(fold['gold'][j]) and f['occurrences']==len(es) and f['recipe_presence']==int(fold['B'][:,j].sum())
            assert f['source_ids']==[f"{coll}|{e['recipe_id']}|E{e['element_ordinal']:04d}" for e in es]
            assert f['original_spans']==sorted({e['original_span'] for e in es})
    checks+=['selection_without_held_gold_and_numeric_only_predictor_interfaces','all_gold_Q_mixtures_spelling_repetitions_and_source_coverage','exact_normalized_title_overlap_diagnostics']
    def match_model(a,p):
        assert close(a['minimum'],p['min']) and close(a['maximum'],p['max'])
        for prefix,ids in [('optimum',p['optima']),('envelope',p['envelope'])]:
            decoded=np.flatnonzero(decode_bitmap(a[prefix+'_bitmap_base64'],78125));assert np.array_equal(decoded,ids)
            assert a[prefix+'_count']==len(ids)
        assert a['canonical_mapping_id']==int(p['optima'][0]) and a['canonical_mapping']==MAPS[p['optima'][0]].tolist()
        prob=np.array([np.bincount(MAPS[p['optima'],j],minlength=5)/len(p['optima']) for j in range(7)])
        assert close(a['optimum_label_probabilities'],prob) and a['optimum_label_possibilities']==p['alternatives'] and a['envelope_label_possibilities']==p['envelope_alternatives']
        assert close(a['envelope_threshold'],p['min']+.01*(p['max']-p['min']))
        return prob
    def match_account(account,fold,models,full):
        exact={};form_scores={};probs={}
        for arm,p in zip(['F','G'],models):
            exact[arm]=exact_macro(fold,p['optima']);assert account['named_macro_exact'][arm]==[exact[arm].numerator,exact[arm].denominator]
            assert close(account['named_macro'][arm],float(exact[arm])) and close(account['occurrence_weighted_named'][arm],p['weighted'])
            probs[arm]=np.array([np.bincount(MAPS[p['optima'],j],minlength=5)/len(p['optima']) for j in range(7)])
            form_scores[arm]=np.sum(probs[arm]*fold['fractions'],axis=1)
            oov=int(fold['oov'].sum());other=float(probs[arm][:,0]@fold['oov']/oov) if oov else None
            assert account['correct_OTHER_rejection_rate'][arm] is None if other is None else close(account['correct_OTHER_rejection_rate'][arm],other)
        delta=exact['G']-exact['F'];assert account['delta_exact']==[delta.numerator,delta.denominator] and close(account['delta'],float(delta))
        if full:
            assert account['oov_occurrences']==int(fold['oov'].sum()) and len(account['forms'])==7
            upper=np.max(fold['fractions'],axis=1)
            assert close(account['oracle_named_macro_upper_bound'],float(upper.mean()))
            for j,row in enumerate(account['forms']):
                g=fold['gold'][j];n=sum(g.values());inside=sum(g[q] for q in fold['concepts'])
                assert row['form_index']==j and row['surface']==fold['forms'][j] and row['gold_counts']==dict(g) and row['occurrences']==n
                assert row['in_inventory_occurrences']==inside and row['out_of_inventory_occurrences']==n-inside
                assert close(row['oracle_single_label_named_upper_bound'],upper[j])
                assert row['contradictory_occurrence_counts_by_named_slot']=={q:n-g[q] for q in fold['concepts']}
                for arm in ['F','G']:assert close(row['named_accuracy'][arm],form_scores[arm][j]) and close(row['OTHER_probability'][arm],probs[arm][j,0])
                assert close(row['delta_G_minus_F'],form_scores['G'][j]-form_scores['F'][j])
        return delta,exact
    exact_observed=[]
    for fi,(a,fold,models) in enumerate(zip(ao,folds,observed)):
        assert a['fold_index']==fi and a['held_collection']==fold['held'] and a['status']=='COMPLETE'
        for arm,p in zip(['F','G'],models):match_model(a['models'][arm],p)
        exact_observed.append(match_account(a['account'],fold,models,True))
    checks+=['all_observed_costs_optima_and_1percent_envelopes_reconstructed','scalar_cost_crosschecks_for_extreme_sampled_and_optimal_maps','uniform_all_optima_gold_accuracy_OTHER_zero_and_polysemy_upper_bounds']
    exact_null={w:Fraction(0) for w in range(1,200)};null_rows={};bykey={(n['fold'],n['world']):n for n in nulls}
    for fi,fold in enumerate(folds):
        rows=artifact(f'NULL_FOLD_{fi}.json.gz');null_rows[fi]=rows;assert len(rows)==199
        for wi,a in enumerate(rows,1):
            n=bykey[fi,wi];B=n['B']
            assert a['fold_index']==fi and a['world_index']==wi and a['seed']==1159000+1000*fi+wi
            assert a['matrix_shape']==list(B.shape) and np.array_equal(decode_bitmap(a['matrix_bitmap_base64'],B.size).reshape(B.shape),B)
            assert a['matrix_sha256']==hashlib.sha256(B.astype(np.uint8).tobytes()).hexdigest()
            assert a['row_sums']==B.sum(axis=1).tolist() and a['column_sums']==B.sum(axis=0).tolist()
            assert a['changed_cells']==int(np.count_nonzero(B!=fold['B'])) and a['changed_trades']==n['changed_trades']
            for arm,p in zip(['F','G'],n['models']):match_model(a['models'][arm],p)
            delta,_=match_account(a,fold,n['models'],False);exact_null[wi]+=delta/6
    checks+=['all1194Curveball_worlds_exact_seeds_100N_trades_and_margins','both_arms_refit_all78125maps_in_every_null_world','all_null_optima_envelopes_uniform_gold_scores_and_changes']
    aggregate=artifact('NULL_AGGREGATE.json');assert len(aggregate)==199
    for wi,row in enumerate(aggregate,1):
        d=exact_null[wi];assert row['world_index']==wi and row['delta_exact']==[d.numerator,d.denominator] and close(row['delta'],float(d))
        assert close(row['fold_deltas'],[null_rows[fi][wi-1]['delta'] for fi in range(6)])
    exact_means={arm:sum((pair[1][arm] for pair in exact_observed),Fraction(0))/6 for arm in ['F','G']};delta=exact_means['G']-exact_means['F'];positive=sum(pair[0]>0 for pair in exact_observed);ge=sum(d>=delta for d in exact_null.values());rank=Fraction(1+ge,200)
    result=artifact('RESULT.json');passed=delta>=Fraction(1,20) and positive>=4 and rank<=Fraction(1,20)
    status='SUPPORTED_LIMITED_SOURCE_RECOVERY' if passed else 'NO_SUPPORTED_GRAPH_LEXICAL_INCREMENT'
    assert result['status']==status and result['folds']==6 and result['forms']==42 and result['assignments_per_fit']==78125 and result['fitted_worlds_including_observed']==1200
    assert result['source_counts']==counts and result['positive_folds']==positive and result['null_aggregate_at_least_observed']==ge and result['null_worlds_per_fold']==199
    assert result['delta_exact']==[delta.numerator,delta.denominator] and close(result['delta'],float(delta)) and close(result['conditional_control_rank'],float(rank))
    for arm,v in exact_means.items():assert result['named_macro_exact'][arm]==[v.numerator,v.denominator] and close(result['named_macro'][arm],float(v))
    for fi,row in enumerate(result['fold_results']):
        assert row['collection']==folds[fi]['held'] and close(row['delta'],float(exact_observed[fi][0]))
        assert row['unique_null_matrices']==len({r['matrix_sha256'] for r in null_rows[fi]}) and row['unchanged_null_worlds']==sum(r['changed_cells']==0 for r in null_rows[fi])
        assert row['optimum_counts']=={arm:len(p['optima']) for arm,p in zip(['F','G'],observed[fi])}
        assert row['envelope_counts']=={arm:len(p['envelope']) for arm,p in zip(['F','G'],observed[fi])}
    assert result['voynich_access'] is False and result['voynich_meanings']==0 and all(result[k] is False for k in ['calibrated_probability_claim','uniform_null_mixing_claim','general_significance_claim'])
    checks+=['exact_Fraction_inclusive_aggregate_rank_without_epsilon_repair','all_fixed_continuation_gates_and_null_capacity_diagnostics','source_control_only_no_Voynich_or_semantic_probability_claim']
    out={'status':'PASS','checks_passed':len(checks),'checks':checks,'scientific_decision':status,'folds':6,'maps_each_fit':78125,'full_null_worlds_independently_regenerated_and_refit':1194,'named_macro_exact':{a:[v.numerator,v.denominator] for a,v in exact_means.items()},'delta_exact':[delta.numerator,delta.denominator],'positive_folds':positive,'conditional_control_rank_exact':[rank.numerator,rank.denominator],'arithmetic_correction':'Exact rational evaluation of uniform-optimum gold means preserves inclusive ties; no fitted cost, map, null or gate changed.','limitations':['Oracle ingredient boundaries and oracle training Q normalization make this a favorable source control.','Prior exposure, nested recipe structure and substantial title overlap prevent independent historical replication claims.','Curveball margins and deterministic draws verified; uniform mixing is not established.','No Voynich structural-unit homology, word meaning or language identified.']}
    (art/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['checks','limitations']}))
if __name__=='__main__':main()
