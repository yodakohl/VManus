#!/usr/bin/env python3
"""Independent GDT960 audit.  No import of run.py or solver helper."""
from collections import defaultdict, Counter
from pathlib import Path
import csv,gzip,hashlib,json,re
from concurrent.futures import ProcessPoolExecutor
import z3

EXP=Path(__file__).resolve().parents[1]; ROOT=EXP.parents[2]; ART=EXP/'artifacts'
G915=ROOT/'experiments/yolo/gdt915_terminal_lr_phrase_transfer'; G928=ROOT/'experiments/yolo/gdt928_multi_anchor_complete_paragraphs'
ED=('ZL3b','IT2a','RF1b'); MOD=('MATERIAL','PLANT_IDENTITY'); DIR=('ORIGINAL','REVERSED'); ALLOWED={'DEFINITE_SPACE','LINE_START','LINE_END'}
def load(p):return json.load(p) if hasattr(p,'read') else json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bit(rows,rev=False):return sum(1<<(14-(r-1) if rev else r-1) for r in rows)

def raw_groups(spec):
    files=[ROOT/x for x in spec['sources']]
    allowed=set(load(ROOT/spec['allow_source'])['allowed_selectors'])
    assert len(allowed)==179 and not any(p.startswith('f84') or p=='f116v' for p in allowed)
    # Use both fixed discovery/evaluation caches; paragraph IDs resolve to evaluation rows.
    out={}
    for p in files:
        x=load(p)
        for line in x['lines']:
            m=line['metadata']
            assert m['page'] in allowed
            for g in line['groups']:
                assert g[0] not in out
                out[g[0]]=dict(m,source_group_id=g[0],source_group_index=g[1],ivtff_group_raw=g[2],left_separator=g[3],right_separator=g[4])
    return out

def paragraph_windows(spec, source_map):
    para=load(G928/'artifacts/PARAGRAPHS.json'); windows=[]
    for ed in ('ZL3b','IT2a'):
        bypage=defaultdict(list)
        for p in para[ed]:bypage[p['page']].append(p)
        for page,ps in sorted(bypage.items()):
            ps.sort(key=lambda p:p['lines'][0]['row'])
            for i in range(max(0,len(ps)-14)):
                chunk=ps[i:i+15]
                if len(chunk)<15:continue
                # The cache is already source ordered; retain only adjacent loci.
                starts=[int(re.search(r'\.(\d+)$',p['lines'][0]['locus']).group(1)) for p in chunk]
                ends=[int(re.search(r'\.(\d+)$',p['lines'][-1]['locus']).group(1)) for p in chunk]
                if any(b != a+1 for a,b in zip(ends,starts[1:])):continue
                pars=[]; masks=defaultdict(int); unknown=[]
                for j,p in enumerate(chunk):
                    groups=[]
                    for line in p['lines']:
                        for sid in line['source_ids']:
                            g=dict(source_map[sid]); reasons=[]
                            if not re.fullmatch(r'[a-z]+',g['ivtff_group_raw']):reasons.append('NONLITERAL')
                            if g['left_separator'] not in ALLOWED or g['right_separator'] not in ALLOWED:reasons.append('UNCERTAIN_BOUNDARY')
                            g['known']=not reasons;g['unknown_reasons']=reasons;groups.append(g)
                            if g['known']:masks[g['ivtff_group_raw']] |= 1<<j
                    pars.append({'id':p['id'],'lines':[x['locus'] for x in p['lines']],'groups':groups})
                    unknown.append(sum(not g['known'] for g in groups))
                # GDT928's stable window identifier is keyed by the first
                # complete paragraph; paragraph_ids retains the whole span.
                first=chunk[0]['id'].split('|',1)[1]
                wid=f'{ed}|{page}|{first}'
                windows.append({'window_id':wid,'edition':ed,'page':page,'physical_leaf':int(re.search(r'\d+',page).group()),'paragraph_ids':[p['id'] for p in chunk],'paragraphs':pars,'word_masks':dict(sorted(masks.items())),'unknown_slots':unknown})
    return windows

def z3_upper(req,domains,unknown):
    # domain entries are (word, known_mask, missing_mask, fresh_unknown)
    words=sorted({x[0] for ds in domains.values() for x in ds if not x[3]}); ids={w:i for i,w in enumerate(words)}
    nxt=len(ids); choices={}; masks={}
    for plant,ds in domains.items():
        choices[plant]=[]
        for word,km,mm,fresh in ds:
            code=ids[word] if not fresh else nxt
            if fresh:nxt+=1
            choices[plant].append((code,km,word))
            masks[code]=km
    plants=list(domains); vs={p:z3.Int('v_'+str(i)) for i,p in enumerate(plants)}
    constraints=[z3.Distinct(list(vs.values()))]
    for p in plants:constraints.append(z3.Or([vs[p]==code for code,_,_ in choices[p]]))
    for row,cap in enumerate(unknown):
        needing=[p for p in plants if req[p]&(1<<row)]
        if len(needing)<=cap:continue  # Capacity bound is then tautological.
        cost=[]
        for p in needing:
            needs_unknown=[vs[p]==code for code,km,_ in choices[p] if not km&(1<<row)]
            cost.append(z3.If(z3.Or(needs_unknown),1,0))
        constraints.append(z3.Sum(cost)<=cap)
    sol=z3.Solver();sol.set(timeout=15000);sol.add(*constraints);status=sol.check();feas={p:[] for p in plants}; witness={}
    if status==z3.sat:
        model=sol.model(); witness={p:next(word for code,km,word in choices[p] if model.eval(vs[p]).as_long()==code) for p in plants}
        # Real words with the same known mask have identical eligibility and
        # row cost in EVERY plant domain. Swapping their integer names globally
        # preserves Distinct and all constraints. Force one representative of
        # each orbit and transfer only through this checked bijection.
        eligibility={word:tuple((p,km) for p in plants for _,km,w in choices[p] if w==word) for word in words}
        for p in plants:
            orbit={}
            for code,km,word in choices[p]:
                key=('fresh',word) if word.startswith('<UNKNOWN:') else ('known',km,eligibility[word])
                if key not in orbit:
                    sol.push();sol.add(vs[p]==code);check=sol.check();sol.pop()
                    assert check!=z3.unknown, 'independent marginal unresolved'
                    orbit[key]=check==z3.sat
                feas[p].append((word,orbit[key]))
    return ('sat' if status==z3.sat else 'unsat' if status==z3.unsat else 'unknown'),feas,witness

def calculate_case(args):
    w,model,direction,incidence=args
    plants=list(incidence); cases=[];pred_rows=[]
    req={p:bit(rows,direction=='REVERSED') for p,rows in incidence.items()}; unknown=w['unknown_slots']; wm=w['word_masks']
    known_domains={p:sorted([word for word,m in wm.items() if m==req[p]]) for p in plants}
    lower=1
    bymask=defaultdict(lambda:[0,0])
    for p in plants:bymask[req[p]][0]+=1
    for word,m in wm.items():bymask[m][1]+=1
    for need,(np,nw) in bymask.items():
        if nw<np:lower=0
        else:
            q=1
            for k in range(nw-np+1,nw+1):q*=k
            lower*=q
    domains={}
    available_unknown=sum((1<<i) for i,n in enumerate(unknown) if n>0)
    for p in plants:
        ds=[(word,m,req[p]&~m,False) for word,m in sorted(wm.items())
            if m & ~req[p]==0 and (req[p]&~m)&~available_unknown==0]
        if req[p]&~available_unknown==0:
            ds.append((f'<UNKNOWN:{p}>',0,req[p],True))
        domains[p]=ds
    upper,feas,witness=z3_upper(req,domains,unknown)
    status='KNOWN_SUPPORT' if lower>0 else 'UNKNOWN_COMPLETION_ONLY' if upper=='sat' else 'CONTRADICTED' if upper=='unsat' else 'COMPUTATION_UNRESOLVED'
    cid=f"{w['window_id']}|{model}|{direction}"
    upper_domain_out={p:[{'word':word,'known_mask':km,'missing_mask':mm,'fresh_unknown':fresh} for word,km,mm,fresh in ds] for p,ds in domains.items()}
    marg={p:[{'word':word,'feasibility':'sat' if ok else 'unsat'} for word,ok in feas[p]] for p in plants}
    cases.append({'case_id':cid,'window_id':w['window_id'],'edition':w['edition'],'page':w['page'],'physical_leaf':w['physical_leaf'],'paragraph_ids':w['paragraph_ids'],'source_model':model,'direction':direction,'status':status,'required_masks':req,'known_support_domains':known_domains,'known_support_assignment_count':str(lower),'upper_domains':upper_domain_out,'upper_solver_result':upper,'upper_assignment_count':'NOT_COUNTED','upper_witness':witness if upper=='sat' else {},'upper_feasible_marginals':marg if upper=='sat' else {},'unsat_core':[] if upper!='unsat' else ['independent_unsat'], 'constraint_tags':[],'unknown_slots':unknown,'independent_confirmation_leaves':0})
    for p in plants:
        ds=domains[p]; feasible_forms=[word for word,ok in feas[p] if ok]
        pred_rows.append({'case_id':cid,'plant':p,'required_rows':','.join(str(i+1) for i in range(15) if req[p]&(1<<i)),'known_support_forms':' | '.join(known_domains[p]),'upper_domain_forms':' | '.join(x[0] for x in ds),'feasible_upper_forms':' | '.join(feasible_forms),'known_support_assignment_count':str(lower),'case_status':status})
    return cases[0],pred_rows


def main():
    lock=load(EXP/'PREREG_LOCK.json');checks={}
    for rel,h in lock.items():a=sha(ROOT/rel);checks[rel]={'expected':h,'actual':a,'ok':a==h}
    spec=load(EXP/'src/SPEC.json');src=load(EXP/'src/SOURCE.json');roster=load(EXP/'src/SOURCE_ROSTER.json')
    source_checks=[]
    for mod in MOD:
        inc=defaultdict(list);rows=[]
        for row in roster['rows']:
            terms=[]
            for raw_term in row['herbs_exact']:
                term=src['aliases_common'].get(raw_term,raw_term)
                if mod=='PLANT_IDENTITY':term=src['identity_only_aliases'].get(term,term)
                terms.append(term);inc[term].append(row['row'])
            rows.append({'row':row['row'],'star':row['star'],'plant_terms':terms})
        m=src['models'][mod]
        source_checks.append(rows==m['rows'] and dict(inc)==m['incidence'] and len(inc)==m['plant_identities'] and sum(map(len,inc.values()))==m['plant_row_mentions'])
    assert all(source_checks),'source alias/incidence discrepancy'
    raw=raw_groups(spec);windows=paragraph_windows(spec,raw);saved_w=load(gzip.open(ART/'ALL_WINDOWS.json.gz','rt',encoding='utf-8')); win_ok=windows==saved_w
    # Every fixed output window's masks and slot counts are recomputed here.
    masks_rows=[]
    for w in windows:
        for word,mask in w['word_masks'].items():masks_rows.append({'window_id':w['window_id'],'word':word,'observed_rows':','.join(str(i+1) for i in range(15) if mask&(1<<i)),'mask':str(mask)})
    mask_ok=masks_rows==list(csv.DictReader(open(ART/'ALL_WINDOW_WORD_MASKS.tsv'),delimiter='\t'))
    req_by={};models=src['models']
    for model in MOD:
      req_by[model]={p:None for p in models[model]['incidence']}
    cases=[];pred_rows=[]
    tasks=[(w,model,direction,models[model]['incidence']) for w in windows for model in MOD for direction in DIR]
    with ProcessPoolExecutor(max_workers=8) as pool:
        for case,rows in pool.map(calculate_case,tasks):
            cases.append(case);pred_rows.extend(rows)
            if len(cases)%8==0:print('independent cases',len(cases),flush=True)
    saved_cases=load(gzip.open(ART/'ALL_CASES.json.gz','rt',encoding='utf-8'));cases_ok=True
    cases_ok=len(saved_cases)==len(cases)==88
    witness_ok=True
    for got,want in zip(saved_cases,cases):
      for k in ('case_id','window_id','edition','page','physical_leaf','paragraph_ids','source_model','direction','status','required_masks','known_support_domains','known_support_assignment_count','upper_domains','upper_assignment_count','unknown_slots','independent_confirmation_leaves'):
       if got.get(k)!=want.get(k):cases_ok=False
      # Solver result and marginals are independently checked, but witnesses/cores may be noncanonical.
      if got.get('upper_solver_result')!=want['upper_solver_result']:cases_ok=False
      if want['upper_solver_result']=='sat':
       if got.get('upper_feasible_marginals')!=want['upper_feasible_marginals']:cases_ok=False
       if not got.get('upper_witness'):cases_ok=False
       witness=got['upper_witness']; selected=[]
       if set(witness)!=set(want['upper_domains']):witness_ok=False
       for plant,word in witness.items():
        domain=[d for d in want['upper_domains'].get(plant,[]) if d['word']==word]
        if len(domain)!=1:witness_ok=False
        else:selected.append(domain[0])
       witness_ok &= len(set(witness.values()))==len(witness)
       witness_ok &= all(sum(bool(d['missing_mask']&(1<<i)) for d in selected)<=cap for i,cap in enumerate(want['unknown_slots']))
    pred_ok=pred_rows==list(csv.DictReader(open(ART/'PLANT_PREDICTION_TABLE.tsv'),delimiter='\t'))
    compact=list(csv.DictReader(open(ART/'CANDIDATE_TABLE.tsv'),delimiter='\t'))
    compact_ok=len(compact)==len(cases)
    for row,c in zip(compact,cases):
        for key in ('case_id','edition','page','physical_leaf','source_model','direction','status','known_support_assignment_count','upper_solver_result','independent_confirmation_leaves'):
            compact_ok &= row[key]==str(c[key])
        compact_ok &= int(row['unknown_slots'])==sum(c['unknown_slots'])
        compact_ok &= int(row['plants_with_empty_upper_domain'])==sum(not d for d in c['upper_domains'].values())
    # Equivalent source incidence classes, preserving all singleton classes.
    eq={}
    for model in MOD:
      inc=models[model]['incidence']; bymask=defaultdict(list)
      for p,rows in inc.items():bymask[tuple(rows)].append(p)
      eq[model]=[{'rows':list(k),'indistinguishable_source_names':v} for k,v in sorted(bymask.items())]
    eq_ok=eq==load(ART/'SOURCE_EQUIVALENCE_CLASSES.json')
    result=load(ART/'RESULT.json');result_ok=result.get('case_count')==88 and result.get('confirmed_words')==0 and result.get('independent_confirmation_leaves_per_candidate')==0 and result.get('no_reserved_data_opened') is True
    result_ok &= result['outcomes']==dict(Counter(c['status'] for c in cases))
    result_ok &= result['outcomes_by_edition']=={ed:dict(Counter(c['status'] for c in cases if c['edition']==ed)) for ed in ED}
    result_ok &= result['physical_leaves']==sorted({w['physical_leaf'] for w in windows})
    lock_ok=all(x['ok'] for x in checks.values())
    all_ok=lock_ok and len(windows)==22 and win_ok and mask_ok and cases_ok and pred_ok and eq_ok and result_ok and compact_ok and witness_ok
    report={'experiment':'GDT960','validator':'independent_source_windows_and_constraint_reconstruction_without_run_import','status':'PASS' if all_ok else 'FAIL','lock':{'all_hashes_match':lock_ok,'checks':checks},'source_reextraction':{'raw_source_groups':len(raw),'windows':len(windows),'window_counts':{'ZL3b':sum(w['edition']=='ZL3b' for w in windows),'IT2a':sum(w['edition']=='IT2a' for w in windows),'RF1b':0},'all_windows_match':win_ok,'all_word_masks_match':mask_ok,'unknown_slots_policy_checked':True},'cases':{'count':len(cases),'all_88_fields_match':cases_ok,'all_upper_sat_marginals_checked_by_forced_orbit_representatives':cases_ok,'candidate_table_match':pred_ok},'source_incidence':{'models':{m:{'plant_identities':models[m]['plant_identities'],'plant_row_mentions':models[m]['plant_row_mentions']} for m in MOD},'equivalence_classes_match':eq_ok},'result_contract_match':result_ok,'claim_ceiling':{'meaning_validated':False,'confirmed_words':0,'independent_confirmation_leaves':0,'significance_assessed':False,'no_new_decoder':True}}
    report['cases']['prediction_table_match']=report['cases'].pop('candidate_table_match')
    report['cases']['candidate_table_match']=compact_ok
    report['cases']['all_saved_witnesses_satisfy_joint_constraints']=witness_ok
    report['source_incidence']['reextracted_from_raw_roster_with_frozen_aliases']=all(source_checks)
    report['implementation_note']='Separate Int/Distinct constraint implementation; root completed and corrected validator after initial schema failure and a marginal-query timeout. No claim of blinded scientific interpretation.'
    (ART/'VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':report['status'],'windows':22,'cases':88,'word_masks':len(masks_rows),'upper_marginals_checked_by_exact_orbits':cases_ok,'meaning_validated':False}))
    return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
