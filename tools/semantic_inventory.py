"""Inclusive historical idea queue. Never infer semantic identity from lexical matches."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3
import re
from tools import research_registry as registry
ROOT=Path(__file__).resolve().parents[1]
DATA='research_registry/semantic_inventory.jsonl'
MANIFEST='research_registry/INVENTORY_MANIFEST.json'
LOCAL='research_registry/runtime/untracked_semantic_proposals.jsonl'
EXTRA=['research_registry/decisions/legacy_proposal_extraction.jsonl','research_registry/decisions/legacy_semantic_components.jsonl']

def read_rows(path):
    return registry.read_jsonl(path) if path.exists() else []

def normalized_extra(row, source_set):
    kind=row.get('record_type','')
    if kind in ('extraction_manifest','extraction_summary','source_coverage','manifest','coverage'):return None
    relative=row.get('path',row.get('source_path',''))
    title=row.get('title',row.get('heading',row.get('section',row.get('hypothesis','Historical source component'))))
    statement=row.get('hypothesis',row.get('statement',row.get('exact_statement',row.get('text',row.get('verbatim',row.get('reason',''))))))
    if not isinstance(statement,str):statement=json.dumps(statement,ensure_ascii=False)
    identifier=row.get('id',row.get('record_id')) or ('COMPONENT:'+hashlib.sha256(registry.canonical(row).encode()).hexdigest()[:24])
    return {'id':identifier,'item_type':('hypothesis_proposal' if row.get('candidate_type')=='explicit_proposal' else 'source_excerpt') if kind=='authored_card' else ('hypothesis_component' if kind=='hypothesis_component' else 'unresolved_source_block'),
            'source_set':source_set,'source_record_id':row.get('parent_id',row.get('parent_gdt')),
            'title':str(title),'statement':statement,'scope':'unknown','disposition':'extracted_needs_review',
            'assessment_basis':'verbatim_source_extraction_not_scientific_review','ready':False,
            'source_status':row.get('source_status','not_assessed'),'review_status':'extracted_unreviewed',
            'sources':[{'path':relative,'locator':f"line:{row.get('line',row.get('line_start',row.get('start_line',1)))}",'sha256':row.get('source_sha256','')} ] if relative else [],
            'events':[],'blockers':[],'reopen':{'policy':'unreviewed','all_of':[],'not_sufficient':['Source extraction alone']},
            'relations':[],'extraction':row,'identity':'distinct_source_component_not_proven_independent_idea'}

def build(root=ROOT):
    errors=registry.source_freshness(root)
    if errors:raise ValueError('; '.join(errors))
    records=registry._assemble(root)
    triage_path='research_registry/decisions/idea_queue_triage.json'
    triage=json.loads((root/triage_path).read_text()) if (root/triage_path).exists() else {'entries':[]}
    triaged={x['id']:x for x in triage['entries']}
    items=[]
    for rid,r in sorted(records.items()):
        t=triaged.get(rid,{})
        # The whole record remains available even if a previous review addressed only a subclaim.
        items.append({'id':rid,'item_type':r['kind'],'source_set':'research_registry','source_record_id':rid,
                      'title':r['title'],'statement':r.get('summary',''),'scope':t.get('category',r.get('scope','unknown')),
                      'disposition':t.get('disposition','candidate_needs_scope_review' if r.get('scope','unknown')=='unknown' else 'historical_review_required'),
                      'assessment_basis':r.get('assessment_basis','unreviewed_import'),'ready':False,
                      'source_status':r.get('source_status',''),'review_status':r.get('review_status','unreviewed_import'),
                      'sources':r.get('sources',[]),'events':r.get('events',[]),'blockers':r.get('blockers',[]),
                      'reopen':r.get('reopen',{}),'relations':r.get('relations',[]),'aliases':r.get('aliases',[]),
                      'triage':t,'identity':'source_record_not_independent_hypothesis_count'})
    inputs=['tools/semantic_inventory.py','tools/extract_legacy_proposals.py','tools/extract_semantic_components.py','research_registry/imported.jsonl','research_registry/curation.jsonl','research_registry/SOURCE_MANIFEST.json',triage_path]
    if (root/'research_registry/ideas.jsonl').exists():inputs.append('research_registry/ideas.jsonl')
    extra_coverage=[];external_sources={}
    for relative in EXTRA:
        if not (root/relative).exists():continue
        inputs.append(relative)
        for row in read_rows(root/relative):
            item=normalized_extra(row,Path(relative).stem)
            if item:items.append(item)
            else:extra_coverage.append(row)
            if row.get('record_type')=='extraction_manifest':
                for pointer in row.get('unresolved_source_pointers',[]):
                    source_pointer=dict(pointer, record_type='unresolved_source_pointer',
                        id='LEGACY_SOURCE:'+hashlib.sha256(registry.canonical(pointer).encode()).hexdigest()[:24],
                        title=pointer['path'], statement=pointer.get('reason','Source requires review'))
                    items.append(normalized_extra(source_pointer,Path(relative).stem))
                for s in row.get('sources',[]):
                    if s.get('path') and s.get('sha256'):external_sources[s['path']]=s['sha256']
            path=row.get('path',row.get('source_path'))
            sha=row.get('source_sha256',row.get('sha256'))
            if path and sha:external_sources[path]=sha
    ids=[r['id'] for r in items]
    if len(set(ids))!=len(ids):raise ValueError('duplicate item IDs')
    for path,sha in external_sources.items():
        p=registry.evidence_path(root,path)
        if not p.is_file() or registry.digest(p)!=sha:raise ValueError('stale extraction source: '+path)
    registry.write_jsonl(root/DATA,sorted(items,key=lambda x:x['id']))
    manifest={'schema_version':1,'status':'INCLUSIVE_SOURCE_INVENTORY','items':len(items),
              'source_records':len(records),'extracted_items':len(items)-len(records),
              'item_types':dict(Counter(x['item_type'] for x in items)),
              'dispositions':dict(Counter(x['disposition'] for x in items)),
              'scope_counts':dict(Counter(x['scope'] for x in items)),
              'unique_semantic_ideas':None,'source_coverage_records':len(extra_coverage),
              'input_sha256':{p:registry.digest(root/p) for p in inputs if (root/p).exists()},
              'external_source_sha256':external_sources,'inventory_sha256':registry.digest(root/DATA),
              'limits':['Includes all source records regardless of keywords, empty summary or previous scope.',
                        'Historical records, proposals and extracted components are different units; total is not independent idea count.',
                        'Unknown scope and unparsed source blocks remain visible; no automatic semantic merger or reopening.',
                        'Missing/deleted historical material cannot be reconstructed; see SOURCE_GAPS.json.',
                        'Full original record events and source locators are retained. Extraction source coverage remains in the bound inputs.']}
    (root/MANIFEST).write_text(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    return {k:manifest[k] for k in ('status','items','source_records','extracted_items','item_types','unique_semantic_ideas')}

def check(root=ROOT):
    m=json.loads((root/MANIFEST).read_text())
    errors=registry.source_freshness(root)
    if errors:raise ValueError('; '.join(errors))
    if registry.digest(root/DATA)!=m['inventory_sha256']:raise ValueError('changed inventory')
    for path,sha in {**m['input_sha256'],**m['external_source_sha256']}.items():
        p=registry.evidence_path(root,path)
        if not p.is_file() or registry.digest(p)!=sha:raise ValueError('stale inventory input: '+path)
    return m

def prose_blocks(root, path):
    """Source-bounded prose only; never expose fences or sealed/private blocks."""
    if not path.endswith('.md'):return []
    from tools.work_preflight import CREDENTIAL_PATTERNS, LOCAL_PATH_PATTERNS
    sealed=re.compile(r'(?<![A-Za-z0-9])f84[a-z0-9]*',re.I)
    lines=registry.evidence_path(root,path).read_text(encoding='utf-8-sig').splitlines()
    blocks=[];pending=[];start=1;fence=None
    def emit(end):
        nonlocal pending
        if pending:
            text='\n'.join(pending);raw=text.encode()
            if not sealed.search(text) and not any(p.search(raw) for p in CREDENTIAL_PATTERNS+LOCAL_PATH_PATTERNS):
                blocks.append({'line_start':start,'line_end':end,'text':text})
            pending=[]
    for n,line in enumerate(lines,1):
        marker=re.match(r'^\s*(`{3,}|~{3,})',line)
        if marker:
            emit(n-1)
            if fence is None:fence=marker.group(1)[0]
            elif marker.group(1)[0]==fence:fence=None
            continue
        if fence:continue
        if not line.strip():emit(n-1);continue
        if not pending:start=n
        pending.append(line)
    emit(len(lines));return blocks

def local_items(root):
    rows=[]
    for source in read_rows(root/LOCAL):
        item=normalized_extra(source,'local_untracked_proposals')
        if not item:continue
        for evidence in item['sources']:
            path=registry.evidence_path(root,evidence['path'])
            if not path.is_file() or registry.digest(path)!=evidence['sha256']:
                raise ValueError('stale local proposal source: '+evidence['path'])
        rows.append(item)
    return rows


def connection(root=ROOT):
    m=check(root);folder=root/'research_registry/runtime';folder.mkdir(parents=True,exist_ok=True)
    path=folder/'semantic_inventory.sqlite3'
    local_path=root/LOCAL
    local_sha=registry.digest(local_path) if local_path.exists() else ''
    key=hashlib.sha256((m['inventory_sha256']+local_sha+registry.digest(Path(__file__))).encode()).hexdigest()
    supplemental=local_items(root)
    con=sqlite3.connect(path)
    try:old=con.execute('SELECT value FROM meta').fetchone()
    except sqlite3.OperationalError:old=None
    if not old or old[0]!=key:
        con.executescript('DROP TABLE IF EXISTS items; DROP TABLE IF EXISTS search; DROP TABLE IF EXISTS meta; CREATE TABLE items(id TEXT PRIMARY KEY,item_type TEXT,scope TEXT,disposition TEXT,payload TEXT); CREATE VIRTUAL TABLE search USING fts5(id UNINDEXED,body); CREATE TABLE meta(value TEXT);')
        source_text_cache={};indexed_sources=set()
        for row in read_rows(root/DATA)+supplemental:
            raw=registry.canonical(row)
            con.execute('INSERT INTO items VALUES(?,?,?,?,?)',(row['id'],row['item_type'],row['scope'],row['disposition'],raw))
            fulltext='\n'.join([row['title'],row['statement'],str(row.get('source_status','')),*row.get('aliases',[])]+[str(e.get(k,'')) for e in row.get('events',[]) for k in ('summary','limitations','status')]+[e['path'] for e in row.get('sources',[])])
            if row['item_type']=='unresolved_source_block':
                for evidence in row['sources']:
                    source=evidence['path']
                    if source in m['external_source_sha256'] and source.endswith('.md') and source not in indexed_sources:
                        if source not in source_text_cache:
                            source_text_cache[source]='\n\n'.join(b['text'] for b in prose_blocks(root,source))
                        fulltext+='\n'+source_text_cache[source]
                        indexed_sources.add(source)
            con.execute('INSERT INTO search VALUES(?,?)',(row['id'],fulltext))
        con.execute('INSERT INTO meta VALUES(?)',(key,));con.commit()
    return con

def get_page(root=ROOT,query='',limit=8,offset=0,scope=None,disposition=None,item_type=None):
    if not 1<=limit<=20 or offset<0:raise ValueError('limit 1..20; offset >=0')
    con=connection(root)
    try:
        conditions=[];args=[]
        for col,val in [('scope',scope),('disposition',disposition),('item_type',item_type)]:
            if val:conditions.append('items.'+col+'=?');args.append(val)
        join=''
        if query:
            join=' JOIN search ON search.id=items.id';conditions.append('search MATCH ?')
            args.append(' AND '.join('"'+s.replace('"','""')+'"' for s in query.split()))
        where=' WHERE '+' AND '.join(conditions) if conditions else ''
        total=con.execute('SELECT COUNT(*) FROM items'+join+where,args).fetchone()[0]
        columns="payload, snippet(search,1,'[',']',' … ',35)" if query else "payload, NULL"
        rows=con.execute('SELECT '+columns+' FROM items'+join+where+' ORDER BY items.id LIMIT ? OFFSET ?',args+[limit,offset]).fetchall()
        cards=[]
        for raw,snippet in rows:
            x=json.loads(raw);card={k:x[k] for k in ('id','item_type','title','scope','disposition','assessment_basis','ready')}
            card['title']=card['title'][:240];card['statement_preview']=(snippet or x['statement'])[:360];cards.append(card)
        return {'results':cards,'matched':total,'next_offset':offset+len(cards) if offset+len(cards)<total else None,'meaning':'Inclusive historical list; records and components are not a deduplicated idea count.'}
    finally:con.close()

def get_entry(root,identifier):
    con=connection(root)
    try:
        row=con.execute('SELECT payload FROM items WHERE id=?',(identifier,)).fetchone()
        if not row:raise ValueError('unknown inventory ID')
        return registry.bounded_view(json.loads(row[0]))
    finally:con.close()

def source_page(root,identifier,offset=0,limit=3):
    if not 1<=limit<=8 or offset<0:raise ValueError('source limit 1..8; offset >=0')
    m=check(root);con=connection(root)
    try:
        result=con.execute('SELECT payload FROM items WHERE id=?',(identifier,)).fetchone()
        if not result:raise ValueError('unknown inventory ID')
        item=json.loads(result[0])
    finally:con.close()
    blocks=[]
    for evidence in item['sources']:
        path=evidence['path']
        if path in m['external_source_sha256'] and path.endswith('.md'):
            blocks.extend(dict(source=path,**b) for b in prose_blocks(root,path))
    chosen=[];size=0
    for block in blocks[offset:offset+limit]:
        shown=dict(block,text=block['text'][:3000],truncated=len(block['text'])>3000)
        cost=len(registry.canonical(shown))
        if chosen and size+cost>10000:break
        chosen.append(shown);size+=cost
    return {'id':identifier,'source_blocks':chosen,'matched':len(blocks),
            'next_offset':offset+len(chosen) if offset+len(chosen)<len(blocks) else None,
            'meaning':'Safe historical source prose; source text is not endorsed meaning.'}


def main(argv=None,root=ROOT):
    p=argparse.ArgumentParser();p.add_argument('query',nargs='?',default='');p.add_argument('--show');p.add_argument('--source-text',action='store_true');p.add_argument('--scope');p.add_argument('--item-type');p.add_argument('--disposition');p.add_argument('--limit',type=int,default=8);p.add_argument('--offset',type=int,default=0);p.add_argument('--build',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args(argv)
    if a.build:result=build(root)
    elif a.check:
        m=check(root);result={k:m[k] for k in ('status','items','source_records','extracted_items','item_types','unique_semantic_ideas')}
    elif a.source_text:
        if not a.show:p.error('--source-text requires --show')
        result=source_page(root,a.show,a.offset,min(a.limit,8))
    elif a.show:result=get_entry(root,a.show)
    else:result=get_page(root,a.query,a.limit,a.offset,a.scope,a.disposition,a.item_type)
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
