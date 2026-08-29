#!/usr/bin/env python3
"""Independent guarded validator and byte replay for GDT639."""
from __future__ import annotations
import csv,hashlib,io,json,re,subprocess,sys
from collections import Counter,defaultdict
from pathlib import Path
sys.dont_write_bytecode=True
def rootof(p):
    for x in (p,*p.parents):
        if (x/'AGENTS.md').is_file() and (x/'.git').exists(): return x
    raise RuntimeError('repository root not found')
ROOT=rootof(Path(__file__).resolve()); REL=Path('experiments/yolo/gdt639_strict_hole_component_repair'); BASE=ROOT/REL; ART=BASE/'artifacts'; RUN=BASE/'src/run.py'; RESULT=ART/'RESULT.json'; VALIDATION=ART/'VALIDATION.json'; MANIFEST=BASE/'experiment.json'
G638=ROOT/'experiments/yolo/gdt638_sequential_compound_promotion/artifacts'; V15=G638/'WORKING_DICTIONARY_V15.tsv'; OLDG=G638/'V15_EXACT_TOKEN_GLOSSARY.tsv'; OLDC=G638/'ALL_LINE_CONCRETE_COVERAGE_V15.tsv'; OLDCOMP=G638/'COMPLETE_PASSAGES_V15.tsv'; ALLOW=G638/'PAGE_ALLOWLIST.tsv'; TOK=Path('transcription/voynich_zl3b_tokens.tsv')
NAMES=('PAGE_ALLOWLIST.tsv','STRICT_CANDIDATE_CENSUS.tsv','COMPONENT_BINDING_AUDIT.tsv','PROMOTION_CANDIDATE_DECK.tsv','ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv','SEQUENTIAL_PROMOTION_LEDGER.tsv','ROUND_COVERAGE_COUNTS.tsv','ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv','HELD_STRICT_DEFAULTS.tsv','NEWLY_COMPLETED_LINES.tsv','V16_EXACT_TOKEN_GLOSSARY.tsv','ALL_LINE_CONCRETE_COVERAGE_V16.tsv','COMPLETE_PASSAGES_V16.tsv','ONE_UNKNOWN_PASSAGES_V16.tsv','WORKING_DICTIONARY_V16.tsv'); GENERATED=tuple(ART/n for n in NAMES)+(RESULT,)
ORDER=('qotchor','dchol','chotaiin','cthar','chear','odaiim','okeey','shy'); OCC=(11,21,8,14,44,1,138,95)
STRICT=('keechy','chokshy','shy','yty','chotaiin','cthar','cpholdy','cheockhy','chckhal','chear','dchol','ytoryd','qol','ckhy','yto','odaiim','qotchor','sodal','okeey','orol','olcthr','olekor','ches','ytaiin')
BARE={'ar','aiim','y'}; WRAPPERS={'q','qo','o','s','sh','ch','k','t','cth'}
STATES={'KNOWN_EXACT_WHOLE','KNOWN_CONTEXT_LICENSED','AMBIGUOUS_ACTIVE_RIVAL','UNKNOWN_SURFACE','READER_BOUNDARY_UNSTABLE'}
FILL=re.compile(r'arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|arbeitsobjekt|werkzeug|produkt weiter|f(?:ü|ue)hre .* aus|leite .* weiter|\b(?:arbeite|prozessiere|verarbeite)\b',re.I)
def tsv(p):
    with Path(p).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canon(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def pipes(v):return v.split(' | ') if v else []
def query(pages):
    cmd=[str(ROOT/'vmanus-exp'),'query-tsv',str(TOK),'--selector','page']
    for p in pages:cmd+=['--allow',p]
    cmd+=['--columns','page,locus,token_index,eva,section,language,hand','--forbid-prefix','f84','--forbid-prefix','f84r']; x=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
    if x.returncode:raise RuntimeError(x.stderr)
    st=[z for z in x.stderr.splitlines() if z.startswith('GUARD_STATS ')]; assert len(st)==1
    rows=list(csv.DictReader(io.StringIO(x.stdout),delimiter='\t')); assert not any(r['page']=='f1r' or r['page'].startswith('f84') for r in rows)
    return rows,{k:int(v) for k,v in json.loads(st[0][12:]).items()}
def main():
    C=[]
    def ck(v,n):
        if not v:raise AssertionError(n)
        C.append(n)
    ck(VALIDATION not in GENERATED,'validation excluded');ck(len(GENERATED)==16 and len(set(GENERATED))==16,'16 unique builder outputs');ck(all(p.is_file() for p in GENERATED),'outputs exist');before={p:p.read_bytes() for p in GENERATED};x=subprocess.run([sys.executable,str(RUN)],cwd=ROOT,text=True,capture_output=True)
    ck(x.returncode==0,'builder zero');ck(x.stdout.strip()=='GDT639 built: candidates=8 accepted=8 audits=332 complete=39 strict=28 one_unknown=62','summary exact')
    for p in GENERATED:ck(p.read_bytes()==before[p],f'byte replay {p.name}')
    R=json.loads(RESULT.read_text());ck(R['schema']=='GDT639_STRICT_HOLE_COMPONENT_REPAIR_RESULT_V1','schema');ck(R['experiment_id']=='GDT639','id');ck(R['status']=='PASS_8_EXACT_COMPONENT_REPAIRS__9_NEW_COMPLETE_LINES__16_HELD_DEFAULTS','status');core={k:v for k,v in R.items() if k!='content_sha256'};ck(R['content_sha256']==canon(core),'result content hash');g=R['guard'];ck(g['allowed_pages']==179 and g['new_pages']==g['new_images']==0,'scope');ck(g['f1r']=='EXCLUDED' and g['f84']==g['f84r']=='FORBIDDEN','protected guards')
    src=RUN.read_text();ck(src.count('guarded_query(')==2,'two guarded queries');ck('read_tsv(ROOT / TOKENS_REL)' not in src and 'read_tsv(ROOT / CROSS_REL)' not in src,'no raw mixed parse')
    for p,d in R['inputs'].items():ck((ROOT/p).is_file(),f'input exists {p}');ck(sha(ROOT/p)==d,f'input hash {p}')
    ck(set(R['outputs'])=={str(REL/'artifacts'/n) for n in NAMES},'result output set')
    for p,d in R['outputs'].items():ck((ROOT/p).is_file(),f'output exists {p}');ck(sha(ROOT/p)==d,f'output hash {p}')
    M=json.loads(MANIFEST.read_text());ck(M['experiment_id']=='GDT639','manifest id');ck(M['sealed_data']['f84']==M['sealed_data']['f84r']=='FORBIDDEN','manifest seals')
    for group in ('inputs','outputs'):
        for z in M.get(group,[]):p=ROOT/z['path'];ck(p.is_file(),f'manifest exists {z["path"]}');ck(sha(p)==z['sha256'],f'manifest hash {z["path"]}')
    pages=[r['page'] for r in tsv(ART/'PAGE_ALLOWLIST.tsv')];ck(len(pages)==len(set(pages))==179 and pages==sorted(pages),'179 pages');ck((ART/'PAGE_ALLOWLIST.tsv').read_bytes()==ALLOW.read_bytes(),'allow inherited');ck('f1r' not in pages and all(not p.startswith('f84') for p in pages),'no protected pages')
    census=tsv(ART/'STRICT_CANDIDATE_CENSUS.tsv');ck(len(census)==24 and tuple(r['surface'] for r in census)==STRICT,'24 strict surfaces exact');ck(len({r['surface'] for r in census})==24,'strict unique');ck(all(r['default_meaning_de'].strip() and not FILL.search(r['default_meaning_de']) for r in census),'every strict default concrete');ck(sum(r['promotion_state']=='TRIAL' for r in census)==8 and sum(r['promotion_state']=='HELD_FOR_NEXT_ROUTE' for r in census)==16,'8 trial 16 held census')
    deck=tsv(ART/'PROMOTION_CANDIDATE_DECK.tsv');ck(tuple(r['surface'] for r in deck)==ORDER,'candidate order');ck([int(r['candidate_order']) for r in deck]==list(range(1,9)),'candidate rounds');ck(tuple(int(r['occurrences']) for r in deck)==OCC,'candidate occurrences');ck(all(r['decision']=='ACCEPT' and r['working_meaning_de'].strip() and not FILL.search(r['working_meaning_de']) for r in deck),'8 concrete accepts')
    rows,stats=query(pages);ck(stats==g['token_query'],'guard stats');ck(len(rows)==32339,'32339 tokens');lines=defaultdict(list)
    for r in rows:lines[r['locus']].append(r)
    source=Counter()
    for loc,ms in lines.items():
        ms.sort(key=lambda r:int(r['token_index']))
        for i,r in enumerate(ms,1):
            if r['eva'] in ORDER:source[(r['eva'],r['page'],loc,i)]+=1
    ck(sum(source.values())==332,'332 source occurrences');ck(tuple(sum(n for k,n in source.items() if k[0]==s) for s in ORDER)==OCC,'source occurrence vector')
    audits=tsv(ART/'ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv');ck(len(audits)==len({r['audit_id'] for r in audits})==332,'332 unique audits');a=Counter((r['surface'],r['page'],r['locus'],int(r['token_ordinal'])) for r in audits);ck(a==source,'audit multiset exact');ro={s:i+1 for i,s in enumerate(ORDER)}
    for r in audits:
        s,loc,i=r['surface'],r['locus'],int(r['token_ordinal']);ms=lines[loc];ck(int(r['round'])==ro[s] and ms[i-1]['eva']==s,f'audit align {r["audit_id"]}');pos='FIRST' if i==1 else 'LAST' if i==len(ms) else 'MIDDLE';ck(r['line_position']==pos,f'audit pos {r["audit_id"]}');ck(r['before_state']=='UNKNOWN_SURFACE' and r['before_gloss']==f'[{s}:?]',f'audit before {r["audit_id"]}');ck(r['after_gloss']==deck[ro[s]-1]['working_meaning_de'],f'audit after {r["audit_id"]}');ck(r['verdict'] in {'CONSISTENT_CONCRETE','OPAQUE_CONTEXT','READER_BOUNDARY_WARNING'} and r['review_reason'].strip(),f'audit verdict {r["audit_id"]}');ck(not FILL.search(r['local_after_de']),f'audit filler {r["audit_id"]}')
    vc=Counter(r['verdict'] for r in audits);ck(vc==Counter({'CONSISTENT_CONCRETE':59,'OPAQUE_CONTEXT':214,'READER_BOUNDARY_WARNING':59}),'verdict totals')
    comp=tsv(ART/'COMPONENT_BINDING_AUDIT.tsv');ck(len(comp)==16 and all(sum(r['surface']==s for r in comp)==2 for s in ORDER),'two component rows each')
    for r in comp:ck((ROOT/r['evidence_path']).is_file(),f'component evidence exists {r["component_id"]}');ck(r['segment'].strip() and r['working_value_de'].strip() and r['evidence_kind'].strip() and r['licensed_use'].strip(),f'component row full {r["component_id"]}')
    ck(any(r['surface']=='cthar' and 'no bare-ar' in r['licensed_use'] for r in comp) and any(r['surface']=='chear' and 'no bare-ar' in r['licensed_use'] for r in comp),'ar scope evidence');ck(any(r['surface']=='odaiim' and 'no bare-aiim' in r['licensed_use'] for r in comp),'aiim scope evidence');ck(any(r['surface']=='shy' and 'no bare-y' in r['licensed_use'] for r in comp),'y scope evidence')
    ledger=tsv(ART/'SEQUENTIAL_PROMOTION_LEDGER.tsv');rounds=tsv(ART/'ROUND_COVERAGE_COUNTS.tsv');ck(len(ledger)==8 and len(rounds)==9,'round rows');ck([int(r['round']) for r in ledger]==list(range(1,9)) and [int(r['round']) for r in rounds]==list(range(9)),'round sequence');base=tsv(V15);ck(len(base)==272 and rounds[0]['dictionary_sha256']==canon(base),'V15 base hash');defs=tsv(ART/'ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv');ck(tuple(r['surface'] for r in defs)==ORDER,'accepted defaults order');bd={r['surface']:r for r in defs};tail=[];ph=rounds[0]['dictionary_sha256'];entries=272;pk,pu,pc=9259,23080,30
    for i,r in enumerate(ledger,1):
        s=ORDER[i-1];rr=rounds[i];ck(r['surface']==rr['surface']==s and r['decision']=='ACCEPT','ledger surface/decision');ck(r['pre_dictionary_sha256']==ph and int(r['pre_dictionary_entries'])==entries,f'pre chain {i}');ck(int(r['occurrences'])==int(r['audited_occurrences'])==OCC[i-1],f'audited all {i}');v=Counter(x['verdict'] for x in audits if int(x['round'])==i)
        for fld,key in (('consistent_concrete','CONSISTENT_CONCRETE'),('opaque_context','OPAQUE_CONTEXT'),('reader_boundary_warning','READER_BOUNDARY_WARNING')):ck(int(r[fld])==v[key],f'{fld} {i}')
        ck(int(r['hard_contradiction'])==int(r['nonsense'])==0 and int(r['reader_exact_occurrences'])>0 and int(r['marginal_complete'])>=1,f'accept gate {i}');tail.append({k:bd[s][k] for k in ('entry','kind','working_meaning_de','composition','context_rule','status')});entries+=1;eh=canon([*base,*tail]);ck(int(r['post_dictionary_entries'])==entries and r['post_dictionary_sha256']==rr['dictionary_sha256']==eh,f'post chain {i}');nk,nu,nc=int(rr['known_token_positions']),int(rr['unknown_token_positions']),int(rr['complete_multi_token_lines']);ck(nk>=pk and nu<=pu and nc>=pc and nk+nu==32339,f'monotone {i}');ph,pk,pu,pc=eh,nk,nu,nc
    held=tsv(ART/'HELD_STRICT_DEFAULTS.tsv');ck(len(held)==16 and set(r['surface'] for r in held)==set(STRICT)-set(ORDER),'16 held exact');ck(all(r['decision']=='HOLD' and r['barrier']!='NONE' and r['default_meaning_de'].strip() and not FILL.search(r['default_meaning_de']) for r in held),'held defaults and barriers')
    D=tsv(ART/'WORKING_DICTIONARY_V16.tsv');ck(len(D)==280 and D[:272]==base and D[272:]==tail,'V15 exact prefix plus 8');ck(canon(D)==ph,'V16 hash');ts={r['entry'].split('@')[0] for r in tail};ck(ts==set(ORDER) and not(ts&(BARE|WRAPPERS)),'no bare/global wrapper rows')
    for r in tail:ck(r['kind']=='EXACT_WHOLE_SURFACE_COMPONENT_REPAIR' and 'exact complete surface only' in r['context_rule'] and 'no substring, bare-body, wrapper or absent-cell transfer' in r['context_rule'],f'exact scope {r["entry"]}');ck(not FILL.search(r['working_meaning_de']),f'dictionary filler {r["entry"]}')
    oldg={r['surface']:r for r in tsv(OLDG)}; glrows=tsv(ART/'V16_EXACT_TOKEN_GLOSSARY.tsv');gl={r['surface']:r for r in glrows};ck(len(oldg)==225 and len(gl)==233 and all(gl[s]==r for s,r in oldg.items()),'225 glossary prefix map');ck(set(gl)-set(oldg)==set(ORDER),'8 glossary additions');ck(not({'ar','aiim','y'}&set(gl)),'no bare glossary bodies')
    old=tsv(OLDC);new=tsv(ART/'ALL_LINE_CONCRETE_COVERAGE_V16.tsv');ck(len(new)==len({r['locus'] for r in new})==4128,'4128 coverage');ob={r['locus']:r for r in old};nb={r['locus']:r for r in new};ck(set(ob)==set(nb),'same loci');changed=0
    for r in new:
        b=ob[r['locus']];n=int(r['token_count']);known,unk=int(r['known_tokens']),int(r['unknown_tokens']);tok=r['zl3b_line'].split();gg,ss,srcs=pipes(r['token_glosses_de']),pipes(r['scope_states']),pipes(r['gloss_sources']);bg,bs,bsrc=pipes(b['token_glosses_de']),pipes(b['scope_states']),pipes(b['gloss_sources']);ck(r['page'] in pages and known+unk==n and len(tok)==len(gg)==len(ss)==len(srcs)==n,f'coverage vectors {r["locus"]}');ck(set(ss)<=STATES and ss.count('UNKNOWN_SURFACE')==unk,f'coverage states {r["locus"]}');ck(not FILL.search(r['token_glosses_de']),f'coverage filler {r["locus"]}')
        for j,s in enumerate(tok):
            if s in ORDER:ck(bs[j]=='UNKNOWN_SURFACE' and ss[j] in {'KNOWN_EXACT_WHOLE','READER_BOUNDARY_UNSTABLE'} and srcs[j].startswith('GDT639:ROUND_'),f'changed {r["locus"]}:{j+1}');changed+=1
            else:ck((gg[j],ss[j],srcs[j])==(bg[j],bs[j],bsrc[j]),f'preserved {r["locus"]}:{j+1}')
    ck(changed==332,'332 positions changed')
    complete=tsv(ART/'COMPLETE_PASSAGES_V16.tsv');one=tsv(ART/'ONE_UNKNOWN_PASSAGES_V16.tsv');ck(len(complete)==39 and sum(int(r['strict_complete']) for r in complete)==28,'39 complete 28 strict');ck(len(one)==62 and sum(int(r['strict_eligible']) for r in one)==20,'62 onehole 20 strict');ck([int(r['rank']) for r in complete]==list(range(1,40)) and [int(r['rank']) for r in one]==list(range(1,63)),'ranks')
    for r in complete:ck(int(r['unknown_tokens'])==0 and int(r['known_tokens'])==int(r['token_count']) and not re.search(r'\[[a-z]+:\?\]',r['working_translation_de']) and not FILL.search(r['working_translation_de']),f'complete concrete {r["locus"]}')
    for r in one:ck(int(r['unknown_tokens'])==1,f'one hole {r["locus"]}')
    oldset={r['locus'] for r in tsv(OLDCOMP)}; newset={r['locus'] for r in complete}-oldset; nl=tsv(ART/'NEWLY_COMPLETED_LINES.tsv');ck(len(newset)==len(nl)==9 and {r['locus'] for r in nl}==newset,'9 new lines');ck(all(r['surface'] in ORDER and not FILL.search(r['smoothed_working_reading_de']) for r in nl),'new line provenance')
    cr=R['candidate_run'];ck((cr['candidates'],cr['accepted'],cr['audited_occurrences'])==(8,8,332) and tuple(cr['accepted_surfaces'])==ORDER,'result candidates')
    ck(cr['verdicts']=={'CONSISTENT_CONCRETE':59,'OPAQUE_CONTEXT':214,'READER_BOUNDARY_WARNING':59},'result verdicts')
    m=R['coverage'];ck((m['physical_lines'],m['complete_multi_token_lines'],m['strict_complete_lines'],m['one_unknown_lines'],m['strict_one_unknown_lines'],m['exact_glossary_surfaces'],m['newly_completed_lines'])==(4128,39,28,62,20,233,9),'result coverage');ck((m['known_token_positions'],m['unknown_token_positions'])==(9591,22748),'result tokens');sc=R['strict_census'];ck(sc=={'every_surface_has_default':True,'held_defaults':16,'strict_surfaces':24,'trial_surfaces':8},'result strict census');w=R['working_dictionary'];ck((w['v15_entries'],w['v16_entries'],w['accepted_tail_entries'])==(272,280,8) and w['v15_prefix_sha256']==canon(base) and w['v16_sha256']==canon(D),'result dictionaries')
    vcore={'schema':'GDT639_VALIDATION_V1','experiment_id':'GDT639','status':'PASS','checks':len(C),'builder_outputs_replayed':len(GENERATED),'strict_surfaces':24,'trial_surfaces':8,'held_defaults':16,'audited_occurrences':332,'physical_lines':4128,'complete_multi_token_lines':39,'strict_complete_lines':28,'one_unknown_lines':62,'newly_completed_lines':9,'dictionary_entries':280,'validated_claim':'All twenty-four strict V15 hole surfaces retain concrete defaults. Eight exact whole-surface component repairs pass a guarded 332-occurrence sequential audit, preserve V15 as an exact prefix, and add nine complete lines; sixteen defaults remain held outside V16.'};V={**vcore,'content_sha256':canon(vcore)};VALIDATION.write_text(json.dumps(V,ensure_ascii=False,indent=2,sort_keys=True)+'\n');print(f'GDT639 validation PASS: {len(C)} checks, {len(GENERATED)} outputs replayed');return 0
if __name__=='__main__':raise SystemExit(main())
