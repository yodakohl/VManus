"""Concrete, source-reviewed semantic propositions; source intake is a separate view."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from tools import research_registry as registry
ROOT=Path(__file__).resolve().parents[1]
DIRECTORY='research_registry'
DATA=DIRECTORY+'/semantic_ideas.jsonl'
MANIFEST=DIRECTORY+'/SEMANTIC_IDEAS_MANIFEST.json'
CORRECTIONS=DIRECTORY+'/semantic_claim_corrections.jsonl'
ARCHIVE=DIRECTORY+'/semantic_ideas_excluded.jsonl'
IDENTITIES=DIRECTORY+'/semantic_identity_decisions.jsonl'
FAILURES=DIRECTORY+'/semantic_failure_decisions.jsonl'
REVIEWS=[DIRECTORY+'/decisions/'+name for name in ['clean_proposal_review.json','clean_component_review.json','clean_ip_review.json','clean_historical_review.json']]
EXTRA_REVIEWS=[DIRECTORY+'/decisions/'+name for name in ['clean_prereg_candidate_review.json','clean_report_proposals_review.json','clean_middle_sidequest_review.json','clean_late_sidequest_review.json','clean_root_early_review.json','clean_final_sidequest_review.json','clean_gap_review_l.json','clean_gap_review_o.json','clean_gap_review_q.json','clean_gap_review_t.json','clean_gap_review_u.json','clean_gap_review_w.json','clean_gap_review_aa.json','clean_gap_review_ab.json','clean_gap_review_ac.json','clean_gap_review_ae.json','clean_gap_review_ai.json','clean_gap_review_af.json','clean_gap_review_ag.json','clean_gap_review_al.json','clean_gap_review_aq_integrated.json','clean_gap_review_am_integrated.json','clean_gap_review_an_integrated.json','clean_gap_review_ao_integrated.json','clean_gap_review_aw_integrated.json','clean_gap_review_ax_integrated.json','clean_gap_review_ay_integrated.json','clean_gap_review_az_integrated.json','clean_gap_review_ba.json']]
SEMANTIC_TYPES={'lexical_hypothesis','semantic_model','functional_hypothesis'}
TYPES=SEMANTIC_TYPES|{'formal_role'}
PLACEHOLDER=re.compile(r'^(?:unknown|unresolved|not[_ ]assessed|needs?[_ ]review|source[_ ]requires[_ ]review|review[_ ]priority|todo|tbd|placeholder|noch zu|unbekannt|zu prüfen)(?:\b|$)',re.I)
TECHNICAL_ASSIGNMENT=re.compile(r'^(?:kind|status|verdict|decision|transferable|commodity|seed|random_state|n_jobs|output|source_path|file|sha256|p_value|n|score|accuracy)\s*(?:→|=|:)',re.I)

def canonical_claim(text):
    # Typography/whitespace only. Do not erase negation, alternative senses or word case.
    return ' '.join(text.replace('`','').split())

def card_basis(card):
    fields={k:card[k] for k in ('claim','claim_type','member_ids','evidence','cases')}
    fields.update(card.get('source_original_assertion',{}))
    return hashlib.sha256(registry.canonical(fields).encode()).hexdigest()

def apply_corrections(rows,root,inputs,source_hashes,relative=CORRECTIONS):
    path=root/relative
    if not path.exists():return rows,[]
    inputs[relative]=registry.digest(path)
    by_id={r['id']:r for r in rows};histories={};seen=set()
    for review in registry.read_jsonl(path):
        target=review['target'];identifier=review['id']
        if target not in by_id or identifier in seen:raise ValueError('invalid correction identity')
        seen.add(identifier);history=histories.setdefault(target,[])
        expected=history[-1]['id'] if history else None
        if review.get('previous_revision')!=expected:raise ValueError('broken correction revision chain')
        if review.get('action') not in ('archive_source_error','retain_as_hypothesis','restate_scope'):raise ValueError('invalid correction action')
        if not review.get('reason','').strip():raise ValueError('correction needs source reasoning')
        if any(not e.get('sha256') for e in review.get('evidence',[])):raise ValueError('correction evidence needs original hash')
        validate_card(dict(by_id[target],evidence=review.get('evidence',[])),root)
        for e in review['evidence']:source_hashes[e['path']]=registry.digest(registry.evidence_path(root,e['path']))
        history.append(review)
    active=[];archive=[]
    for r in rows:
        history=histories.get(r['id'],[])
        if history:
            if history[-1]['target_basis_sha256']!=card_basis(r):raise ValueError('changed corrected claim; explicit review required')
            r['source_correction_history']=history
            if history[-1]['action']=='restate_scope':
                replacement=history[-1].get('replacement',{})
                if set(replacement)!={'claim','claim_type'}:raise ValueError('scope restatement requires exactly claim and claim_type')
                r['source_original_assertion']={k:r[k] for k in ('claim','claim_type')}
                r.update(replacement);validate_card(r,root)
        if history and history[-1]['action']=='archive_source_error':
            r['original_status']=r['status'];r['status']='source_extraction_withdrawn';archive.append(r)
        else:active.append(r)
    return active,archive

def validate_card(card,root=ROOT,source_ids=None):
    if card.get('claim_type') not in TYPES:raise ValueError('non-idea kind in clean cards')
    claim=card.get('claim','').strip()
    if len(claim)<6 or PLACEHOLDER.search(claim) or TECHNICAL_ASSIGNMENT.search(claim):
        raise ValueError('placeholder or technical assignment in clean card: '+card.get('id',''))
    if card.get('ready',False) is not False:raise ValueError('curation is not execution approval')
    ids=card.get('member_ids',[])
    if not ids or len(ids)!=len(set(ids)):raise ValueError('missing or repeated source ID')
    if source_ids is not None and not set(ids)<=source_ids:raise ValueError('unknown source ID')
    evidence=card.get('evidence',[])
    if not evidence:raise ValueError('claim needs exact evidence')
    for e in evidence:
        p=registry.evidence_path(root,e['path'])
        if not p.is_file():raise ValueError('missing evidence source')
        if not isinstance(e.get('line'),int) or e['line']<1:raise ValueError('missing evidence line')
        quote=e.get('quote','')
        if not quote.strip():raise ValueError('missing evidence quote')
        lines=p.read_text(encoding='utf-8-sig').splitlines()
        start=e['line']-1
        if lines[start:start+len(quote.splitlines())]!=quote.splitlines():
            raise ValueError('source quote mismatch: '+e['path']+':'+str(e['line']))
        if e.get('sha256') and registry.digest(p)!=e['sha256']:raise ValueError('stale evidence')
    return True

def build(root=ROOT):
    # Ingestion records remain immutable sources; none become an idea by mere membership.
    inventory=registry.read_jsonl(root/DIRECTORY/'semantic_inventory.jsonl')
    sources={r['id'] for r in inventory}
    proposal_sources={r['id'] for r in inventory if r['id'].startswith('LEGACY_PROPOSAL:')}
    grouped={};inputs={DIRECTORY+'/semantic_inventory.jsonl':registry.digest(root/DIRECTORY/'semantic_inventory.jsonl')};disposition_counts={};sources_hashes={};review_card_count=0
    reviews={relative:json.loads((root/relative).read_text()) for relative in REVIEWS+EXTRA_REVIEWS if (root/relative).exists()}
    if not set(REVIEWS)<=reviews.keys():raise ValueError('missing completed review')
    links={};reviewed_sources=set()
    for review in reviews.values():
        for d in review.get('dispositions',[]):
            if d.get('decision') not in ('pending_source_review','pending_review'):
                reviewed_sources.add(d['source_id'])
            for target in d.get('card_ids',[]):links.setdefault(target,set()).add(d['source_id'])
    card_ids={c['id'] for review in reviews.values() for c in review['cards']}
    if not set(links)<=card_ids:raise ValueError('disposition refers to unknown reviewed card')
    for relative,review in reviews.items():
        path=root/relative
        if not path.exists():raise ValueError('missing completed review: '+relative)
        inputs[relative]=registry.digest(path)
        decisions=review.get('dispositions',[])
        disposition_counts[relative]=dict(Counter(x.get('decision','unspecified') for x in decisions))
        for original in review['cards']:
            card=dict(original)
            card['member_ids']=sorted(set(card['member_ids'])|links.get(card['id'],set()))
            validate_card(card,root,sources)
            card['ready']=False
            context_ids=set()
            for e in card['evidence']:
                for n in re.findall(r'gdt(\d+)',e['path'],re.I):
                    candidate='GDT'+n.zfill(3)
                    if candidate in sources:context_ids.add(candidate)
            card['registry_context_ids']=sorted(context_ids)
            review_card_count+=1
            key=(card['claim_type'],canonical_claim(card['claim']))
            # One displayed assertion, with distinct source-scope cases underneath.
            # This is not a merger of experiments, histories or possibly different domains.
            if key not in grouped:
                identifier='SEM:'+hashlib.sha256(registry.canonical(key).encode()).hexdigest()[:20]
                grouped[key]={'id':identifier,'claim':card['claim'],'claim_type':card['claim_type'],
                    'status':'unconfirmed','ready':False,'member_ids':[],'evidence':[],'cases':[],
                    'review_ids':[],'registry_context_ids':[],'deduplication':'Identical normalized assertion only; source scopes and alternatives remain separate cases.'}
            item=grouped[key]
            item['review_ids'].append(card['id'])
            item['member_ids']=sorted(set(item['member_ids'])|set(card['member_ids']))
            item['registry_context_ids']=sorted(set(item['registry_context_ids'])|context_ids)
            for e in card['evidence']:
                bound=dict(e,sha256=registry.digest(registry.evidence_path(root,e['path'])))
                if bound not in item['evidence']:item['evidence'].append(bound)
                sources_hashes[e['path']]=bound['sha256']
            case={k:v for k,v in card.items() if k not in ('claim','evidence','ready')}
            case['review_file']=relative
            item['cases'].append(case)
    rows=sorted(grouped.values(),key=lambda r:r['id'])
    for r in rows:validate_card(r,root,sources)
    assertion_count=len(rows)
    rows,archive=apply_corrections(rows,root,inputs,sources_hashes)
    registry.write_jsonl(root/DATA,rows)
    registry.write_jsonl(root/ARCHIVE,archive)
    manifest={'schema_version':1,'status':'SOURCE_REVIEWED_CONCRETE_CLAIMS','cards':len(rows),
        'builder_sha256':registry.digest(Path(__file__)),
        'semantic_cards':sum(r['claim_type'] in SEMANTIC_TYPES for r in rows),
        'formal_role_cards':sum(r['claim_type']=='formal_role' for r in rows),
        'review_cards_before_exact_assertion_grouping':review_card_count,
        'exact_assertion_repetitions_grouped':review_card_count-assertion_count,
        'archived_source_errors':len(archive),'archived_source_cases':sum(len(r['cases']) for r in archive),
        'archive_sha256':registry.digest(root/ARCHIVE),
        'claim_types':dict(Counter(r['claim_type'] for r in rows)),
        'review_dispositions':disposition_counts,'reviewed_source_fragments':len(reviewed_sources),'input_sha256':inputs,
        'proposal_source_coverage':{'total':len(proposal_sources),'reviewed':len(proposal_sources & reviewed_sources),
            'remaining':len(proposal_sources-reviewed_sources)},
        'source_sha256':sources_hashes,'data_sha256':registry.digest(root/DATA),
        'limits':['Source claim review, not confirmation of meanings.',
            'Default queue excludes formal-role claims, source pointers, unresolved intake and methods/results.',
            'Identical assertion wording is grouped for display; domain and experimental cases remain distinct.',
            'No general semantic equivalence or permission to repeat failed experiments follows from this grouping.']}
    (root/MANIFEST).write_text(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    return {k:manifest[k] for k in ('status','cards','semantic_cards','formal_role_cards','exact_assertion_repetitions_grouped')}

def validate(root=ROOT):
    m=json.loads((root/MANIFEST).read_text())
    if registry.digest(Path(__file__))!=m['builder_sha256']:raise ValueError('changed clean idea builder; rebuild required')
    if registry.digest(root/DATA)!=m['data_sha256']:raise ValueError('changed clean idea snapshot')
    if registry.digest(root/ARCHIVE)!=m['archive_sha256']:raise ValueError('changed source correction archive')
    if (root/CORRECTIONS).exists() and CORRECTIONS not in m['input_sha256']:raise ValueError('new corrections; rebuild required')
    for path,sha in {**m['input_sha256'],**m['source_sha256']}.items():
        p=registry.evidence_path(root,path)
        if not p.is_file() or registry.digest(p)!=sha:raise ValueError('stale clean idea input: '+path)
    return m

def identity_view(root,rows):
    from tools import semantic_identity as identity
    decisions=identity.read_decisions(root/IDENTITIES)
    index=identity.build_index(rows,decisions,root,archived_ids=[r['id'] for r in registry.read_jsonl(root/ARCHIVE)])
    by_id={r['id']:r for r in rows};groups=[]
    for offset in range(0,index.counts['groups'],100):
        for header in index.page_groups(offset,100):
            members=[]
            for start in range(0,header['member_count'],100):members.extend(index.get_group(header['id'],start,100)['member_ids'])
            types={by_id[m]['claim_type'] for m in members}
            if len(types)!=1:raise ValueError('identity group crosses claim types')
            groups.append((header['id'],members))
    return groups,decisions

def connect(root=ROOT):
    m=validate(root);folder=root/DIRECTORY/'runtime';folder.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(folder/'semantic_ideas.sqlite3')
    local=local_cards(root)
    from tools import semantic_identity as identity
    decisions=identity.read_decisions(root/IDENTITIES)
    # Source checks apply even when the card index can be reused.
    for decision in identity._latest(decisions).values():identity._evidence(root,decision.get('evidence'))
    key=m['data_sha256']+registry.digest(Path(__file__))
    from tools import semantic_identity as identity
    key+=registry.digest(Path(identity.__file__))
    key+=hashlib.sha256(registry.canonical([local,decisions]).encode()).hexdigest()
    try:old=con.execute('SELECT value FROM meta').fetchone()
    except sqlite3.OperationalError:old=None
    if not old or old[0]!=key:
        rows=registry.read_jsonl(root/DATA)+local
        groups,decisions=identity_view(root,rows)
        con.executescript('DROP TABLE IF EXISTS ideas; DROP TABLE IF EXISTS display; DROP TABLE IF EXISTS search; DROP TABLE IF EXISTS meta; CREATE TABLE ideas(id TEXT PRIMARY KEY,claim_type TEXT,payload TEXT);CREATE TABLE display(id TEXT PRIMARY KEY,claim_type TEXT,payload TEXT);CREATE VIRTUAL TABLE search USING fts5(id UNINDEXED,claim,sources,evidence);CREATE TABLE meta(value TEXT);')
        by_id={r['id']:r for r in rows}
        for r in rows:con.execute('INSERT INTO ideas VALUES(?,?,?)',(r['id'],r['claim_type'],registry.canonical(r)))
        for group_id,members in groups:
            original=[by_id[x] for x in members];representative=dict(original[0])
            representative.update(equivalence_group_id=group_id,equivalence_member_ids=members,
                equivalent_variants=len(members),group_scope_cases=sum(len(r['cases']) for r in original))
            con.execute('INSERT INTO display VALUES(?,?,?)',(representative['id'],representative['claim_type'],registry.canonical(representative)))
            con.execute('INSERT INTO search VALUES(?,?,?,?)',(representative['id'],'\n'.join(r['claim'] for r in original),' '.join(x for r in original for x in r['member_ids']+r.get('registry_context_ids',[])),'\n'.join(e['quote'] for r in original for e in r['evidence'])))
        con.execute('INSERT INTO meta VALUES(?)',(key,));con.commit()
    return con

def local_cards(root=ROOT,include_archived=False):
    path=root/DIRECTORY/'runtime'/'clean_local_review.json'
    if not path.exists():return []
    from tools.semantic_inventory import local_items
    universe={r['id'] for r in local_items(root)}
    result=[]
    for c in json.loads(path.read_text())['cards']:
        validate_card(c,root,universe)
        result.append(dict(c,id='SEMLOCAL:'+hashlib.sha256(c['id'].encode()).hexdigest()[:20],
            ready=False,review_ids=[c['id']],cases=[{k:v for k,v in c.items() if k not in ('claim','evidence')}],
            local_only=True,status=c.get('status','unconfirmed')))
    active,archive=apply_corrections(result,root,{}, {},DIRECTORY+'/runtime/semantic_local_corrections.jsonl')
    return active+archive if include_archived else active

def get_page(root=ROOT,query='',limit=8,offset=0,include_formal=False):
    if not 1<=limit<=20 or offset<0:raise ValueError('limit 1..20, offset >=0')
    con=connect(root)
    try:
        clauses=[];args=[];join=''
        if not include_formal:clauses.append("claim_type!='formal_role'")
        if query.strip():
            join=' JOIN search ON search.id=display.id';clauses.append('search MATCH ?')
            args.append(' AND '.join('"'+q.replace('"','""')+'"' for q in query.split()))
        where=' WHERE '+' AND '.join(clauses) if clauses else ''
        total=con.execute('SELECT COUNT(*) FROM display'+join+where,args).fetchone()[0]
        order='bm25(search,0,10,3,1),display.id' if query.strip() else 'display.id'
        rows=con.execute('SELECT payload FROM display'+join+where+' ORDER BY '+order+' LIMIT ? OFFSET ?',args+[limit,offset]).fetchall()
        cards=[]
        for raw, in rows:
            r=json.loads(raw)
            assessments=[]
            for case in r['cases']:
                a={k:case[k] for k in ('source_polarity','failure_reason','disposition') if case.get(k)}
                if a and a not in assessments:assessments.append(a)
            cards.append({'id':r['id'],'claim':r['claim'][:600],'claim_truncated':len(r['claim'])>600,'claim_type':r['claim_type'],'status':r['status'],'source_occurrences':len(r['member_ids']),'scope_cases':len(r['cases']),
                'equivalent_variants':r.get('equivalent_variants',1),'group_scope_cases':r.get('group_scope_cases',len(r['cases'])),'local_only':r.get('local_only',False),'historical_assessments':registry.bounded_view({'items':assessments[:2]})})
        return {'results':cards,'matched':total,'next_offset':offset+len(cards) if offset+len(cards)<total else None,'meaning':'Reviewed equivalent propositions share one display row. Status, source_occurrences and scope_cases describe the representative only; equivalents retains every original variant. No meaning is confirmed.'}
    finally:con.close()

def scoped_assessments(root,card):
    from tools import semantic_identity as identity
    latest={};seen=set()
    for d in registry.read_jsonl(root/FAILURES):
        key=d['decision_key'];expected=latest[key]['id'] if key in latest else None
        if d['id'] in seen or d.get('previous_revision')!=expected:raise ValueError('broken scoped-assessment revision chain')
        seen.add(d['id']);latest[key]=d
    selected=[d for d in latest.values() if card['id'] in d['targets']]
    if not selected:return []
    con=connect(root)
    try:
        for d in selected:
            if d.get('status')!='reviewed_scoped_context':raise ValueError('unknown scoped assessment status')
            if set(d['card_basis'])!=set(d['targets']) or set(d['effective_basis'])!=set(d['targets']):raise ValueError('incomplete scoped assessment binding')
            for target in d['targets']:
                row=con.execute('SELECT payload FROM ideas WHERE id=?',(target,)).fetchone()
                if not row:raise ValueError('assessed card no longer active; review required')
                current=json.loads(row[0])
                if card_basis(current)!=d['card_basis'][target] or identity.effective_basis(current)!=d['effective_basis'][target]:raise ValueError('stale scoped assessment')
            identity._evidence(root,d.get('evidence'))
            if not d.get('claim_ceiling') or not d.get('scope'):raise ValueError('scoped assessment needs applicability limits')
        return [dict(d,kind='reviewed_question_context',automatic_card_status_propagation=False) for d in selected]
    finally:con.close()

def show(root,identifier,field=None,limit=3,offset=0):
    if not 1<=limit<=20 or offset<0:raise ValueError('limit 1..20, offset >=0')
    con=connect(root)
    try:
        rows=con.execute('SELECT payload FROM ideas WHERE id=?',(identifier,)).fetchall()
        if not rows:
            rows=[(registry.canonical(r),) for r in registry.read_jsonl(root/DATA)+local_cards(root,include_archived=True)+registry.read_jsonl(root/ARCHIVE)
                if identifier==r['id'] or identifier in r['review_ids']]
        if not rows:raise ValueError('unknown semantic idea ID')
        r=json.loads(rows[0][0])
    finally:con.close()
    if field:
        if field in ('equivalents','relations'):
            all_rows=registry.read_jsonl(root/DATA)+local_cards(root)
            groups,decisions=identity_view(root,all_rows);by_id={x['id']:x for x in all_rows}
            members=next((members for _,members in groups if r['id'] in members),[r['id']])
            if field=='equivalents':
                r[field]=[{k:by_id[x][k] for k in ('id','claim','claim_type','status')} for x in members if x in by_id]
            else:r[field]=[d for d in decisions if r['id'] in d['member_ids']]
        if field=='assessments':
            contexts=set(r.get('registry_context_ids',[]))
            data=[{k:x[k] for k in ('id','title','review_status','source_status','blockers','reopen') if k in x}
                for x in registry.read_jsonl(root/DIRECTORY/'semantic_inventory.jsonl') if x['id'] in contexts]
            r['assessments']=scoped_assessments(root,r)+[dict(x,kind='source_experiment_context') for x in data]
        if field not in ('evidence','cases','member_ids','assessments','equivalents','relations'):raise ValueError('field must be evidence, cases, member_ids, assessments, equivalents or relations')
        data=r[field];selected=[];chars=0
        for item in data[offset:offset+limit]:
            bounded=registry.bounded_view(item) if isinstance(item,dict) else item
            size=len(registry.canonical(bounded))
            if selected and chars+size>10000:break
            selected.append(bounded);chars+=size
        return {'id':r['id'],'field':field,'scope':'Source context; experiment assessments are not automatic verdicts on every component.',
            'items':selected,'matched':len(data),'next_offset':offset+len(selected) if offset+len(selected)<len(data) else None}
    return registry.bounded_view(r)

def main(argv=None,root=ROOT):
    p=argparse.ArgumentParser();p.add_argument('query',nargs='?',default='');p.add_argument('--shortlist',action='store_true');p.add_argument('--show');p.add_argument('--field');p.add_argument('--limit',type=int,default=8);p.add_argument('--offset',type=int,default=0);p.add_argument('--include-formal',action='store_true');p.add_argument('--build',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args(argv)
    if not 1<=a.limit<=20 or a.offset<0:p.error('limit 1..20, offset >=0')
    if a.build:result=build(root)
    elif a.check:
        m=validate(root);result={k:m[k] for k in ('status','cards','semantic_cards','formal_role_cards')}
    elif a.shortlist:
        from tools.semantic_priority_view import get_page as priority_page
        result=priority_page(root,a.query,a.limit,a.offset)
    elif a.show:result=show(root,a.show,a.field,a.limit,a.offset)
    else:result=get_page(root,a.query,a.limit,a.offset,a.include_formal)
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
