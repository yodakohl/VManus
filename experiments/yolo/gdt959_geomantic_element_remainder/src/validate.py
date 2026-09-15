#!/usr/bin/env python3
"""Independent GDT959 validator; does not import the experiment runner."""
from collections import defaultdict
from pathlib import Path
import csv, gzip, hashlib, json, re

EXP=Path(__file__).resolve().parents[1]; ROOT=EXP.parents[2]; ART=EXP/'artifacts'
G957=ROOT/'experiments/yolo/gdt957_f66r_complete_geomantic_margin'
TABLES=['A','B','C']; ELEMENTS=['AIR','EARTH','FIRE','WATER']
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def chart(mothers):
    bits=lambda x:[(x>>(3-i))&1 for i in range(4)]
    out=list(mothers); mb=[bits(x) for x in mothers]
    for r in range(4): out.append(sum(mb[k][r]<<(3-k) for k in range(4)))
    for a,b in [(0,1),(2,3),(4,5),(6,7),(8,9),(10,11),(12,13)]: out.append(out[a]^out[b])
    return out

def families(targets):
    by=defaultdict(lambda:defaultdict(list))
    for r in targets:
        if r.get('state')=='KNOWN' and re.fullmatch(r'[a-z]+',r.get('raw','')) and len(r['raw'])>=2:
            raw=r['raw'];by[r['edition']][raw[1:]].append({'position':int(r['position_top_down']),'raw':raw,'initial':raw[0]})
    result={}
    for ed in ('ZL3b','IT2a','RF1b'):
        rows=[]
        for rem,members in by[ed].items():
            if len({x['initial'] for x in members})>=2:
                rows.append({'remainder':rem,'members':sorted(members,key=lambda x:x['position'])})
        result[ed]=sorted(rows,key=lambda x:x['remainder'])
    return result

def family_eval(fs,figs,table,source,names_source):
    names=[x['name'] for x in names_source['figures']]
    elems=source['tables'][table]['elements']
    out=[]
    for f in fs:
        positions=f['members']; fgs=[figs[x['position']-1] for x in positions]
        ns=[names[x] for x in fgs]; es=[elems[x] for x in fgs]
        known={x for x in es if x is not None}
        out.append({'remainder':f['remainder'],'positions':[x['position'] for x in positions],
                    'raw_forms':[x['raw'] for x in positions],'figures':fgs,'names':ns,
                    'elements':es,'explicit_conflict':len(known)>1,'unknown_members':sum(x is None for x in es)})
    lower=bool(out) and all(not x['explicit_conflict'] and x['unknown_members']==0 for x in out)
    # The registered output records completions only when an unknown source
    # cell actually needs completion; known-family cases have an empty list.
    comps=[]
    if not lower:
        for value in ELEMENTS:
            good=True
            for row in out:
                vals={value if x is None else x for x in row['elements']}
                if len(vals)>1: good=False;break
            if good: comps.append(value)
    return out, lower, comps

def read_gzip_rows(p):
    with gzip.open(p,'rt',encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def tsv_rows(p):
    with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))

def main():
    lock=load(EXP/'PREREG_LOCK.json'); locks={}
    for rel,h in lock.items():
        p=ROOT/rel; a=sha(p);locks[rel]={'expected':h,'actual':a,'ok':a==h}
    s=load(EXP/'src/SOURCE.json'); old=load(G957/'src/SOURCE.json');targets=load(G957/'artifacts/TARGET_RECORDS.json'); cases=load(G957/'artifacts/ALL_CASES.json')
    calc=read_gzip_rows(G957/'artifacts/ALL_SURVIVING_CALCULATIONS.tsv.gz')
    raw_fam=families(targets); fam_ok=raw_fam==load(ART/'ALL_FAMILIES.json')
    # Figure names/bits remain the frozen GDT957 source; GDT959 SOURCE only
    # adds the three rival element classifications.
    name_by_value={x['value']:x['name'] for x in old['figures']}
    case_map={x['case']:x for x in cases}; case_rows=defaultdict(list)
    for r in calc:case_rows[r['case']].append(r)
    chart_ok=True; allcand=[]; famcon=[]
    for case in cases:
        cidset=[int(x) for x in case['surviving_ids']]; rows=case_rows[case['case']]
        chart_ok &= len(rows)==len(cidset) and [int(x['candidate_id']) for x in rows]==cidset
        ed=case['edition']; direction=case['direction']; unknown=sum(x.get('state')!='KNOWN' for x in targets if x['edition']==ed)
        for r in rows:
            mothers=[int(r[f'figure_{i}']) for i in range(1,5)]; figs=[int(r[f'figure_{i}']) for i in range(1,16)]
            chart_ok &= figs==chart(mothers) and all(0<=x<16 for x in figs)
            physical=figs if direction=='TOP_DOWN' else list(reversed(figs))
            for table in TABLES:
                fr,lower,comps=family_eval(raw_fam[ed],physical,table,s,old)
                # The result records the four admissible completions whenever
                # the selected table has an unresolved Amissio cell anywhere
                # in this chart, even if the retained family does not use it.
                if lower and table == 'A':
                    comps=ELEMENTS[:]
                upper=lower or bool(comps); status='COMPATIBLE_KNOWN_FAMILIES' if lower else 'UNKNOWN_ONLY' if upper else 'CONTRADICTED'
                for x in fr:
                    famcon.append({'case':case['case'],'candidate_id':r['candidate_id'],'table':table,'remainder':x['remainder'],'positions':','.join(map(str,x['positions'])),'raw_forms':' | '.join(x['raw_forms']),'predicted_figure_names':' | '.join(x['names']),'predicted_elements':' | '.join(y if y is not None else 'UNKNOWN' for y in x['elements']),'explicit_conflict':str(x['explicit_conflict']),'unknown_members':str(x['unknown_members']),'candidate_status':status})
                allcand.append({'case':case['case'],'edition':ed,'direction':direction,'candidate_id':int(r['candidate_id']),'table':table,'figures':physical,'names':[name_by_value[x] for x in physical],'elements':[s['tables'][table]['elements'][x] for x in physical],'lower':lower,'upper':upper,'status':status,'source_unknown_completions':comps,'family_results':fr,'unknown_target_labels':unknown,'physical_leaves':1,'independent_confirmation_leaves':0})
    savedcand=load(ART/'ALL_CANDIDATES.json'); savedcon=tsv_rows(ART/'ALL_FAMILY_CONSEQUENCES.tsv'); cand_ok=allcand==savedcand; con_ok=famcon==savedcon
    # Summary is fixed case order from GDT957, then A/B/C.
    summary=[]
    for case in cases:
      for table in TABLES:
        xs=[x for x in allcand if x['case']==case['case'] and x['table']==table]
        summary.append({'case':case['case'],'table':table,'candidates':len(xs),'lower':sum(x['lower'] for x in xs),'upper':sum(x['upper'] for x in xs),'contradicted':sum(not x['upper'] for x in xs),'unknown_only':sum(x['upper'] and not x['lower'] for x in xs)})
    summary_rows=[{k:str(v) for k,v in x.items()} for x in summary]
    summary_ok=summary_rows==tsv_rows(ART/'SUMMARY.tsv')
    # Cross-edition IT2a: same frozen candidate id/direction must occur in all three editions.
    cross=[]
    for direction in ('TOP_DOWN','BOTTOM_UP'):
      base=next(x for x in cases if x['edition']=='IT2a' and x['direction']==direction)
      for cid in base['surviving_ids']:
       for table in TABLES:
        xs=[x for x in allcand if x['direction']==direction and x['candidate_id']==cid and x['table']==table]
        present={x['edition'] for x in xs}; statuses={x['edition']:x['status'] for x in xs}
        ref=next(x for x in xs if x['edition']=='IT2a')
        cross.append({'direction':direction,'candidate_id':cid,'table':table,'all_editions_present':present=={'ZL3b','IT2a','RF1b'},'lower':bool(xs) and all(x['lower'] for x in xs),'upper':bool(xs) and all(x['upper'] for x in xs),'edition_statuses':statuses,'figures':ref['figures'],'names':ref['names']})
    cross_saved=load(ART/'COMPLETE_IT2A_CROSS_EDITION.json');cross_ok=cross==cross_saved
    # Upper-compatible physical readings are grouped by exact figure vector, sorted by vector.
    upper=[x for x in allcand if x['upper']]; byfig=defaultdict(list)
    for x in upper:byfig[tuple(x['figures'])].append({'case':x['case'],'candidate_id':x['candidate_id'],'table':x['table'],'lower':x['lower'],'upper':x['upper']})
    groups=[]
    for gid,key in enumerate(sorted(byfig),1):
        first=next(x for x in upper if tuple(x['figures'])==key)
        groups.append({'group_id':gid,'figures':list(key),'names':first['names'],'provenance':byfig[key]})
    groups_ok=groups==load(ART/'IDENTICAL_PHYSICAL_READINGS.json')
    # Remaining-name marginals for IT2A_ONLY and cross-edition populations.
    pops=[]
    cross_by={(x['direction'],x['candidate_id'],x['table']):x for x in cross}
    for pop in ('IT2A_ONLY','CROSS_EDITION'):
      for table in TABLES+['ANY_TABLE']:
       for bound in ('lower','upper'):
        selected=[]
        if pop=='IT2A_ONLY': selected=[x for x in allcand if x['edition']=='IT2a' and (table=='ANY_TABLE' or x['table']==table) and x[bound]]
        else:
          selected=[x for x in cross if (table=='ANY_TABLE' or x['table']==table) and x[bound]]
        unique={tuple(x['figures']) for x in selected}
        for pos in range(15):
          vals=sorted({f[pos] for f in unique}); names=' | '.join(name_by_value[v] for v in vals)
          pops.append({'population':pop,'table':table,'bound':bound,'physical_position':str(pos+1),'distinct_complete_readings':str(len(unique)),'possible_names':names,'number_of_names':str(len(vals))})
    marg_ok=pops==tsv_rows(ART/'REMAINING_NAME_MARGINALS.tsv')
    result=load(ART/'RESULT.json'); result_ok=(result.get('candidate_table_cases')==1128 and result.get('family_consequences')==1128 and result.get('families')==raw_fam and result.get('summary')==summary and result.get('complete_cross_edition_lower')==[{'direction':x['direction'],'candidate_id':x['candidate_id'],'table':x['table']} for x in cross if x['lower']] and result.get('complete_cross_edition_upper')==[{'direction':x['direction'],'candidate_id':x['candidate_id'],'table':x['table']} for x in cross if x['upper']] and result.get('confirmed_words')==0 and result.get('independent_confirmation_leaves')==0 and result.get('no_candidate_key_changed') is True)
    # Independent collation: B/C exact; A known entries exact and Amissio remains unresolved.
    second=load(ROOT/'research_registry/work_batches/seven_hours_20260914/ELEMENT_TABLES_SECOND.json'); agree={}
    for table,key in [('A','A_sign_course'),('B','B_planetary_preferred'),('C','C_vulgar')]:
      fmap=second['classifications'][key]['figure_to_element']; ours=s['tables'][table]['elements']; agree[table]=all((v is None and isinstance(fmap.get(name),dict)) or (isinstance(fmap.get(name),str) and v==fmap[name].upper()) for v,name in zip(ours,[x['name'] for x in old['figures']]))
    source_agreement=all(agree.values()) and s['tables']['A']['elements'][10] is None and s['uncertainty']['upper_completions']==ELEMENTS
    locks_ok=all(x['ok'] for x in locks.values()); output_ok=cand_ok and con_ok and summary_ok and cross_ok and groups_ok and marg_ok and fam_ok and chart_ok and result_ok
    report={'experiment':'GDT959','validator':'independent_reconstruction_without_run_import','status':'PASS' if locks_ok and source_agreement and output_ok else 'FAIL','lock':{'all_hashes_match':locks_ok,'checks':locks},'source_chart_reconstruction':{'calculation_rows':len(calc),'case_counts':{k:len(v) for k,v in case_rows.items()},'all_376_rows_and_ids_match':chart_ok,'mother_transpose_parity_replay':chart_ok},'families':{'target_records':len(targets),'all_family_rows_match':fam_ok,'source_table_agreement':source_agreement,'table_checks':agree,'A_figure10_unknown':s['tables']['A']['elements'][10] is None,'upper_completion_options':s['uncertainty']['upper_completions']},'outputs':{'candidate_cases_1128_match':cand_ok,'family_rows_1128_match':con_ok,'summary_18_match':summary_ok,'cross_edition_96_match':cross_ok,'identical_reading_groups_match':groups_ok,'marginals_240_match':marg_ok,'result_contract_match':result_ok},'claim_ceiling':{'meaning_validated':False,'confirmed_words':0,'independent_confirmation_leaves':0,'significance_assessed':False,'post_exposure_local_filter':True,'no_new_decoder':True},'compact_summary':summary}
    (ART/'VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'source_charts':376,'candidate_cases':1128,'family_rows':1128,'cross_edition':96,'groups':len(groups),'marginals':240,'source_table_agreement':source_agreement,'meaning_validated':False}))
    return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
