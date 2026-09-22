"""Independent GDT1034 certificate audit; no primary runner or matching solver.

--self-test reads source contracts and synthetic fixtures only.
--execute is reserved for the explicit post-publication authorization.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]

class Invalid(Exception):
    pass

def need(condition, message):
    if not condition:
        raise Invalid(message)

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def same(actual, expected, where='root'):
    need(type(actual) is type(expected), where+': type differs')
    if isinstance(expected, dict):
        need(actual.keys() == expected.keys(), where+': keys differ')
        for key in expected:
            same(actual[key], expected[key], where+'.'+str(key))
    elif isinstance(expected, list):
        need(len(actual) == len(expected), where+': length differs')
        for i,(a,e) in enumerate(zip(actual,expected)):
            same(a,e,where+f'[{i}]')
    else:
        need(actual == expected, where+': value differs '+repr(actual)+' != '+repr(expected))

def source_contracts():
    spec = load(EXP/'src/SPEC.json')
    entries = load(EXP/'src/ENTRIES.json')
    need(spec['experiment'] == 'GDT1034', 'experiment')
    need(set(entries) == {'A','B'} and len(entries['A']) == 67 and len(entries['B']) == 59, '126 complete entries')
    need([(r['section'],r['family'],r['groups']) for r in spec['records']] ==
         [('II','A',49),('III','A',46),('IV','B',55),('V','B',33)], 'fixed source sections')
    for record in spec['records']:
        need(digest(ROOT/record['path']) == record['sha256'], 'source hash '+record['section'])
    for family,rows in entries.items():
        for form,entry in rows.items():
            need(entry['form'] == form and all(isinstance(entry[k],str) and entry[k] for k in ('value','type','denotation')), 'incomplete entry '+family+':'+form)
    need(entries['A']['qoky']['denotation'].startswith('General typed negative existential'), 'current broadened NO required')
    return spec, entries

def entry_reconstruction(spec):
    docs = {r['section']:load(ROOT/r['path']) for r in spec['records']}
    A = {e['form']:dict(e) for e in docs['II']['lexicon']+docs['III']['new_lexicon']}
    change = docs['III']['explicit_new_branch_before_any_semantic_test']['changed_entry']
    for field in ('value','type','denotation'):
        A[change['form']][field] = change['new_'+field]
    B = {e['form']:dict(e) for e in docs['V']['frozen_parent_lexicon']+docs['V']['new_lexicon']}
    frozen = {e['form']:e for e in docs['IV']['lexicon']}
    inherited = {e['form']:e for e in docs['V']['frozen_parent_lexicon']}
    same(inherited,frozen,'literal38 inheritance')
    return {'A':A,'B':B}, docs

def allowed_relation(compatibility, entries):
    same(compatibility['entries'], entries, 'COMPATIBILITY complete entries')
    pairs = set()
    for pair in compatibility['allowed_pairs']:
        a,b = pair['A'],pair['B']
        need(a in entries['A'] and b in entries['B'], 'allowed pair unknown entry')
        need((a,b) not in pairs, 'duplicate allowed pair')
        need(isinstance(pair.get('reason'),str) and pair['reason'].strip(), 'missing edge reason')
        pairs.add((a,b))
    rows = compatibility['A_rows']
    need(len(rows) == len(entries['A']) and {r['form'] for r in rows} == set(entries['A']), 'complete A semantic row census')
    for row in rows:
        for field in ('form','value','type','denotation'):
            same(row[field],entries['A'][row['form']][field],'compatibility A row '+field)
        need(len(row['allowed_B_forms']) == len(set(row['allowed_B_forms'])), 'duplicate B form in A row')
        need(set(row['allowed_B_forms']) == {b for a,b in pairs if a == row['form']}, 'A row/edge relation differs')
        need(isinstance(row.get('reason'),str) and row['reason'].strip(), 'missing A row exclusion/allowance reason')
    return pairs


def audit_source_metadata(spec, entries):
    compatibility = load(EXP/'src/COMPATIBILITY.json')
    allowed_relation(compatibility,entries)
    receipt = compatibility['review_source']
    need(digest(ROOT/receipt['path']) == receipt['sha256'], 'semantic review receipt hash')
    reviewed = load(ROOT/receipt['path'])
    same(compatibility['A_rows'],reviewed['A_rows'],'semantic A review rows')
    same(compatibility['allowed_pairs'],reviewed['allowed_pairs'],'semantic edge receipt')
    need(len(reviewed['B_rows']) == 59 and {r['form'] for r in reviewed['B_rows']} == set(entries['B']), 'complete B review rows')
    for row in reviewed['B_rows']:
        for field in ('form','value','type','denotation'):
            same(row[field],entries['B'][row['form']][field],'B semantic review '+field)
    binding = spec['B_pool_source']
    need(digest(ROOT/binding['path']) == binding['sha256']
         and digest(EXP/'src/B_POOLS.json') == binding['sha256'], 'byte-exact B pool review binding')
    data = load(EXP/'src/B_POOLS.json')
    pools = data['pools']
    need(data['entry_coverage'] == 59 and data['pool_count'] == len(pools) == 46, 'B pool metadata coverage')
    need(len({p['id'] for p in pools}) == len(pools), 'pool IDs duplicate')
    members = [form for p in pools for form in p['forms']]
    need(len(members) == len(set(members)) == 59 and set(members) == set(entries['B']), 'B pool complete disjoint partition')
    by_form = {form:p for p in pools for form in p['forms']}
    for pool in pools:
        need(pool['forms'] and isinstance(pool.get('reason'),str) and pool['reason'].strip(), 'pool reason/member missing')
        need(set(pool['values']) == {entries['B'][f]['value'] for f in pool['forms']}, 'pool value metadata')
    value_rows = data['B_value_class_audit']
    values = {e['value'] for e in entries['B'].values()}
    need(len(value_rows) == data['base_value_class_count'] == len(values) == 51
         and {r['value'] for r in value_rows} == values, 'complete B value-class audit')
    for row in value_rows:
        forms = {f for f,e in entries['B'].items() if e['value'] == row['value']}
        need(set(row['forms']) == forms and len(row['forms']) == len(forms), 'value-class member audit')
        need(all(by_form[f]['id'] == row['pool_id'] for f in forms), 'value-class pool audit')
    source_binding = data['source_binding']
    need(source_binding['semantic_entries_path'] == receipt['path'], 'B pools semantic source pointer')
    expected = {r['path']:r['sha256'] for r in spec['records']}
    need({r['path']:r['sha256'] for r in source_binding['original_source_files']} == expected, 'B pool original source bindings')
    return pools

def source_nodes(spec, entries, docs):
    nodes = {'A':{},'B':{}}
    receipts = {}
    for record in spec['records']:
        section,family = record['section'],record['family']
        rows = docs[section][record['receipt']]
        need(len(rows) == record['groups'], 'complete source receipt length '+section)
        need([x['position'] for x in rows] == list(range(1,len(rows)+1)), 'receipt positions '+section)
        receipts[section] = rows
        for row in rows:
            form = row.get('form',row.get('raw_form'))
            need(form in entries[family], 'receipt unknown entry')
            need(row['value'] == entries[family][form]['value'], 'receipt value '+section)
            node = f"{section}:{row['position']:03d}"
            nodes[family][node] = dict(section=section,position=row['position'],entry=form,value=row['value'])
    need(len(nodes['A']) == 95 and len(nodes['B']) == 88, 'complete183 nodes')
    return nodes, receipts

def make_adjacency(nodes, allowed):
    return {a:sorted(b for b,brow in nodes['B'].items() if (arow['entry'],brow['entry']) in allowed)
            for a,arow in sorted(nodes['A'].items())}

def audit_certificate(A, B, adjacency, certificate):
    """Matching lower bound = complete vertex-cover upper bound, hence optimal."""
    aa,bb = set(A),set(B)
    need(set(adjacency) == aa, 'adjacency misses A nodes')
    for a,neighbors in adjacency.items():
        need(len(neighbors) == len(set(neighbors)) and set(neighbors) <= bb, 'adjacency duplicate/unknown B')
    pairs = certificate['pairs']
    used_a,used_b = set(),set()
    for pair in pairs:
        need(isinstance(pair,list) and len(pair) == 2, 'matching pair shape')
        a,b = pair
        need(a in aa and b in bb and b in adjacency[a], 'matching uses absent edge')
        need(a not in used_a and b not in used_b, 'matching reused node')
        used_a.add(a);used_b.add(b)
    ca,cb = certificate['cover_A'],certificate['cover_B']
    need(isinstance(ca,list) and isinstance(cb,list), 'cover lists')
    need(len(ca) == len(set(ca)) and len(cb) == len(set(cb)), 'cover duplicate')
    need(set(ca) <= aa and set(cb) <= bb, 'cover unknown node')
    need(all(a in ca or b in cb for a,neighbors in adjacency.items() for b in neighbors), 'uncovered allowed edge')
    need(type(certificate['size']) is int and certificate['size'] == len(pairs), 'certificate size')
    need(len(ca)+len(cb) == len(pairs), 'cover and matching sizes differ')
    return len(pairs)

def overlap_counts(A, B):
    need(all(type(v) is int and v > 0 for v in list(A.values())+list(B.values())), 'nonpositive word count')
    words = sorted(set(A)|set(B))
    return [dict(form=w,A=A.get(w,0),B=B.get(w,0),required_pairs=min(A.get(w,0),B.get(w,0))) for w in words]

def selector_guard(page, leaf):
    need(isinstance(page,str) and not page.startswith('f84') and page != 'f116v', 'forbidden page')
    match = re.fullmatch(r'f([0-9]+)[rv][0-9]*',page)
    need(match is not None and type(leaf) is int and leaf == int(match.group(1)), 'page/leaf disagreement')

def flatten_paragraph(paragraph, reader='ZL3b'):
    page,leaf,pid = paragraph['page'],paragraph['leaf'],paragraph['id']
    selector_guard(page,leaf)
    lines = paragraph['lines']
    need(lines and pid == page+'|'+lines[0]['locus']+'-'+lines[-1]['locus'], 'whole paragraph boundary ID')
    need(all(l['locus'].startswith(page+'.') for l in lines), 'line selector')
    raw,literal,flags = [],[],[]
    source_ids = []
    for line in lines:
        need(type(line['offset']) is int and line['offset'] == len(raw), 'line offset')
        words,ids = line['words'],line['source_ids']
        need(len(words) == len(ids) and all(isinstance(w,str) for w in words), 'word/ID shape')
        need(ids == [f"{reader}|{line['locus']}|G{i+1:03d}" for i in range(len(words))], 'source IDs')
        literal_line = line.get('anchor_eligible') is True
        # Missing/nonboolean flags remain nonliteral; no truthiness coercion.
        if literal_line:
            need(all(re.fullmatch('[a-z]+',w) for w in words), 'nonliteral spelling on literal line')
            literal.extend(words)
        raw.extend(words);source_ids.extend(ids)
        flags.append(dict(locus=line['locus'],anchor_eligible=line.get('anchor_eligible')))
    need(paragraph['groups'] == len(raw), 'whole paragraph group count')
    need(len(source_ids) == len(set(source_ids)), 'duplicate source IDs')
    return raw,literal,flags,source_ids


def reconstruct_scope(spec, packet, receipts):
    need(set(packet) == {'ZL3b','IT2a','RF1b'}, 'packet reader keys')
    by_id = {}
    for paragraph in packet['ZL3b']:
        need(paragraph['id'] not in by_id, 'duplicate ZL paragraph')
        by_id[paragraph['id']] = paragraph
    scope = []
    counters = {panel:{family:Counter() for family in ('A','B')}
                for panel in ('RAW_EXACT','LITERAL_LINES')}
    for record in spec['records']:
        section,family = record['section'],record['family']
        need(record['paragraph'] in by_id, 'missing complete fixed paragraph')
        paragraph = by_id[record['paragraph']]
        raw,literal,flags,source_ids = flatten_paragraph(paragraph)
        receipt = receipts[section]
        expected_words = [r.get('form',r.get('raw_form')) for r in receipt]
        same(raw,expected_words,section+' full receipt/raw identity')
        need(len(raw) == record['groups'], 'registered complete group count')
        positions = []
        for line in paragraph['lines']:
            for i,word in enumerate(line['words']):
                positions.append(dict(word=word,source_id=line['source_ids'][i],
                                      locus=line['locus'],anchor_eligible=line.get('anchor_eligible')))
        for row,pos in zip(receipt,positions):
            if 'source_id' in row:
                need(row['source_id'] == pos['source_id'], 'receipt source ID differs')
            if 'locus' in row:
                need(row['locus'] == pos['locus'], 'receipt locus differs')
        scope.append(dict(section=section,family=family,paragraph=paragraph['id'],
                          page=paragraph['page'],leaf=paragraph['leaf'],groups=paragraph['groups'],
                          positions=positions))
        counters['RAW_EXACT'][family].update(raw)
        counters['LITERAL_LINES'][family].update(literal)
    counts = {panel:overlap_counts(counter['A'],counter['B']) for panel,counter in counters.items()}
    need(len(counts['RAW_EXACT']) == 113, 'RAW complete union !=113')
    return scope,counts


def pool_capacities(pools, nodes, adjacency, B_entries):
    """Keep A neighbors as a UNION: several edges never multiply a slot."""
    need(len({p['id'] for p in pools}) == len(pools), 'duplicate pool IDs')
    members = [form for p in pools for form in p['forms']]
    need(len(members) == len(set(members)) and set(members) == set(B_entries), 'pools do not partition all B entries')
    capacities = []
    for pool in pools:
        need(isinstance(pool['id'],str) and pool['id'] and pool['forms'], 'empty pool')
        forms = set(pool['forms'])
        b_nodes = sorted(b for b,row in nodes['B'].items() if row['entry'] in forms)
        b_set = set(b_nodes)
        a_nodes = sorted(a for a,neighbors in adjacency.items() if b_set.intersection(neighbors))
        capacities.append(dict(id=pool['id'],forms=pool['forms'],A_nodes=a_nodes,B_nodes=b_nodes,
                               A_capacity=len(a_nodes),B_capacity=len(b_nodes)))
    return capacities


def word_domains(counts, capacities):
    panels = {}
    for panel,rows in counts.items():
        domains = []
        for row in rows:
            if not (row['A'] > 0 and row['B'] > 0):
                continue
            possible = [p['id'] for p in capacities
                        if row['A'] <= p['A_capacity'] and row['B'] <= p['B_capacity']]
            domains.append(dict(row,possible_pools=possible,
                                decision='NECESSARY_DOMAIN_NONEMPTY' if possible else 'EMPTY_NECESSARY_DOMAIN'))
        panels[panel] = domains
    return dict(pool_capacities=capacities,panels=panels)


def reconstruct_result(counts, nodes, allowed, capacity, domains):
    panels = {}
    for name,rows in counts.items():
        required = sum(r['required_pairs'] for r in rows)
        empty = sum(not r['possible_pools'] for r in domains['panels'][name])
        panels[name] = dict(A_positions=sum(r['A'] for r in rows),
                            B_positions=sum(r['B'] for r in rows),
                            shared_types=sum(r['A'] > 0 and r['B'] > 0 for r in rows),
                            required_pairs=required,source_capacity=capacity,
                            deficit=max(0,required-capacity),
                            empty_word_domains=empty,
                            decision='REFUTED_FIXED_SHARED_CODE' if required > capacity or empty else 'NO_DECISION')
    return dict(experiment='GDT1034',panels=panels,
                source_positions={f:len(nodes[f]) for f in ('A','B')},
                allowed_entry_pairs=len(allowed),B_pools=len(domains['pool_capacities']),confirmed_words=0,
                independent_meaning_capacity=0,significance_claim=False)


def check_locks(spec):
    lock = load(EXP/'PREREG_LOCK.json')
    files = lock['files']
    need(isinstance(files,dict), 'lock files map')
    required = {str(EXP.relative_to(ROOT)/p) for p in
                ('PREREGISTRATION.md','METHOD.md','src/SPEC.json','src/ENTRIES.json',
                 'src/COMPATIBILITY.json','src/B_POOLS.json','src/run.py','src/validate.py')}
    required.update(r['path'] for r in spec['records'])
    required.add(spec['packet']['path'])
    need(required <= set(files), 'lock omits bound input or code')
    for path,expected in files.items():
        need(digest(ROOT/path) == expected, 'lock mismatch '+path)
    return files


def execute(spec, entries):
    locks = check_locks(spec)
    pools = audit_source_metadata(spec,entries)
    independently_built,docs = entry_reconstruction(spec)
    same(entries,independently_built,'all126 original entries with current qoky')
    compatibility = load(EXP/'src/COMPATIBILITY.json')
    allowed = allowed_relation(compatibility,entries)
    nodes,receipts = source_nodes(spec,entries,docs)
    adjacency = make_adjacency(nodes,allowed)
    artifact = load(EXP/'artifacts/CERTIFICATE.json')
    need(set(artifact) == {'A','B','adjacency','certificate'}, 'certificate artifact keys')
    same(artifact['A'],nodes['A'],'all95 A nodes')
    same(artifact['B'],nodes['B'],'all88 B nodes')
    same(artifact['adjacency'],adjacency,'complete allowed occurrence graph')
    capacity = audit_certificate(nodes['A'],nodes['B'],adjacency,artifact['certificate'])
    need(len(pools) == 46, 'fixed46 B pools')
    capacities = pool_capacities(pools,nodes,adjacency,entries['B'])
    packet_path = ROOT/spec['packet']['path']
    need(digest(packet_path) == spec['packet']['sha256'], 'packet SHA')
    scope,counts = reconstruct_scope(spec,load(packet_path),receipts)
    domains = word_domains(counts,capacities)
    result = reconstruct_result(counts,nodes,allowed,capacity,domains)
    for name,value in [('SCOPE.json',scope),('ALL_WORD_COUNTS.json',counts),('WORD_DOMAINS.json',domains),('RESULT.json',result)]:
        same(load(EXP/'artifacts'/name),value,name)
    return dict(experiment='GDT1034',status='PASS',independent_implementation=True,
                primary_runner_read_or_imported=False,own_matching_solver_used=False,
                locks_verified=len(locks),validator_sha256=digest(Path(__file__)),
                source_entries={family:len(rows) for family,rows in entries.items()},
                source_nodes={family:len(rows) for family,rows in nodes.items()},
                allowed_occurrence_edges=sum(map(len,adjacency.values())),
                matching_size=capacity,vertex_cover_size=len(artifact['certificate']['cover_A'])+len(artifact['certificate']['cover_B']),
                certificate_proof='Feasible matching lower bound equals a vertex cover that covers every allowed edge; weak duality certifies maximum cardinality.',
                artifacts_compared=['CERTIFICATE.json','SCOPE.json','ALL_WORD_COUNTS.json','WORD_DOMAINS.json','RESULT.json'],
                reconstructed_result=result,synthetic=self_test(),
                claim_limit='Registered semantic compatibility is an input assumption. This validator checks complete reconstruction and the combinatorial certificate, not historical meanings or a translation.')

def self_test():
    passed=[]
    def check(A,B,adj,certificate,want=True):
        try:
            audit_certificate(A,B,adj,certificate)
        except Invalid:
            need(not want,'valid certificate rejected')
        else:
            need(want,'invalid certificate accepted')
    base=dict(pairs=[['a','x'],['b','y']],cover_A=['a','b'],cover_B=[],size=2)
    adj={'a':['x','y'],'b':['x','y'],'isolated':[]}
    check(adj,{'x','y','z'},adj,base)
    check(adj,{'x','y','z'},adj,dict(pairs=base['pairs'],cover_A=[],cover_B=['x','y'],size=2))
    check({'a'},{'x'},{'a':[]},dict(pairs=[],cover_A=[],cover_B=[],size=0))
    passed.extend(['perfect_cover_A','perfect_cover_B','empty_graph'])
    for bad in [dict(pairs=[['a','x'],['a','y']],cover_A=['a','b'],cover_B=[],size=2),
                dict(pairs=[['a','x'],['b','x']],cover_A=['a','b'],cover_B=[],size=2),
                dict(pairs=[['a','z']],cover_A=['a'],cover_B=[],size=1),
                dict(pairs=[['a','x']],cover_A=['a'],cover_B=[],size=1),
                dict(pairs=base['pairs'],cover_A=['a','a'],cover_B=[],size=2),
                dict(pairs=base['pairs'],cover_A=['a','b'],cover_B=[],size=1),
                dict(pairs=base['pairs'],cover_A=['a'],cover_B=['unknown'],size=2)]:
        check(adj,{'x','y','z'},adj,bad,False)
    passed.append('seven_invalid_certificates')
    # A one-edge greedy witness cannot match a two-node cover on this graph.
    check({'a','b'},{'x','y'},{'a':['x','y'],'b':['x']},dict(pairs=[['a','x']],cover_A=['a'],cover_B=[],size=1),False)
    passed.append('nonmaximum_greedy_rejected')
    rows=overlap_counts(Counter({'aliasone':3,'aliastwo':1,'left':4}),Counter({'aliasone':2,'aliastwo':4,'right':2}))
    need(sum(r['required_pairs'] for r in rows)==3 and len(rows)==4,'complete alias/min counts')
    passed.append('complete_min_counts_and_zeros')
    class Poison(dict):
        def __getitem__(self,key):
            if key == 'lines': raise AssertionError('forbidden payload accessed')
            return super().__getitem__(key)
    for page,leaf in [('f84r',84),('f84v',84),('f84r1',84),('f116v',116),('f1r',2)]:
        try: flatten_paragraph(Poison(page=page,leaf=leaf,id=page+'|irrelevant'))
        except Invalid: pass
        else: raise Invalid('selector poison was accepted')
    passed.append('selector_poison')
    for flag,expected in [(True,['a']),(False,[]),(None,[]),(1,[]),('true',[])]:
        p=dict(page='f1r',leaf=1,id='f1r|f1r.1-f1r.1',groups=1,
               lines=[dict(locus='f1r.1',offset=0,words=['a'],source_ids=['ZL3b|f1r.1|G001'],anchor_eligible=flag)])
        raw,literal,flags,ids=flatten_paragraph(p)
        need(raw==['a'] and literal==expected,'literal flag identity')
    passed.append('literal_flag_identity')
    # Complete occurrence graph replicates every source slot of each permitted entry.
    nodes={'A':{'II:001':dict(entry='a'),'II:002':dict(entry='a'),'III:001':dict(entry='c')},
           'B':{'IV:001':dict(entry='b'),'V:001':dict(entry='b'),'V:002':dict(entry='d')}}
    adjacency=make_adjacency(nodes,{('a','b')})
    need(adjacency=={'II:001':['IV:001','V:001'],'II:002':['IV:001','V:001'],'III:001':[]},'complete occurrence expansion')
    need(audit_certificate(nodes['A'],nodes['B'],adjacency,
                           dict(pairs=[['II:001','IV:001'],['II:002','V:001']],cover_A=['II:001','II:002'],cover_B=[],size=2))==2,'expanded occurrence certificate')
    passed.append('full_occurrence_expansion')
    counts={'RAW_EXACT':overlap_counts(Counter({'w':3}),Counter({'w':2})),
            'LITERAL_LINES':overlap_counts(Counter({'w':1}),Counter({'w':2}))}
    pools=[dict(id='B1',forms=['b']),dict(id='B2',forms=['d'])]
    caps=pool_capacities(pools,nodes,adjacency,{'b':{},'d':{}})
    need(caps[0]['A_capacity']==2 and caps[0]['B_capacity']==2,'pool A union versus repeated edges')
    domains=word_domains(counts,caps)
    result=reconstruct_result(counts,nodes,{('a','b')},1,domains)
    need(result['panels']['RAW_EXACT']['decision']=='REFUTED_FIXED_SHARED_CODE'
         and result['panels']['RAW_EXACT']['deficit']==1
         and result['panels']['LITERAL_LINES']['decision']=='NO_DECISION','panel threshold and weaker literal result')
    passed.append('decision_boundary_and_literal_relaxation')
    result=reconstruct_result(counts,nodes,{('a','b')},2,domains)
    need(result['panels']['RAW_EXACT']['deficit']==0
         and result['panels']['RAW_EXACT']['empty_word_domains']==1
         and result['panels']['RAW_EXACT']['decision']=='REFUTED_FIXED_SHARED_CODE'
         and domains['panels']['LITERAL_LINES'][0]['possible_pools']==['B1'], 'single-word domain independent falsifier')
    aliases=word_domains({'RAW_EXACT':overlap_counts(Counter({'x':1,'y':1,'only_a':4}),Counter({'x':2,'y':2}))},caps)
    need([r['form'] for r in aliases['panels']['RAW_EXACT']]==['x','y']
         and all(r['possible_pools']==['B1'] for r in aliases['panels']['RAW_EXACT']), 'all shared words/unlimited aliases')
    passed.extend(['single_word_domain_empty_without_matching_deficit','all_shared_alias_domains','A_neighbor_union'])
    return dict(status='PASS',checks=passed)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--self-test',action='store_true')
    p.add_argument('--execute',action='store_true')
    args=p.parse_args()
    spec,entries=source_contracts()
    if not args.execute:
        audit_source_metadata(spec,entries)
        print(json.dumps(self_test(),indent=2));return 0
    try:
        result=execute(spec,entries)
    except Exception as error:
        result=dict(experiment='GDT1034',status='FAIL',error_type=type(error).__name__,error=str(error),
                    primary_runner_read_or_imported=False,own_matching_solver_used=False)
        (EXP/'artifacts/VALIDATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(result,ensure_ascii=False,indent=2));return 1
    (EXP/'artifacts/VALIDATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0

if __name__ == '__main__':
    raise SystemExit(main())
