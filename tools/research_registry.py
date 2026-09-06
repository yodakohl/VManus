"""Bounded, offline research memory. Evidence navigation never authorizes a rerun."""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
import fcntl
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sqlite3
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = 'research_registry'
KINDS = {'idea', 'family', 'attempt', 'history', 'anchor'}
SCOPES = {'semantic', 'structural', 'method', 'acquisition', 'workflow', 'unknown'}
VERDICTS = {'unreviewed', 'untested', 'supported_limited', 'nonconfirming',
            'refuted_specific_model', 'inconclusive', 'not_tested', 'stopped_by_user'}
POLICIES = {'unreviewed', 'conditional', 'do_not_repeat_same_model', 'user_stopped'}
CHANGES = {'new_data', 'new_binding', 'new_design', 'source_correction', 'new_authorization'}
RELATIONS = {'tests', 'duplicate_of', 'related_to', 'corrects', 'supersedes',
             'same_experiment_reference'}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def safe_relative_path(value):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value:
        return False
    p = PurePosixPath(value)
    return (not p.is_absolute() and p.as_posix() == value and
            not any(x.startswith('.') or x in {'runtime', 'private'} for x in p.parts))


def evidence_path(root, value):
    if not safe_relative_path(value):
        raise ValueError(f'unsafe evidence path: {value!r}')
    path = root / value
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('evidence symlink leaves repository')
    return path


def atomic_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent,
                                     prefix='.registry-', delete=False) as stream:
        stream.write(content)
        temporary = Path(stream.name)
    temporary.replace(path)


def read_jsonl(path):
    if not path.exists():
        return []
    rows = []
    with path.open(encoding='utf-8') as stream:
        for number, line in enumerate(stream, 1):
            if line.strip():
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f'invalid JSONL {path.name}:{number}') from exc
                if not isinstance(row, dict):
                    raise ValueError(f'object required at {path.name}:{number}')
                rows.append(row)
    return rows


def write_jsonl(path, rows):
    atomic_text(path, ''.join(canonical(row) + '\n' for row in rows))


@contextmanager
def writer(root):
    folder = root / DIRECTORY / 'runtime'
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / 'writer.lock').open('a') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def write_snapshot(root, records, manifest=None):
    """Write import artifacts only; never overwrite authored ideas or reviews."""
    folder = root / DIRECTORY
    write_jsonl(folder / 'imported.jsonl', sorted(records, key=lambda x: x['id']))
    manifest = dict(manifest or {'sources': []})
    manifest['snapshot_sha256'] = digest(folder / 'imported.jsonl')
    atomic_text(folder / 'SOURCE_MANIFEST.json', canonical(manifest) + '\n')


def record_fingerprint(record):
    """New events invalidate a review; unrelated source-file append does not."""
    content = {k: v for k, v in record.items()
               if k not in {'sources', 'imported_fields', 'signals', 'signals_policy'}}
    content['relations'] = [r for r in record.get('relations',[])
                            if r.get('type') != 'same_experiment_reference']
    content['events'] = [{k: v for k, v in event.items() if k != 'source_row'}
                         for event in record.get('events', [])]
    fields = record.get('imported_fields', {})
    content['imported_fields'] = {k: v for k, v in fields.items()
                                  if k not in {'definition_lines', 'mention_lines', 'excerpts'}}
    return hashlib.sha256(canonical(content).encode()).hexdigest()


def design_fingerprint(record):
    design = record.get('design', {})
    keys = ('mechanism', 'unit', 'contrast', 'prediction', 'scope')
    if not all(isinstance(design.get(k), str) and design[k].strip() for k in keys):
        return ''
    normalized = {k: ' '.join(design[k].casefold().split()) for k in keys}
    return hashlib.sha256(canonical(normalized).encode()).hexdigest()


def _evidence(review):
    paths = set()
    for item in review.get('blockers', []) + review.get('relations', []):
        paths.update(item.get('evidence', []))
    for item in review.get('reopen', {}).get('all_of', []):
        paths.update(item.get('evidence', []))
    return sorted(paths)


def _base_records(root):
    folder = root / DIRECTORY
    rows = read_jsonl(folder / 'imported.jsonl') + read_jsonl(folder / 'ideas.jsonl')
    records = {}
    for row in rows:
        identifier = row.get('id')
        if not isinstance(identifier, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_:.-]{0,150}', identifier):
            raise ValueError('invalid record id')
        if identifier in records:
            raise ValueError(f'duplicate record id: {identifier}')
        if row.get('kind') not in KINDS or row.get('scope', 'unknown') not in SCOPES:
            raise ValueError(f'invalid record kind/scope: {identifier}')
        if row.get('verdict', 'unreviewed') not in VERDICTS:
            raise ValueError(f'invalid verdict: {identifier}')
        for source in row.get('sources', []):
            evidence_path(root, source['path'])
        records[identifier] = row
    return records


def _review_rows(root):
    latest = {}
    for row in read_jsonl(root / DIRECTORY / 'curation.jsonl'):
        identifier = row.get('record_id')
        if identifier in latest:
            previous = latest[identifier]
            if row.get('previous_sha256') != hashlib.sha256(canonical(previous).encode()).hexdigest():
                raise ValueError(f'broken review revision chain: {identifier}')
        if row.get('scope') not in SCOPES or row.get('verdict') not in VERDICTS:
            raise ValueError(f'invalid curated scope/verdict: {identifier}')
        reopen = row.get('reopen', {})
        if reopen.get('policy') not in POLICIES:
            raise ValueError(f'invalid reopening policy: {identifier}')
        if any(x.get('change') not in CHANGES for x in reopen.get('all_of', [])):
            raise ValueError(f'invalid change requirement: {identifier}')
        latest[identifier] = row
    return latest


def bind_curations(root):
    """Explicit initial migration binding, never silently rebind an old review."""
    records = _base_records(root)
    path = root / DIRECTORY / 'curation.jsonl'
    rows = read_jsonl(path)
    bound = 0
    for row in rows:
        if row.get('basis_sha256'):
            continue
        identifier = row['record_id']
        if identifier not in records:
            raise ValueError(f'unknown curated record: {identifier}')
        row['basis_sha256'] = record_fingerprint(records[identifier])
        row['evidence_sha256'] = {}
        for relative in _evidence(row):
            evidence = evidence_path(root, relative)
            if not evidence.is_file():
                raise ValueError(f'missing review evidence: {relative}')
            row['evidence_sha256'][relative] = digest(evidence)
        bound += 1
    write_jsonl(path, rows)
    return {'bound_reviews': bound, 'not_checked': 'historical truth or sufficiency of source evidence'}


def _assemble(root):
    records = _base_records(root)
    for identifier, review in _review_rows(root).items():
        if identifier not in records:
            raise ValueError(f'unknown curated record: {identifier}')
        record = records[identifier]
        errors = []
        if review.get('basis_sha256') != record_fingerprint(record):
            errors.append('review_basis_changed_or_unbound')
        hashes = review.get('evidence_sha256', {})
        for relative in _evidence(review):
            path = evidence_path(root, relative)
            if not path.is_file():
                errors.append('missing_evidence:' + relative)
            elif hashes.get(relative) != digest(path):
                errors.append('evidence_changed_or_unbound:' + relative)
        for key in ('scope', 'verdict', 'blockers', 'reopen', 'relations', 'design',
                    'assessment_basis', 'related_change_types', 'inherited_status', 'inherited_summary'):
            if key in review:
                record[key] = review[key]
        record['review_status'] = ('stale_review' if errors else
                                  'inherited_summary' if review.get('assessment_basis') == 'registry_summary_only'
                                  else 'curated')
        record['review_errors'] = errors
        record['latest_review'] = {'reviewer':review.get('reviewer','not_recorded'),
                                  'reason':review.get('reason','not_recorded')}
    edges = {}
    for identifier, record in records.items():
        edges[identifier] = []
        for link in record.get('relations', []):
            if link.get('type') not in RELATIONS or link.get('target') not in records:
                raise ValueError(f'invalid or dangling relation on {identifier}')
            if link['target'] == identifier:
                raise ValueError(f'self relation on {identifier}')
            if link['type'] in {'duplicate_of', 'supersedes'}:
                edges[identifier].append(link['target'])
    # Only identity/replacement links must be acyclic. Related-to links may cycle.
    remaining = {identifier:len(targets) for identifier,targets in edges.items()}
    children = {identifier:[] for identifier in records}
    for identifier, targets in edges.items():
        for target in targets: children[target].append(identifier)
    ready = [identifier for identifier,count in remaining.items() if count == 0]
    visited = 0
    while ready:
        identifier = ready.pop(); visited += 1
        for child in children[identifier]:
            remaining[child] -= 1
            if remaining[child] == 0: ready.append(child)
    if visited != len(records):
        raise ValueError('cycle in duplicate/supersedes relations')
    return records


def _manifest_sources(manifest):
    sources = manifest.get('sources', [])
    return list(sources.values()) if isinstance(sources, dict) else sources


def source_freshness(root):
    path = root / DIRECTORY / 'SOURCE_MANIFEST.json'
    if not path.exists():
        return ['missing source manifest']
    errors = []
    manifest = json.loads(path.read_text())
    snapshot = root / DIRECTORY / 'imported.jsonl'
    if manifest.get('snapshot_sha256') and (not snapshot.is_file() or digest(snapshot) != manifest['snapshot_sha256']):
        errors.append('snapshot changed outside importer')
    for source in _manifest_sources(manifest):
        p = evidence_path(root, source['path'])
        if not p.is_file() or digest(p) != source['sha256']:
            errors.append('stale imported source: ' + source['path'])
    if manifest.get('importer_sha256'):
        implementation = root / 'tools/research_registry_import.py'
        if not implementation.is_file() or digest(implementation) != manifest['importer_sha256']:
            errors.append('stale importer implementation')
    return errors


def _cache_key(root):
    paths = [root / DIRECTORY / n for n in
             ('imported.jsonl', 'ideas.jsonl', 'curation.jsonl', 'SOURCE_MANIFEST.json')]
    # A primary report changing also invalidates the derived review state.
    for review in _review_rows(root).values():
        paths.extend(evidence_path(root, p) for p in _evidence(review))
    pairs = [(str(p.relative_to(root)), digest(p) if p.is_file() else 'MISSING')
             for p in sorted(set(paths))]
    return hashlib.sha256(canonical({'sources':pairs,'implementation':digest(Path(__file__))}).encode()).hexdigest()


def build_index(root):
    errors = source_freshness(root)
    if errors:
        raise ValueError('; '.join(errors) + '; run ideas refresh')
    records = _assemble(root)
    folder = root / DIRECTORY / 'runtime'
    folder.mkdir(parents=True, exist_ok=True)
    temporary = folder / 'index-building.sqlite3'
    temporary.unlink(missing_ok=True)
    connection = sqlite3.connect(temporary)
    try:
        connection.executescript('''
        CREATE TABLE records (id TEXT PRIMARY KEY, kind TEXT, scope TEXT, verdict TEXT,
                              review_status TEXT, signature TEXT, payload TEXT);
        CREATE TABLE aliases (alias TEXT, id TEXT, PRIMARY KEY(alias,id));
        CREATE INDEX alias_lookup ON aliases(alias);
        CREATE TABLE facets (id TEXT, facet TEXT, value TEXT);
        CREATE INDEX facet_lookup ON facets(facet,value,id);
        CREATE TABLE relations (source TEXT,target TEXT,kind TEXT,payload TEXT);
        CREATE INDEX relations_target ON relations(target);
        CREATE INDEX relations_source ON relations(source);
        CREATE TABLE reviews (record_id TEXT, sequence INTEGER, payload TEXT);
        CREATE INDEX reviews_record ON reviews(record_id,sequence);
        CREATE VIRTUAL TABLE search USING fts5(id UNINDEXED,title,body,tokenize='unicode61');
        CREATE TABLE meta (key TEXT PRIMARY KEY,value TEXT);
        ''')
        for record in records.values():
            identifier = record['id']
            connection.execute('INSERT INTO records VALUES (?,?,?,?,?,?,?)',
                (identifier, record['kind'], record.get('scope','unknown'),
                 record.get('verdict','unreviewed'), record.get('review_status','imported_unreviewed'),
                 design_fingerprint(record), canonical(record)))
            for alias in set([identifier] + record.get('aliases', [])):
                connection.execute('INSERT INTO aliases VALUES (?,?)', (alias.casefold(), identifier))
            for item in record.get('blockers', []):
                connection.execute('INSERT INTO facets VALUES (?,?,?)', (identifier,'blocker',item['code']))
            for item in record.get('reopen', {}).get('all_of', []):
                connection.execute('INSERT INTO facets VALUES (?,?,?)', (identifier,'change',item['change']))
            for change in record.get('related_change_types',[]):
                connection.execute('INSERT INTO facets VALUES (?,?,?)', (identifier,'change',change))
            for signal in record.get('signals', []):
                connection.execute('INSERT INTO facets VALUES (?,?,?)', (identifier,'signal',signal))
            for relation in record.get('relations',[]):
                connection.execute('INSERT INTO relations VALUES (?,?,?,?)',
                    (identifier,relation['target'],relation['type'],canonical(relation)))
            connection.execute('INSERT INTO search VALUES (?,?,?)',
                               (identifier, record['title'], canonical(record)))
        for sequence,review in enumerate(read_jsonl(root / DIRECTORY / 'curation.jsonl')):
            connection.execute('INSERT INTO reviews VALUES (?,?,?)',
                               (review['record_id'],sequence,canonical(review)))
        connection.execute('INSERT INTO meta VALUES (?,?)', ('cache_key', _cache_key(root)))
        connection.commit()
    finally:
        connection.close()
    temporary.replace(folder / 'index.sqlite3')
    return {'records': len(records), 'kinds': dict(Counter(r['kind'] for r in records.values())),
            'curated': sum(r.get('review_status') == 'curated' for r in records.values()),
            'ledger_events': sum(len(r.get('events', [])) for r in records.values())}


def _connect(root):
    errors = source_freshness(root)
    if errors:
        raise ValueError('; '.join(errors) + '; run ideas refresh')
    path = root / DIRECTORY / 'runtime' / 'index.sqlite3'
    key = _cache_key(root)
    rebuild = not path.exists()
    if not rebuild:
        with sqlite3.connect(path) as connection:
            row = connection.execute("SELECT value FROM meta WHERE key='cache_key'").fetchone()
            rebuild = row is None or row[0] != key
    if rebuild:
        with writer(root):
            build_index(root)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def _limit(value, maximum=20):
    if not 1 <= value <= maximum:
        raise ValueError(f'limit must be between 1 and {maximum}')
    return value


def _clip(value, size):
    text = str(value)
    return text if len(text) <= size else text[:size-1] + '…'


def bounded_view(value, budget=12000):
    """Bound model-facing detail without changing stored evidence or decisions."""
    if len(canonical(value)) <= budget:
        return value
    original_size = len(canonical(value))
    for width, items in [(500,8),(250,5),(120,3),(60,2)]:
        def trim(obj):
            if isinstance(obj,str): return _clip(obj,width)
            if isinstance(obj,list): return [trim(x) for x in obj[:items]]
            if isinstance(obj,dict): return {k:trim(v) for k,v in obj.items()}
            return obj
        result = trim(value)
        result['_display_truncated'] = True
        result['_stored_characters'] = original_size
        result['_continuation'] = 'Use events/sources/requirements with offset; canonical JSONL retains complete record.'
        if len(canonical(result)) <= budget:
            return result
    # Malformed/adversarially wide objects must not flood the context either.
    return {'id':value.get('id'), 'decision':value.get('decision'), 'approved':False,
            '_display_truncated':True, '_stored_characters':original_size,
            '_continuation':'Inspect a paged field or canonical JSONL outside model context.'}


def _card(record):
    return {'id': record['id'], 'kind': record['kind'], 'scope': record.get('scope','unknown'),
            'title': _clip(record['title'], 150), 'summary': _clip(record.get('summary',''),260),
            'verdict': record.get('verdict','unreviewed'),
            'review': record.get('review_status','imported_unreviewed'),
            'blockers': [x['code'] for x in record.get('blockers',[])][:4],
            'signals': record.get('signals',[])[:4],
            'reopen_policy': record.get('reopen',{}).get('policy','unreviewed')}


def _get(connection, identifier):
    rows = connection.execute('SELECT DISTINCT id FROM aliases WHERE alias=?',
                              (identifier.casefold(),)).fetchall()
    if len(rows) != 1:
        raise ValueError(('unknown record: ' if not rows else 'ambiguous alias: ') + identifier)
    row = connection.execute('SELECT payload FROM records WHERE id=?', (rows[0]['id'],)).fetchone()
    return json.loads(row['payload'])


def search(root, query='', limit=8, kind=None, blocker=None, offset=0, scope=None, change=None, signal=None):
    _limit(limit)
    if offset < 0:
        raise ValueError('offset must be nonnegative')
    if kind is not None and kind not in KINDS:
        raise ValueError('unknown kind')
    if scope is not None and scope not in SCOPES:
        raise ValueError('unknown scope')
    terms = re.findall(r'[^\W_]+', query.casefold(), flags=re.UNICODE)[:30]
    # Small bilingual navigation vocabulary, explicitly not a semantic classifier.
    for token, alternatives in {'seiten':['folios','pages'], 'bedeutung':['semantic','meaning'],
            'datenmangel':['capacity','insufficient'], 'zuordnung':['ownership','binding'],
            'prüfsumme':['checksum'], 'blatt':['folio'], 'duplikat':['duplicate']}.items():
        if token in terms:
            terms.extend(alternatives)
    parameters, where = [], []
    table = 'records r'
    order = 'r.id'
    if terms:
        table += ' JOIN search s ON s.id=r.id'
        where.append('search MATCH ?')
        parameters.append(' OR '.join('"' + t.replace('"','""') + '"' for t in terms))
        order = 'bm25(search,0,5,1),r.id'
    for column, value in [('kind',kind), ('scope',scope)]:
        if value:
            where.append('r.'+column+'=?'); parameters.append(value)
    for facet, value in [('blocker',blocker), ('change',change), ('signal',signal)]:
        if value:
            where.append('EXISTS (SELECT 1 FROM facets f WHERE f.id=r.id AND f.facet=? AND f.value=?)')
            parameters.extend([facet,value])
    clause = ' WHERE ' + ' AND '.join(where) if where else ''
    with _connect(root) as connection:
        count = connection.execute('SELECT count(*) FROM '+table+clause,parameters).fetchone()[0]
        rows = connection.execute('SELECT r.payload FROM '+table+clause+' ORDER BY '+order+' LIMIT ? OFFSET ?',
                                  parameters+[limit,offset]).fetchall()
    return {'results': [_card(json.loads(row['payload'])) for row in rows],
            'matched': count, 'limit': limit, 'offset': offset,
            'next_offset': offset+limit if count>offset+limit else None,
            'meaning': 'lexical navigation; no novelty, duplicate identity, or rerun approval'}


def show(root, identifier, event_limit=3):
    _limit(event_limit,10)
    with _connect(root) as connection:
        record = _get(connection,identifier)
    result = _card(record)
    result.update({'source_status': _clip(record.get('source_status',''),450),
                   'aliases': record.get('aliases',[])[:8],
                   'blockers': record.get('blockers',[])[:8],
                   'blocker_count': len(record.get('blockers',[])),
                   'reopen': record.get('reopen',{}),
                   'relations': record.get('relations',[])[:12],
                   'sources': record.get('sources',[])[:6],
                   'source_count': len(record.get('sources',[])),
                   'review_errors': record.get('review_errors',[]),
                   'assessment_basis': record.get('assessment_basis','unreviewed_import'),
                   'latest_review': record.get('latest_review',{}),
                   'event_count': len(record.get('events',[])),
                   'events': [{k:_clip(v,500) if isinstance(v,str) else v for k,v in row.items()}
                              for row in record.get('events',[])[-event_limit:]],
                   'legacy_reopen_text': _clip(record.get('legacy_reopen_text',''),1000),
                   'imported_report_pointer': record.get('imported_fields',{}).get('primary_report','')})
    return bounded_view(result)


def _paged_result(identifier, field, items, total, offset):
    selected = list(items)
    def packet():
        return {'id':identifier,'field':field,'total':total,'offset':offset,'items':selected,
                'next_offset':offset+len(selected) if total>offset+len(selected) else None}
    while len(selected)>1 and len(canonical(packet()))>12000:
        selected.pop()
    result = bounded_view(packet())
    if selected and not result.get('items'):
        # One unusually large object still has an addressable page; never skip it.
        entry = selected[0]
        result = packet()
        result['items'] = [{'_display_truncated':True,
            'id':entry.get('id') if isinstance(entry,dict) else None,
            'source_row':entry.get('source_row') if isinstance(entry,dict) else None,
            'stored_sha256':hashlib.sha256(canonical(entry).encode()).hexdigest()}]
        result['_display_truncated'] = True
    # Nested display clipping must never advance beyond the records actually shown.
    shown = len(result.get('items',[]))
    result['next_offset'] = offset+shown if total>offset+shown else None
    return result


def page_field(root, identifier, field, limit=8, offset=0):
    _limit(limit)
    if offset < 0: raise ValueError('offset must be nonnegative')
    with _connect(root) as connection:
        record = _get(connection,identifier)
        if field == 'reviews':
            rows = connection.execute('SELECT payload FROM reviews WHERE record_id=? ORDER BY sequence LIMIT ? OFFSET ?',
                                      (record['id'],limit,offset)).fetchall()
            total = connection.execute('SELECT count(*) FROM reviews WHERE record_id=?',(record['id'],)).fetchone()[0]
            return _paged_result(record['id'],field,[json.loads(r['payload']) for r in rows],total,offset)
        if field == 'relations':
            rows = connection.execute('SELECT source,target,kind,payload FROM relations WHERE source=? OR target=? ORDER BY source,target,kind LIMIT ? OFFSET ?',
                (record['id'],record['id'],limit,offset)).fetchall()
            total = connection.execute('SELECT count(*) FROM relations WHERE source=? OR target=?',
                                       (record['id'],record['id'])).fetchone()[0]
            items = [dict(json.loads(row['payload']),source=row['source'],target=row['target'],
                          direction='outgoing' if row['source']==record['id'] else 'incoming') for row in rows]
            return _paged_result(record['id'],field,items,total,offset)
    values = record.get('reopen',{}).get('all_of',[]) if field == 'requirements' else record.get(field,[])
    if field not in {'events','sources','requirements','relations'}:
        raise ValueError('unsupported paged field')
    return _paged_result(record['id'],field,values[offset:offset+limit],len(values),offset)


def duplicates(root, query='', proposal=None, limit=8):
    signature = design_fingerprint(proposal or {})
    exact = []
    if signature:
        with _connect(root) as connection:
            rows = connection.execute('SELECT payload FROM records WHERE signature=? LIMIT ?',
                                      (signature,_limit(limit))).fetchall()
            exact = [_card(json.loads(row['payload'])) for row in rows]
    result = search(root, query or canonical(proposal or {}), limit=limit)
    result['same_declared_design'] = exact
    result['decision'] = 'CANDIDATES_ONLY_NO_AUTOMATIC_MERGE'
    return result


def reconsider(root, identifier, changes, evidence):
    if not set(changes) <= CHANGES:
        raise ValueError('unknown change type')
    with _connect(root) as connection:
        record = _get(connection,identifier)
    policy = record.get('reopen',{}).get('policy','unreviewed')
    requirements = record.get('reopen',{}).get('all_of',[])
    missing_evidence = []
    for value in evidence:
        if not evidence_path(root,value).is_file():
            missing_evidence.append(value)
    missing_changes = sorted({x['change'] for x in requirements} - set(changes))
    if record.get('verdict') == 'stopped_by_user' or policy == 'user_stopped':
        decision = 'USER_STOP_NO_RERUN'
    elif record.get('verdict') == 'refuted_specific_model' or policy == 'do_not_repeat_same_model':
        decision = 'SAME_MODEL_NOT_REOPENED'
    elif record.get('review_status') != 'curated':
        decision = 'SOURCE_REVIEW_REQUIRED'
    elif policy != 'conditional' or not requirements:
        decision = 'NO_REVIEWED_REOPENING_CONTRACT'
    elif missing_changes or not evidence or missing_evidence:
        decision = 'CHANGE_PACKET_INCOMPLETE'
    else:
        decision = 'RECONSIDERATION_REVIEW_REQUIRED'
    return bounded_view({'id':record['id'], 'decision':decision, 'approved':False,
            'missing_change_types':missing_changes, 'missing_evidence_files':missing_evidence,
            'conditions':[dict(x,verification='UNVERIFIED_CONTENT') for x in requirements],
            'not_sufficient':record.get('reopen',{}).get('not_sufficient',[]),
            'reason':'File existence and change labels do not establish condition truth; inspect evidence, fixed gates and source scope.',
            'review_errors':record.get('review_errors',[])})


def check_registry(root):
    errors = source_freshness(root)
    try:
        records = _assemble(root)
        errors.extend(f'{r["id"]}: '+error for r in records.values()
                      for error in r.get('review_errors',[]))
    except (ValueError,KeyError) as exc:
        errors.append(str(exc)); records = {}
    return {'status':'PASS' if not errors else 'FAIL', 'errors':errors, 'records':len(records),
            'coverage':'schema, identities, relation consistency, source/review freshness; not semantic truth'}


def refresh(root):
    from tools.research_registry_import import import_records, import_manifest
    with writer(root):
        records = import_records(root)
        manifest = import_manifest(root)
        implementation = root / 'tools/research_registry_import.py'
        if implementation.is_file():
            manifest['importer_sha256'] = digest(implementation)
        write_snapshot(root,records,manifest)
        return build_index(root)


def add_idea(root, proposal):
    with writer(root):
        records = _base_records(root)
        serial = 1
        while f'IDEA{serial:06d}' in records:
            serial += 1
        identifier = proposal.get('id') or f'IDEA{serial:06d}'
        if identifier in records:
            raise ValueError('ID already exists; use a review instead of overwriting')
        if not proposal.get('title') or not proposal.get('summary'):
            raise ValueError('new idea needs title and summary')
        row = {'id':identifier,'kind':'idea','aliases':[],'title':proposal['title'],
               'summary':proposal['summary'],'source_status':'NEW_PROPOSAL','scope':proposal.get('scope','unknown'),
               'review_status':'imported_unreviewed','verdict':'untested','blockers':[],
               'reopen':{'policy':'unreviewed','all_of':[],'not_sufficient':[]},'relations':[],
               'sources':[],'events':[], 'design':proposal.get('design',{})}
        path = root / DIRECTORY / 'ideas.jsonl'
        rows = read_jsonl(path)
        write_jsonl(path,rows+[row])
        try:
            result = build_index(root)
        except Exception:
            write_jsonl(path,rows)
            raise
    return {'id':identifier,'status':'UNTESTED_PROPOSAL','records':result['records']}


def append_review(root, review):
    if not review.get('reason') or not review.get('reviewer'):
        raise ValueError('review needs reason and reviewer; history must remain attributable')
    with writer(root):
        records = _base_records(root)
        identifier = review['record_id']
        if identifier not in records:
            raise ValueError('unknown review ID')
        old = _review_rows(root).get(identifier)
        review = dict(review)
        review['previous_sha256'] = hashlib.sha256(canonical(old).encode()).hexdigest() if old else None
        review['basis_sha256'] = record_fingerprint(records[identifier])
        review['evidence_sha256'] = {}
        for relative in _evidence(review):
            p = evidence_path(root,relative)
            if not p.is_file():
                raise ValueError('missing review evidence: '+relative)
            review['evidence_sha256'][relative] = digest(p)
        path = root / DIRECTORY / 'curation.jsonl'
        previous = read_jsonl(path)
        write_jsonl(path,previous+[review])
        try:
            result = build_index(root)
        except Exception:
            write_jsonl(path,previous)
            raise
    return {'reviewed':identifier,'previous_review_preserved':old is not None,**result}


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(prog='vmanus-work ideas')
    commands = parser.add_subparsers(dest='command',required=True)
    commands.add_parser('refresh',help='reimport five metadata sources; keep authored ideas/reviews')
    commands.add_parser('bind-curation',help='explicit initial review binding; does not rebind existing reviews')
    commands.add_parser('check',help='source freshness and registry consistency')
    commands.add_parser('stats',help='compact coverage, counts are not independent hypotheses')
    search_parser = commands.add_parser('search',help='bounded offline full-text navigation')
    search_parser.add_argument('query',nargs='?',default='')
    search_parser.add_argument('--limit',type=int,default=8)
    search_parser.add_argument('--offset',type=int,default=0)
    search_parser.add_argument('--kind',choices=sorted(KINDS))
    search_parser.add_argument('--scope',choices=sorted(SCOPES))
    search_parser.add_argument('--blocker')
    search_parser.add_argument('--change',choices=sorted(CHANGES))
    search_parser.add_argument('--signal',help='lexical historical hint, not an adjudicated blocker')
    show_parser = commands.add_parser('show',help='one compact dossier, not the complete history')
    show_parser.add_argument('identifier')
    show_parser.add_argument('--events',type=int,default=3)
    for field in ('events','sources','requirements','relations','reviews'):
        field_parser = commands.add_parser(field,help='paged detail; never dump a complete registry')
        field_parser.add_argument('identifier')
        field_parser.add_argument('--limit',type=int,default=8)
        field_parser.add_argument('--offset',type=int,default=0)
    dupe = commands.add_parser('duplicates',help='candidate duplicates; never silently merge')
    dupe.add_argument('query',nargs='?',default='')
    dupe.add_argument('--proposal')
    dupe.add_argument('--limit',type=int,default=8)
    reconsider_parser = commands.add_parser('reconsider',help='match changed-input types to reviewed requirements')
    reconsider_parser.add_argument('identifier')
    reconsider_parser.add_argument('--change',action='append',choices=sorted(CHANGES),default=[])
    reconsider_parser.add_argument('--evidence',action='append',default=[])
    for command in ('add','review'):
        command_parser = commands.add_parser(command)
        command_parser.add_argument('file',help='repository-relative JSON object; review is append-only')
    args = parser.parse_args(argv)
    try:
        if args.command == 'refresh': result = refresh(root)
        elif args.command == 'bind-curation':
            with writer(root): result = bind_curations(root)
        elif args.command == 'check': result = check_registry(root)
        elif args.command == 'stats':
            with _connect(root) as connection:
                result = {'records':connection.execute('SELECT count(*) FROM records').fetchone()[0],
                          'groups':[dict(row) for row in connection.execute(
                              'SELECT kind,scope,review_status,count(*) AS n FROM records GROUP BY kind,scope,review_status')],
                          'warning':'record counts are not deduplicated semantic hypothesis counts'}
        elif args.command == 'search': result = search(root,args.query,args.limit,args.kind,args.blocker,args.offset,args.scope,args.change,args.signal)
        elif args.command == 'show': result = show(root,args.identifier,args.events)
        elif args.command in {'events','sources','requirements','relations','reviews'}:
            result = page_field(root,args.identifier,args.command,args.limit,args.offset)
        elif args.command == 'duplicates':
            proposal = json.loads(evidence_path(root,args.proposal).read_text()) if args.proposal else None
            result = duplicates(root,args.query,proposal,args.limit)
        elif args.command == 'reconsider': result = reconsider(root,args.identifier,args.change,args.evidence)
        elif args.command in {'add','review'}:
            value = json.loads(evidence_path(root,args.file).read_text())
            result = add_idea(root,value) if args.command == 'add' else append_review(root,value)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 1 if result.get('status') == 'FAIL' else 0
    except (ValueError,KeyError,OSError,sqlite3.Error) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    raise SystemExit(main())
