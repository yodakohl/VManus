#!/usr/bin/env python3
"""Independent frozen cross-situational pipeline audit, no runner imports."""
import collections
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import re
import numpy as np

E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
CODES=['HORIZONTAL_BEADS','BASAL_SWOLLEN_BRANCHES','RADIATE_HEAD','SPINY_ROUND_HEAD','BROAD_PETAL_FLOWER','MULTI_UNIT_SPIKE']
BETAS=[0,-.25,.25,-.5,.5,-1,1,-2,2,-4,4]
STATES=np.array(list(itertools.product([0,1],repeat=6)),dtype=int)
def read(p):return json.loads(p.read_text())
def sigmoid(z):return 1/(1+np.exp(-z))
def close(a,b):return np.allclose(a,b,rtol=1e-9,atol=1e-11,equal_nan=True)

def evaluate(features,Y,pages,strata,full=False):
    n,w=Y.shape;leaf=np.array([int(re.match(r'f(\d+)',p)[1]) for p in pages]);leaves=sorted(set(leaf.tolist()));fcount=len(leaves)
    held_visual=np.zeros((n,w));held_count=np.zeros((n,w));held_base=np.zeros((n,w));unique_positive=np.zeros((fcount,w,6),bool);records=[]
    for fi,heldleaf in enumerate(leaves):
        tr=np.flatnonzero(leaf!=heldleaf);te=np.flatnonzero(leaf==heldleaf)
        g=(Y[tr].sum(axis=0)+.5)/(len(tr)+1)
        baseline=np.empty((n,w))
        for st in sorted(set(strata)):
            trainst=[i for i in tr if strata[i]==st];ix=[i for i in range(n) if strata[i]==st]
            baseline[ix]=(Y[trainst].sum(axis=0)+10*g)/(len(trainst)+10)
        logits=np.log(baseline)-np.log1p(-baseline)
        baseobj=np.sum(np.where(Y[tr],np.log(baseline[tr]),np.log1p(-baseline[tr])),axis=0)
        wordcap=np.array([sum(bool(Y[(leaf==l)&(leaf!=heldleaf),j].any()) for l in leaves if l!=heldleaf)>=2 for j in range(w)])
        complete=features[tr][np.all(features[tr]>=0,axis=1)]
        statecount=np.ones(64)/64
        for state in complete:statecount[np.flatnonzero(np.all(STATES==state,axis=1))[0]]+=1
        joint=statecount/statecount.sum()
        conditional=np.empty((n,64))
        for i,obs in enumerate(features):
            legal=np.all((obs<0)|(STATES==obs),axis=1);mass=joint*legal;conditional[i]=mass/mass.sum()
        eligible=[];objectives=[baseobj];preds=[baseline[te]];names=['BACKGROUND'];params=[np.zeros(w)];detail=[]
        count_pred=baseline[te].copy();count_beta=np.zeros(w);count_obj=baseobj.copy()
        for f in range(7):
            values=STATES[:,f] if f<6 else STATES.sum(axis=1)
            supports=np.arange(2 if f<6 else 7)
            mass=np.stack([conditional[:,values==v].sum(axis=1) for v in supports],axis=1)
            mu=np.mean(mass[tr]@supports);var=np.mean(mass[tr]@(supports**2))-mu**2
            elig=(len(set(leaf[tr][features[tr,f]==1]))>=2 and len(set(leaf[tr][features[tr,f]==0]))>=2) if f<6 else True
            eligible.append(bool(elig));betas=BETAS if var>1e-12 else [0]
            z=(supports-mu)/math.sqrt(var) if var>1e-12 else np.zeros(len(supports))
            objs=[];ptest=[]
            for beta in betas:
                probability=np.sum(sigmoid(logits[:,:,None]+beta*z[None,None,:])*mass[:,None,:],axis=2)
                objective=np.sum(np.where(Y[tr],np.log(probability[tr]),np.log1p(-probability[tr])),axis=0)-beta**2/2
                objs.append(objective);ptest.append(probability[te])
            objs=np.stack(objs);best=objs.max(axis=0);which=np.argmax(objs>=best[None,:]-1e-12,axis=0)
            selected_beta=np.array(betas)[which];selected_obj=objs[which,np.arange(w)];selected_pred=np.stack(ptest)[which,:,np.arange(w)].T
            raw_beta=selected_beta.copy();raw_obj=selected_obj.copy()
            selected_beta=np.where(wordcap,selected_beta,0);selected_obj=np.where(wordcap,selected_obj,baseobj);selected_pred=np.where(wordcap[None,:],selected_pred,baseline[te])
            if f<6 and elig:
                objectives.append(np.where(wordcap,selected_obj,-np.inf));preds.append(selected_pred);names.append(CODES[f]);params.append(selected_beta)
            elif f==6:count_pred=selected_pred;count_beta=selected_beta;count_obj=selected_obj
            detail.append({'eligible':bool(elig),'mean':float(mu),'variance':float(var),'beta':selected_beta.tolist(),'objective':selected_obj.tolist(),'raw_beta':raw_beta.tolist(),'raw_objective':raw_obj.tolist()})
        objective=np.stack(objectives);mx=objective.max(axis=0);ties=objective>=mx[None,:]-1e-12
        pv=np.stack(preds);visual=np.sum(pv*ties[:,None,:],axis=0)/ties.sum(axis=0)[None,:]
        for j in range(w):
            ids=np.flatnonzero(ties[:,j])
            if len(ids)==1 and ids[0]>0 and params[ids[0]][j]>0:unique_positive[fi,j,CODES.index(names[ids[0]])]=True
        held_visual[te]=visual;held_count[te]=count_pred;held_base[te]=baseline[te]
        if full:records.append({'leaf':heldleaf,'train':tr.tolist(),'test':te.tolist(),'word_capacity':wordcap.tolist(),'feature_eligible':eligible[:6],'joint':joint.tolist(),'conditional':conditional.tolist(),'global':g.tolist(),'baseline':baseline.tolist(),'features':detail,'selected_names':[[names[k] for k in np.flatnonzero(ties[:,j])] for j in range(w)],'selected_betas':[[float(params[k][j]) for k in np.flatnonzero(ties[:,j])] for j in range(w)],'COUNT_beta':count_beta.tolist(),'COUNT_objective':count_obj.tolist()})
    logs=[]
    for pred in [held_base,held_visual,held_count]:logs.append(np.log2(np.where(Y,pred,1-pred)))
    gain_base=np.mean([np.mean(logs[1][leaf==l]-logs[0][leaf==l],axis=0) for l in leaves],axis=0)
    gain_count=np.mean([np.mean(logs[1][leaf==l]-logs[2][leaf==l],axis=0) for l in leaves],axis=0)
    stable_counts=unique_positive.sum(axis=0);present_yes=np.zeros((w,6),int)
    for j in range(w):
        for f in range(6):present_yes[j,f]=len(set(leaf[(Y[:,j]==1)&(features[:,f]==1)]))
    stable=stable_counts>=.8*fcount;binding=(stable & (present_yes>=3)).any(axis=1)
    gate=(gain_base>=.01)&(gain_count>=.01)&binding
    T=np.where(gate,np.minimum(gain_base,gain_count),np.nan)
    return {'gain_base':gain_base,'gain_count':gain_count,'unique_counts':stable_counts,'present_yes':present_yes,'gates':gate,'T':T,'max':float(np.nanmax(T)) if gate.any() else 0.,'pred_base':held_base,'pred_visual':held_visual,'pred_count':held_count,'folds':records,'leaves':leaves}
def load_inputs():
    import csv
    for name,digest in read(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    source=read(E/'src/SOURCE.json'); metadata=read(E/'src/METADATA.json')
    def selected_tsv(path,cols):
        with (ROOT/path).open() as f:
            rows=csv.reader(f,delimiter='\t');header=next(rows);indices=[header.index(c) for c in cols]
            return [dict(zip(cols,(row[i] for i in indices))) for row in rows]
    pages=sorted(r['folio'] for r in selected_tsv(source['image_roster'],['folio']));assert len(pages)==38 and len(set(pages))==38
    wordsrows=selected_tsv(source['word_presence']['file'],['word','image_folio_ids']);words=sorted(r['word'] for r in wordsrows);assert len(words)==169 and len(set(words))==169
    byword={r['word']:set(r['image_folio_ids'].split(';')) for r in wordsrows}
    assert all(s<=set(pages) for s in byword.values())
    Y=np.array([[int(p in byword[w]) for w in words] for p in pages])
    observations=[]
    for path in source['observer_codes']:
        rows=selected_tsv(path,['folio']+CODES);by={r['folio']:r for r in rows};assert set(by)==set(pages)
        observations.append([[by[p][c] for c in CODES] for p in pages])
    raw=np.array(observations)
    features=np.full((38,6),-1,int)
    features[(raw[0]=='YES')&(raw[1]=='YES')]=1;features[(raw[0]=='NO')&(raw[1]=='NO')]=0
    actual={}
    for path in source['metadata_sources']:
        for line in read(ROOT/path)['lines']:
            m=line['metadata']
            if m['page'] in pages:
                values={k:m[k] for k in ['section','currier','hand']}
                assert m['page'] not in actual or actual[m['page']]==values
                actual[m['page']]=values
    assert metadata==actual and set(metadata)==set(pages)
    allowed=set(read(ROOT/'experiments/yolo/gdt915_terminal_lr_phrase_transfer/src/SPEC.json')['allowed_selectors'])
    assert set(pages)<=allowed and all(not p.startswith(('f84','f116v')) for p in pages)
    strata=[(metadata[p]['hand'],metadata[p]['currier']) for p in pages]
    leafrows=collections.defaultdict(list)
    for i,p in enumerate(pages):leafrows[int(re.match(r'f(\d+)',p)[1])].append(i)
    blocks=collections.defaultdict(list)
    for leaf,indices in leafrows.items():
        signature=tuple(sorted((pages[i][-1],*strata[i]) for i in indices));blocks[signature].append(leaf)
    blocks={k:sorted(v) for k,v in sorted(blocks.items())}
    return pages,words,Y,features,raw,strata,leafrows,blocks

def assignments(features,raw,pages,leafrows,blocks):
    rng=random.Random(1157);worlds=[];receipt=[];mobile=0;orbit=1
    def bundle(leaf,data):
        ix=sorted(leafrows[leaf],key=lambda i:pages[i][-1])
        return tuple(tuple(data[i].tolist()) for i in ix)
    for sig,leaves in blocks.items():
        types=collections.Counter(bundle(l,features) for l in leaves)
        norbit=math.factorial(len(leaves))
        for c in types.values():norbit//=math.factorial(c)
        orbit*=norbit
        if len(types)>1:mobile+=len(leaves)
        receipt.append({'signature':sig,'leaves':leaves,'types':types,'orbit':norbit})
    for replicate in range(1,200):
        mapping=np.arange(len(pages));donors={}
        for sig,leaves in blocks.items():
            shuffled=leaves.copy();rng.shuffle(shuffled)
            for recipient,donor in zip(leaves,shuffled):
                donors[recipient]=donor
                source={pages[i][-1]:i for i in leafrows[donor]}
                for i in leafrows[recipient]:mapping[i]=source[pages[i][-1]]
        worlds.append({'replicate':replicate,'mapping':mapping,'donors':donors,'features':features[mapping],'raw':raw[:,mapping,:]})
    return worlds,receipt,mobile,orbit
def null_evaluate(payload):
    features,Y,pages,strata=payload
    result=evaluate(features,Y,pages,strata)
    return {k:v for k,v in result.items() if k not in ['pred_base','pred_visual','pred_count','folds']}

def full_reconstruction(workers=16):
    from concurrent.futures import ProcessPoolExecutor
    inputs=load_inputs();pages,words,Y,features,raw,strata,leafrows,blocks=inputs
    observed=evaluate(features,Y,pages,strata,full=True)
    worlds,receipt,mobile,orbit=assignments(features,raw,pages,leafrows,blocks)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        results=list(pool.map(null_evaluate,[(world['features'],Y,pages,strata) for world in worlds]))
    return inputs,observed,worlds,receipt,mobile,orbit,results
def scalar_checks(inputs,observed):
    pages,words,Y,features,raw,strata,leafrows,blocks=inputs
    checked=0
    for foldindex in [0,len(observed['folds'])//2,len(observed['folds'])-1]:
        fold=observed['folds'][foldindex];train=fold['train'];post=fold['conditional']
        for wordindex in [0,len(words)//2,len(words)-1]:
            for feature in range(7):
                detail=fold['features'][feature];values=[int(s[feature]) if feature<6 else int(sum(s)) for s in STATES]
                mu=detail['mean'];var=detail['variance'];z=[(v-mu)/math.sqrt(var) if var>1e-12 else 0 for v in values]
                objectives=[]
                for beta in BETAS if var>1e-12 else [0]:
                    terms=[]
                    for i in train:
                        p=fold['baseline'][i][wordindex];offset=math.log(p/(1-p))
                        probability=sum(weight/(1+math.exp(-(offset+beta*zz))) for weight,zz in zip(post[i],z))
                        terms.append(math.log(probability if Y[i,wordindex] else 1-probability))
                    objectives.append((beta,sum(terms)-beta**2/2))
                maximum=max(v for b,v in objectives);beta,obj=next((b,v) for b,v in objectives if v>=maximum-1e-12)
                assert beta==detail['raw_beta'][wordindex] and close(obj,detail['raw_objective'][wordindex])
                checked+=1
    return checked

def main():
    import gzip
    data=full_reconstruction();inputs,observed,worlds,receipt,mobile,orbit,nulls=data
    pages,words,Y,features,raw,strata,leafrows,blocks=inputs;art=E/'artifacts'
    def artifact(name):
        path=art/name
        return json.loads(gzip.decompress(path.read_bytes())) if name.endswith('.gz') else read(path)
    def digest(x):return hashlib.sha256(json.dumps(x,separators=(',',':')).encode()).hexdigest()
    checks=['all11pins_before_source_read','fixed169wholeforms38images_and_projected_presence_columns','six_consensus_features_preserve_unknown','metadata_reconstructed_from915_cache_and32wholeleaf_folds']
    actual=artifact('INPUT.json')
    assert actual['pages']==pages and actual['words']==words and actual['features']==CODES and actual['beta_grid']==sorted(BETAS)
    assert actual['metadata']==read(E/'src/METADATA.json') and actual['representation']=='ZL3b'
    assert actual['leaf_ids']==[int(re.match(r'f(\d+)',p)[1]) for p in pages]
    assert np.array_equal(actual['word_presence'],Y) and np.array_equal(actual['consensus'],features) and np.array_equal(actual['codes_A_B'],np.transpose(raw,(1,2,0)))
    cap=artifact('CAPACITY.json');capacity=mobile>=12 and orbit>=100
    assert cap['leaf_count']==len(leafrows) and cap['mobile_leaves']==mobile and cap['observable_orbit']==orbit and cap['capacity']==capacity
    assert len(cap['blocks'])==len(receipt)
    for a,p in zip(cap['blocks'],receipt):
        assert a['signature']==[list(s) for s in p['signature']] and a['leaves']==p['leaves'] and a['observable_orbit']==p['orbit']
        mult={json.dumps([list(row) for row in key]):v for key,v in p['types'].items()}
        assert a['observable_bundle_multiplicities']==mult and a['mobile_leaves']==(len(p['leaves']) if len(p['types'])>1 else 0)
        assert a['positions']=={str(l):sorted(leafrows[l],key=lambda i:pages[i][-1]) for l in p['leaves']}
    checks.append('effective_observable_orbit_not_raw_disagreement_capacity')
    af=artifact('OBSERVED_FOLDS.json.gz');assert len(af)==len(observed['folds'])
    for a,p in zip(af,observed['folds']):
        tr=p['train'];te=p['test'];held=p['leaf'];wc=np.array(p['word_capacity'])
        assert a['held_leaf']==held and a['train_pages']==[pages[i] for i in tr] and a['test_pages']==[pages[i] for i in te]
        assert a['train_word_counts']==Y[tr].sum(axis=0).tolist()
        positive=np.sum([Y[indices].max(axis=0) for l,indices in leafrows.items() if l!=held],axis=0)
        assert a['train_positive_leaf_counts']==positive.tolist() and a['word_capacity']==p['word_capacity']
        assert a['feature_definite_yes_leaves']==[sum(any(features[i,j]==1 for i in ix) for l,ix in leafrows.items() if l!=held) for j in range(6)]
        assert a['feature_definite_no_leaves']==[sum(any(features[i,j]==0 for i in ix) for l,ix in leafrows.items() if l!=held) for j in range(6)]
        assert a['feature_eligible']==p['feature_eligible']
        assert close(a['baseline_global'],p['global']) and close(a['baseline_stratum'],p['baseline'][0])
        totalmass=1+sum(np.all(features[i]>=0) for i in tr)
        assert close(a['joint_state_prior_mass'],np.array(p['joint'])*totalmass) and close(a['conditional_state_probabilities'],p['conditional'])
        assert close(a['training_means'],[v['mean'] for v in p['features']]) and close(a['training_variances'],[v['variance'] for v in p['features']])
        for j,(aa,pp) in enumerate(zip(a['feature_fits'],p['features'][:6])):
            assert aa['feature']==CODES[j] and aa['eligible']==pp['eligible']
            if pp['eligible']:assert close(aa['beta'],pp['raw_beta']) and close(aa['objective'],pp['raw_objective'])
        for j in range(len(words)):
            assert set(a['selected_models'][j])==set(p['selected_names'][j]),(held,words[j],'ties')
            ownnames=p['selected_names'][j];ownbetas=p['selected_betas'][j]
            unique=ownnames[0] if len(ownnames)==1 and ownnames[0]!='BACKGROUND' and ownbetas[0]>0 else None
            assert a['selected_positive_unique_feature'][j]==unique
        assert close(a['count_beta'],p['COUNT_beta']) and close(a['count_objective'],p['COUNT_objective'])
        for label,key in [('visual_p_yes','pred_visual'),('count_p_yes','pred_count'),('background_p_yes','pred_base')]:assert close(a['predictions'][label],observed[key][te])
        lp={name:np.log2(np.where(Y[te],observed[key][te],1-observed[key][te])) for name,key in [('v','pred_visual'),('c','pred_count'),('b','pred_base')]}
        assert close(a['gain_over_background'],np.mean(lp['v']-lp['b'],axis=0)) and close(a['gain_over_count'],np.mean(lp['v']-lp['c'],axis=0))
        base=np.array(p['baseline'])[tr];assert close(a['background_objective'],np.sum(np.where(Y[tr],np.log(base),np.log1p(-base)),axis=0))
    scalar_count=scalar_checks(inputs,observed)
    checks+=['all32folds_counts_joint64states_conditioning_and_latent_variance','all_feature_and_COUNT_grid_fits_ridge_objectives_and_ties','all_observed_held_probabilities_and_leaf_weighted_gains','all_aliases_ineligible_and_word_capacity_fallbacks',f'{scalar_count}_direct64state_scalar_grid_crosschecks']
    def candidates_match(actual_rows,ours):
        assert len(actual_rows)==169
        for j,row in enumerate(actual_rows):
            assert row['word']==words[j] and close(row['gain_over_background'],ours['gain_base'][j]) and close(row['gain_over_count'],ours['gain_count'][j])
            assert row['positive_unique_fold_counts']==ours['unique_counts'][j].tolist() and row['joint_word_definite_yes_leaves']==ours['present_yes'][j].tolist()
            qualifying=[CODES[f] for f in range(6) if ours['unique_counts'][j,f]/len(leafrows)>=.8 and ours['present_yes'][j,f]>=3]
            assert row['qualifying_features']==qualifying and row['gates_pass']==bool(ours['gates'][j])
            assert (row['T'] is None and np.isnan(ours['T'][j])) or close(row['T'],ours['T'][j])
            reasons=[]
            if ours['gain_base'][j]<.01:reasons.append('BACKGROUND_GAIN_BELOW_0_01')
            if ours['gain_count'][j]<.01:reasons.append('COUNT_GAIN_BELOW_0_01')
            if not np.any(ours['unique_counts'][j]/len(leafrows)>=.8):reasons.append('NO_FEATURE_80_PERCENT_UNIQUE_POSITIVE_FOLDS')
            if not qualifying:reasons.append('NO_SAME_FEATURE_STABILITY_AND_THREE_JOINT_YES_LEAVES')
            assert row['failure_reasons']==reasons
    ac=artifact('CANDIDATES.json');candidates_match(ac,observed)
    an=artifact('NULL_RESULTS.json.gz');assert len(an)==len(worlds)==len(nulls)==199
    rawhashes=[];obshashes=[]
    for a,p,n in zip(an,worlds,nulls):
        assert a['replicate']==p['replicate'] and a['page_donor_indices']==p['mapping'].tolist()
        rawhash=digest(np.transpose(p['raw'],(1,2,0)).tolist());obshash=digest(p['features'].tolist());rawhashes.append(rawhash);obshashes.append(obshash)
        assert a['raw_world_hash']==rawhash and a['observable_world_hash']==obshash
        candidates_match(a['candidates'],n);assert close(a['maximum'],n['max'])
    checks+=['all199_seeded_wholeleaf_face_preserving_bundle_assignments_and_hashes','all33631null_word_candidates_gates_and_search_maxima']
    nominated=[]
    for j,row in enumerate(ac):
        rank=(1+sum(n['max']>=observed['T'][j]-1e-12 for n in nulls))/200 if observed['gates'][j] else None
        assert row['search_reference_rank']==rank and row['nominated']==bool(capacity and rank is not None and rank<=.05)
        if row['nominated']:nominated.append(row)
    aliases=artifact('ALIASES.json')['exact_observed_mask_aliases']
    expected_aliases=[{'features':[CODES[a],CODES[b]],'relationship':'IDENTICAL_CONSENSUS_TERNARY_MASKS'} for a,b in itertools.combinations(range(6),2) if np.array_equal(features[:,a],features[:,b])]
    assert aliases==expected_aliases
    result=artifact('RESULT.json');status='NO_CAPACITY' if not capacity else 'FEATURE_COMPATIBLE_WORD_LEADS' if nominated else 'NO_SUPPORTED_VISUAL_WORD_LEAD'
    assert result['status']==status and result['capacity']==capacity and result['nominees']==nominated
    assert result['observed_gate_pass_words']==[words[j] for j in range(169) if observed['gates'][j]]
    assert result['null_positive_maxima']==sum(n['max']>0 for n in nulls) and result['unique_raw_worlds']==len(set(rawhashes)) and result['unique_observable_worlds']==len(set(obshashes))
    assert result['pages']==38 and result['leaves']==32 and result['words']==169 and result['null_draws']==199 and result['features']==CODES and result['mobile_leaves']==mobile and result['observable_orbit']==orbit
    assert result['meanings']==0 and all(result[k] is False for k in ['authorial_owner_claim','project_wide_significance_claim','independent_confirmation'])
    checks+=['all_observed_search_ranks_aliases_and_final_decision','zero_semantic_owner_or_project_wide_significance_claim']
    out={'status':'PASS','checks_passed':len(checks),'checks':checks,'scientific_decision':status,'observed_words':169,'outer_folds':32,'null_worlds_recomputed':199,'null_word_candidates_recomputed':199*169,'direct_scalar_grid_checks':scalar_count,'mobile_leaves':mobile,'observable_orbit':orbit,'observed_pre_rank_words':result['observed_gate_pass_words'],'nominated_words':[r['word'] for r in nominated],'limitations':['Previously selected and exposed image roster and word inventory: reference ranks do not cover historical project selection.','Baseline adjusts page prevalence and hand/Currier, not page text length, token exposure or word position. Generic visual COUNT is not a text-length control.','Feature prediction does not identify an authorial referent, organ name or word meaning.','Inherited frozen observer codes were not reannotated; no new images or reserved sources opened.','Failure closes this fixed estimator, not cross-situational inference in general.']}
    (art/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
    text=['# GDT1157 independent validation','','PASS: '+str(len(checks))+' check groups.','','All observed folds and all 199 complete search worlds independently reconstructed, including every word candidate, ambiguity conditioning, fixed grid selection and search maximum. No runner scientific functions imported. Additional direct scalar integration over all 64 latent states checked '+str(scalar_count)+' selected grid fits.','','Decision: '+status+'.','','## Checks','']+['- '+c for c in checks]+['','## Limits','']+['- '+c for c in out['limitations']]
    (art/'VALIDATION.md').write_text('\n'.join(text)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['checks','limitations']}))

if __name__=='__main__':main()
