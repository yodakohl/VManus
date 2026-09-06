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
REVIEWS=[DIRECTORY+'/decisions/'+name for name in ['clean_proposal_review.json','clean_component_review.json','clean_ip_review.json','clean_historical_review.json']]
EXTRA_REVIEWS=[DIRECTORY+'/decisions/'+name for name in ['clean_prereg_candidate_review.json','clean_report_proposals_review.json','clean_middle_sidequest_review.json','clean_late_sidequest_review.json','clean_root_early_review.json','clean_final_sidequest_review.json']]
SEMANTIC_TYPES={'lexical_hypothesis','semantic_model','functional_hypothesis'}
TYPES=SEMANTIC_TYPES|{'formal_role'}
PLACEHOLDER=re.compile(r'^(?:unknown|unresolved|not[_ ]assessed|needs?[_ ]review|source[_ ]requires[_ ]review|review[_ ]priority|todo|tbd|placeholder|noch zu|unbekannt|zu prüfen)(?:\b|$)',re.I)
TECHNICAL_ASSIGNMENT=re.compile(r'^(?:kind|status|verdict|decision|transferable|commodity|seed|random_state|n_jobs|output|source_path|file|sha256|p_value|n|score|accuracy)\s*(?:→|=|:)',re.I)

def canonical_claim(text):
    # Typography/whitespace only. Do not erase negation, alternative senses or word case.
    return ' '.join(text.replace('`','').split())

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
    registry.write_jsonl(root/DATA,rows)
    manifest={'schema_version':1,'status':'SOURCE_REVIEWED_CONCRETE_CLAIMS','cards':len(rows),
        'builder_sha256':registry.digest(Path(__file__)),
        'semantic_cards':sum(r['claim_type'] in SEMANTIC_TYPES for r in rows),
        'formal_role_cards':sum(r['claim_type']=='formal_role' for r in rows),
        'review_cards_before_exact_assertion_grouping':review_card_count,
        'exact_assertion_repetitions_grouped':review_card_count-len(rows),
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
    for path,sha in {**m['input_sha256'],**m['source_sha256']}.items():
        p=registry.evidence_path(root,path)
        if not p.is_file() or registry.digest(p)!=sha:raise ValueError('stale clean idea input: '+path)
    return m

def connect(root=ROOT):
    m=validate(root);folder=root/DIRECTORY/'runtime';folder.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(folder/'semantic_ideas.sqlite3')
    key=m['data_sha256']+registry.digest(Path(__file__))
    local=local_cards(root)
    key+=hashlib.sha256(registry.canonical(local).encode()).hexdigest()
    try:old=con.execute('SELECT value FROM meta').fetchone()
    except sqlite3.OperationalError:old=None
    if not old or old[0]!=key:
        con.executescript('DROP TABLE IF EXISTS ideas; DROP TABLE IF EXISTS search; DROP TABLE IF EXISTS meta; CREATE TABLE ideas(id TEXT PRIMARY KEY,claim_type TEXT,payload TEXT);CREATE VIRTUAL TABLE search USING fts5(id UNINDEXED,claim,sources,evidence);CREATE TABLE meta(value TEXT);')
        for r in registry.read_jsonl(root/DATA)+local:
            con.execute('INSERT INTO ideas VALUES(?,?,?)',(r['id'],r['claim_type'],registry.canonical(r)))
            con.execute('INSERT INTO search VALUES(?,?,?,?)',(r['id'],r['claim'],' '.join(r['member_ids']+r.get('registry_context_ids',[])),'\n'.join(e['quote'] for e in r['evidence'])))
        con.execute('INSERT INTO meta VALUES(?)',(key,));con.commit()
    return con

def local_cards(root=ROOT):
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
    return result

def get_page(root=ROOT,query='',limit=8,offset=0,include_formal=False):
    if not 1<=limit<=20 or offset<0:raise ValueError('limit 1..20, offset >=0')
    con=connect(root)
    try:
        clauses=[];args=[];join=''
        if not include_formal:clauses.append("claim_type!='formal_role'")
        if query.strip():
            join=' JOIN search ON search.id=ideas.id';clauses.append('search MATCH ?')
            args.append(' AND '.join('"'+q.replace('"','""')+'"' for q in query.split()))
        where=' WHERE '+' AND '.join(clauses) if clauses else ''
        total=con.execute('SELECT COUNT(*) FROM ideas'+join+where,args).fetchone()[0]
        order='bm25(search,0,10,3,1),ideas.id' if query.strip() else 'ideas.id'
        rows=con.execute('SELECT payload FROM ideas'+join+where+' ORDER BY '+order+' LIMIT ? OFFSET ?',args+[limit,offset]).fetchall()
        cards=[]
        for raw, in rows:
            r=json.loads(raw)
            assessments=[]
            for case in r['cases']:
                a={k:case[k] for k in ('source_polarity','failure_reason','disposition') if case.get(k)}
                if a and a not in assessments:assessments.append(a)
            cards.append({'id':r['id'],'claim':r['claim'][:600],'claim_truncated':len(r['claim'])>600,'claim_type':r['claim_type'],'status':r['status'],'source_occurrences':len(r['member_ids']),'scope_cases':len(r['cases']),
                'local_only':r.get('local_only',False),'historical_assessments':registry.bounded_view({'items':assessments[:2]})})
        return {'results':cards,'matched':total,'next_offset':offset+len(cards) if offset+len(cards)<total else None,'meaning':'Concrete historical hypotheses; unconfirmed meanings. Source archive is available separately.'}
    finally:con.close()

def show(root,identifier,field=None,limit=3,offset=0):
    if not 1<=limit<=20 or offset<0:raise ValueError('limit 1..20, offset >=0')
    con=connect(root)
    try:
        rows=con.execute('SELECT payload FROM ideas WHERE id=?',(identifier,)).fetchall()
        if not rows:
            rows=[(registry.canonical(r),) for r in registry.read_jsonl(root/DATA)+local_cards(root) if identifier in r['review_ids']]
        if not rows:raise ValueError('unknown semantic idea ID')
        r=json.loads(rows[0][0])
    finally:con.close()
    if field:
        if field=='assessments':
            contexts=set(r.get('registry_context_ids',[]))
            data=[{k:x[k] for k in ('id','title','review_status','source_status','blockers','reopen') if k in x}
                for x in registry.read_jsonl(root/DIRECTORY/'semantic_inventory.jsonl') if x['id'] in contexts]
            r['assessments']=data
        if field not in ('evidence','cases','member_ids','assessments'):raise ValueError('field must be evidence, cases, member_ids or assessments')
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
    p=argparse.ArgumentParser();p.add_argument('query',nargs='?',default='');p.add_argument('--show');p.add_argument('--field');p.add_argument('--limit',type=int,default=8);p.add_argument('--offset',type=int,default=0);p.add_argument('--include-formal',action='store_true');p.add_argument('--build',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args(argv)
    if not 1<=a.limit<=20 or a.offset<0:p.error('limit 1..20, offset >=0')
    if a.build:result=build(root)
    elif a.check:
        m=validate(root);result={k:m[k] for k in ('status','cards','semantic_cards','formal_role_cards')}
    elif a.show:result=show(root,a.show,a.field,a.limit,a.offset)
    else:result=get_page(root,a.query,a.limit,a.offset,a.include_formal)
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
