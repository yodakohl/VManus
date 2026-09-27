#!/usr/bin/env python3
"""Bounded literal replay for IDEA581, independent of its author runner.
Reads only the frozen author packet and admitted GDT1042 guarded projection.
No semantic executor and no access to mixed/sealed target sources.
"""
from pathlib import Path
import csv, json, hashlib, collections, sys

ROOT = Path(__file__).resolve().parents[3]
DOS = ROOT / 'research_registry/proposals/laufenberg_f85r2_20260926'
PROJ = ROOT / 'experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/guarded_projection.tsv'
DRAFT = DOS / 'CONTEXT_SYNOPSIS_WHOLE_DRAFT.json'
CONTRACT = DOS / 'CONTEXT_SYNOPSIS_AUTHOR_CONTRACT.md'
REPORT = DOS / 'CONTEXT_SYNOPSIS_WHOLE_REPORT.md'
OUT = DOS / 'CONTEXT_SYNOPSIS_REPLAY_B.json'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read_tsv(path):
    with path.open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f, delimiter='\t'))
def failcheck(name, bad):
    checks[name] = not bool(bad)
    if bad: errors[name] = bad[:20] if isinstance(bad, list) else [bad]

checks, errors = {}, {}
d = json.loads(DRAFT.read_text(encoding='utf-8'))
p = read_tsv(PROJ)
a = d['all_occurrences']
source_keys = ['source_group_id','edition','locus','source_group_index','source_group_count','paragraph_start','paragraph_end','left_separator','right_separator','ivtff_group_raw']
failcheck('source_group_count_473', len(p) != 473 or len(a) != 473)
pmap = {r['source_group_id']:r for r in p}
amap = {r['source_group_id']:r for r in a}
failcheck('unique_source_ids', len(pmap)!=473 or len(amap)!=473)
failcheck('source_id_set_equal', set(pmap)^set(amap))
field_mismatches=[]
for sid, src in pmap.items():
    row=amap.get(sid)
    if row and any(str(row.get(k)) != src.get(k) for k in source_keys):
        field_mismatches.append({'id':sid,'fields':[k for k in source_keys if str(row.get(k)) != src.get(k)]})
failcheck('all_guarded_projection_fields_equal', field_mismatches)

# Recompute native order, line-relative position, scope block, and reader counts.
reader_counts=collections.Counter(r['edition'] for r in p)
unique_loci=sorted({r['locus'] for r in p}, key=lambda s:int(s.split('.')[-1]))
block_errors=[]; linepos_errors=[]
for row in a:
    locus_num=int(row['locus'].split('.')[-1])
    expected_block=('OUTSIDE' if locus_num in (1,24) else 'N' if locus_num<=6 else 'E' if locus_num<=11 else 'S' if locus_num<=17 else 'W')
    if row['block'] != expected_block: block_errors.append(row['source_group_id'])
    ls=row['left_separator']=='LINE_START'; le=row['right_separator']=='LINE_END'
    expected_pos='first_last' if ls and le else 'first' if ls else 'last' if le else 'interior'
    if row['within_line_position'] != expected_pos: linepos_errors.append({'id':row['source_group_id'],'expected':expected_pos,'actual':row['within_line_position']})
failcheck('scope_blocks_recomputed',block_errors)
failcheck('line_positions_recomputed_from_separators',linepos_errors)
failcheck('reader_row_counts', reader_counts != {'ZL3b':156,'IT2a':157,'RF1b':160})
failcheck('numeric_loci_1_to_24', unique_loci != [f'f85r2.{i}' for i in range(1,25)])

# Independently rebuild every exact-form occurrence index from the 473 source rows.
exact={}
for row in p: exact.setdefault(row['ivtff_group_raw'],[]).append(row['source_group_id'])
lex=d['lexicon']; index_errors=[]; binding_errors=[]
for form,entry in lex.items():
    expected=exact.get(form,[])
    if entry.get('all_exact_occurrences') != expected:
        index_errors.append({'form':form,'expected_count':len(expected),'actual_count':len(entry.get('all_exact_occurrences',[])),'expected_ids':expected,'actual_ids':entry.get('all_exact_occurrences',[])})
for row in a:
    entry=lex.get(row['ivtff_group_raw'])
    if entry:
        expected={'type':entry['type'],'value':entry['value'],'assignment_stage':entry['assignment_stage']}
        actual=row.get('binding') or {}
        if any(actual.get(k)!=v for k,v in expected.items()):
            binding_errors.append({'id':row['source_group_id'],'expected':expected,'actual':actual})
failcheck('exact_occurrence_indexes',index_errors)
failcheck('binding_matches_same_literal_value',binding_errors)

# Reconstruct the exact spans and verify the 66 derived ZL groups, with no overlap.
span_ids=[]; span_errors=[]; span_rows={}
for s in d['manual_derivation_spans']:
    loc=s['locus']; start=int(s['start_group']); end=int(s['end_group'])
    expected=[f"ZL3b|{loc}|G{i:03d}" for i in range(start,end+1)]
    if any(x not in pmap for x in expected): span_errors.append({'span':s['id'],'missing': [x for x in expected if x not in pmap]})
    for sid in expected:
        if sid in span_rows: span_errors.append({'overlap':sid,'spans':[span_rows[sid],s['id']]})
        span_rows[sid]=s['id']; span_ids.append(sid)
    if [int(pmap[x]['source_group_index']) for x in expected if x in pmap] != list(range(start,end+1)):
        span_errors.append({'nonconsecutive':s['id']})
failcheck('manual_spans_valid_nonoverlapping',span_errors)
actual_derived={r['source_group_id'] for r in a if r['status']=='DERIVED_IN_AUTHORED_ZL_SPAN'}
failcheck('derived_status_equals_span_union',actual_derived ^ set(span_ids))
failcheck('derived_scope_count_66', len(actual_derived)!=66)

# Check all-occurrence assignment/status bookkeeping without treating a gloss as truth.
status_errors=[]
for row in a:
    form=row['ivtff_group_raw']; is_assigned=form in lex; derived=row['source_group_id'] in actual_derived and row['edition']=='ZL3b'
    expected='DERIVED_IN_AUTHORED_ZL_SPAN' if derived else 'ASSIGNED_BUT_UNPARSED' if is_assigned else 'UNKNOWN_LITERAL'
    if row['status'] != expected: status_errors.append({'id':row['source_group_id'],'expected':expected,'actual':row['status']})
failcheck('assigned_unknown_derived_statuses',status_errors)
expected_unknown={r['ivtff_group_raw'] for r in p if r['edition']=='ZL3b'}-set(lex)
failcheck('unknown_ZL_type_set',set(d['unknown_ZL_types']) ^ expected_unknown)
failcheck('assigned_unique_ZL_form_count',len({r['ivtff_group_raw'] for r in p if r['edition']=='ZL3b' and r['ivtff_group_raw'] in lex})!=57)

# Directly show the key selected spans and literal sequences for manual audit.
def surface(locus,start,end):
    return [pmap[f'ZL3b|{locus}|G{i:03d}']['ivtff_group_raw'] for i in range(start,end+1)]
key_spans={
 'A1_OPEN_KIND':surface('f85r2.1',1,2), 'A1_OPEN_PAIR':surface('f85r2.1',3,4),
 'A1_OPEN_MODAL':surface('f85r2.1',5,5), 'A1_DIFFER':surface('f85r2.1',6,8),
 'A1_JUDGE_INPUT':surface('f85r2.1',9,10), 'A1_AGE':surface('f85r2.1',11,14),
 'A1_GOOD':surface('f85r2.1',15,18), 'A1_HARM':surface('f85r2.1',19,22),
 'A1_CLOSE_MODAL':surface('f85r2.1',23,23), 'E_OPEN_KIND':surface('f85r2.7',1,2),
 'E_OPEN_PAIR':surface('f85r2.7',3,4), 'E_OPEN_MODAL':surface('f85r2.7',5,5),
 'E_GOOD':surface('f85r2.8',1,4), 'E_CONJOIN_HEAD':surface('f85r2.8',6,6),
 'E_CYCLE_OPERANDS':surface('f85r2.9',1,2), 'E_HARM':surface('f85r2.9',3,6),
 'E_CLOSE_MODAL':surface('f85r2.11',3,3), 'E_END':surface('f85r2.11',4,4),
 'S_AGE':surface('f85r2.12',1,4)}
expected_key={
 'A1_OPEN_KIND':['odeedy','otedy'],'A1_OPEN_PAIR':['opaees','ar'],'A1_OPEN_MODAL':['chcthy'],
 'A1_DIFFER':['otchdy','otody','otar'],'A1_JUDGE_INPUT':['chepaiin','otodar'],
 'A1_AGE':['otodaiin','opaiin','otaiin','qopchas'],
 'A1_GOOD':['otchedy','olkaiin','odar','aloees'],'A1_HARM':['otchedy','qotedaiin','odar','octhody'],
 'A1_CLOSE_MODAL':['shedaiin'],'E_OPEN_KIND':['pchedeey','olkey'],'E_OPEN_PAIR':['qokedy','sheos'],
 'E_OPEN_MODAL':['fcheey'],'E_GOOD':['otchedy','chotey','qocthey','oteey'],
 'E_CONJOIN_HEAD':['oloqorain'],'E_CYCLE_OPERANDS':['daiin','qotaiin'],
 'E_HARM':['tchedy','otedy','qotchdy','chckhey'],'E_CLOSE_MODAL':['shedaiin'],
 'E_END':['chok{co}m'],'S_AGE':['otchs','shedor','chey','sorain']}
key_mismatches=[{'span':k,'expected':v,'actual':key_spans.get(k)} for k,v in expected_key.items() if key_spans.get(k)!=v]
failcheck('critical_derivation_surface_sequences',key_mismatches)

# Counts and AST/source-duty coverage asserted by the draft, checked for internal bookkeeping consistency.
counts=d['counts']; actual_unknown_groups=sum(1 for r in p if r['edition']=='ZL3b' and r['source_group_id'] not in actual_derived)
reported_unknown_types=len(expected_unknown)
internal=[]
for key,expected in [('total_assigned_ZL_types',57),('unknown_ZL_types',reported_unknown_types),('fully_owned_ZL_groups',66),('unowned_ZL_groups',90)]:
    actual={'total_assigned_ZL_types':len(set(lex)&{r['ivtff_group_raw'] for r in p if r['edition']=='ZL3b'}),'unknown_ZL_types':reported_unknown_types,'fully_owned_ZL_groups':len(actual_derived),'unowned_ZL_groups':actual_unknown_groups}[key]
    if counts.get(key)!=actual: internal.append({'count':key,'reported':counts.get(key),'recomputed':actual})
failcheck('headline_counts',internal)
failcheck('source_coverage_has_four_duties',len(d['source_coverage'])!=4)

result={
 'status':'PASS_LITERAL_REPLAY_WITH_MANUAL_CONTENT_LIMITS' if all(checks.values()) else 'FAIL_LITERAL_REPLAY',
 'inputs':{str(PROJ.relative_to(ROOT)):sha(PROJ),str(DRAFT.relative_to(ROOT)):sha(DRAFT),str(CONTRACT.relative_to(ROOT)):sha(CONTRACT),str(REPORT.relative_to(ROOT)):sha(REPORT)},
 'method':'Direct independent comparison of all_occurrences to GDT1042 guarded_projection.tsv; recomputed exact-form indexes, per-row assignments/statuses, reader/block/line-position counts, and derivation span union. No producer run.py imported/read; no semantic executor.',
 'checks':checks,'errors':errors,
 'recomputed':{'source_rows':len(p),'reader_rows':dict(reader_counts),'loci':unique_loci,'unique_source_ids':len(pmap),'ZL_derived_groups':len(actual_derived),'ZL_unowned_groups':actual_unknown_groups,'assigned_ZL_forms':57,'unknown_ZL_forms':reported_unknown_types,'manual_spans':len(d['manual_derivation_spans']),'ZL_source_coverage_duties':len(d['source_coverage'])},
 'critical_span_surfaces':key_spans,
 'manual_semantic_assessment':{
  'A1':'The spans instantiate one existential Kind and unordered sick/healthy Context pair, then one POSSIBILITY containing context-distinctness, input-needs-judgment, undirected age response-profile inequality across COLD/HEAT, and the two same-k GOOD/HARM Eval atoms; explicit shedaiin closes modal before three generic year/season/judgment atoms. The written AST aligns to the stated sequences and rules; all ontology/payloads remain authored guesses.',
  'E':'Fresh Kind and unequal TimeSituation-pair binders and possibility. First otchedy uses chotey/qocthey/oteey. The next temporal harm is via explicitly charged tchedy partial application, checked otedy/qotchdy/chckhey. oloqorain takes YEAR, qotaiin (cycle predicate) and Eval harm as written operands; it does not hide its arguments. Possibility closes before END_UNIT. Temporal contexts are distinct generic AtTime contexts, but no predicate explicitly locates them within the YEAR cycle; YEAR variation and the two-context evaluation are conjoined, not explicitly linked. This limits O2’s stronger reading.',
  'S12':'The four groups provide an unmodalized generic AGE_PAIR/COLD/HEAT response-profile inequality; remaining S duty content is unresolved.',
  'source_duties':'O1, O3, O4 are represented at the declared synopsis level with stated generic/undirected limitations. O2 has same-k opposite GOOD/HARM at distinct generic temporal contexts under joint possibility, plus independent CycleVaries(YEAR); the temporal-to-year link is not lexically/model-wise supplied. Thus source-inspired selected synopsis is partial as a target page but its four preselected duties are addressed unevenly; O2 claim should be worded as juxtaposed temporal-context contrast with year variation, not a fully bound within-year changing regimen.',
  'limits':'No semantics confirmed. Literal integrity passes do not validate any lexical assignment, typed derivation, plausibility of chosen synopsis, source interpretation, or meanings of unparsed rows. An independent reread of the 64-verse source text was not part of this replay; source cross-check is limited to the owned source result.'
 }
}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':result['status'],'checks':checks,'errors':errors,'recomputed':result['recomputed'],'output':str(OUT.relative_to(ROOT))},ensure_ascii=False,indent=2))
if not all(checks.values()): sys.exit(1)
