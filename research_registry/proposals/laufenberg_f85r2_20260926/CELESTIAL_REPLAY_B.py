#!/usr/bin/env python3
"""Independent literal/coverage replay for frozen RAW569; no producer runner import."""
import csv, hashlib, json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DRAFT = ROOT / 'research_registry/proposals/laufenberg_f85r2_20260926/CELESTIAL_AUTHOR_DRAFT.json'
PROJ = ROOT / 'experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/guarded_projection.tsv'
OUT = ROOT / 'research_registry/proposals/laufenberg_f85r2_20260926/CELESTIAL_REPLAY_B.json'
NATIVE = ROOT / 'experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/native_groups.tsv'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

d = json.loads(DRAFT.read_text())
with PROJ.open(newline='') as f:
    rows = list(csv.DictReader(f, delimiter='\t'))
assert len(rows) == 473, len(rows)
with NATIVE.open(newline='') as f:
    native_rows = list(csv.DictReader(f, delimiter='\t'))
assert len(native_rows) == 473, len(native_rows)
native_byid = {r['source_group_id']: r for r in native_rows}
assert len(native_byid) == len(native_rows)
# Verify that the source-scope hash in the author's draft refers to the native
# row projection, while the protected selector-query output has its own hash.
native_transform_errors=[]
for r in rows:
    n=native_byid.get(r['source_group_id'])
    if n is None:
        native_transform_errors.append((r['source_group_id'],'missing_native_row')); continue
    for a,b in [('edition','edition'),('locus','locus'),('source_group_index','source_group_index'),('source_group_count','source_group_count'),('paragraph_start','paragraph_start'),('paragraph_end','paragraph_end'),('left_separator','left_separator'),('right_separator','right_separator'),('ivtff_group_raw','ivtff_group_raw')]:
        if str(r[a]) != str(n[b]): native_transform_errors.append((r['source_group_id'],a,r[a],n[b]))
assert not native_transform_errors, native_transform_errors[:5]
# The preregistered four-block unit occupies loci .2 through .23 (inclusive).
selected_loci = {f'f85r2.{i}' for i in range(2,24)}
sel = [r for r in rows if r['locus'] in selected_loci]
outside = [r for r in rows if r['locus'] not in selected_loci]
counts = Counter(r['edition'] for r in sel)
assert counts == Counter({'ZL3b':108,'IT2a':107,'RF1b':109}), counts
assert len(sel) == 324
lex = d['lexicon']
# Rebuild target rows from the owned projection and fixed exact-form lexicon, not annotated producer rows.
# Compare each edition's frozen row packet against literal source columns and exact-form status.
replay_rows = {'ZL3b':d['all_primary_occurrences']}
for packet in d['alternate_rows_and_gaps']:
    replay_rows[packet['edition']] = packet['rows']
row_checks = {}
for edition in ('ZL3b','IT2a','RF1b'):
    observed = [x for x in replay_rows[edition] if x.get('block') in ('N','E','S','W')]
    source = [r for r in sel if r['edition']==edition]
    assert len(observed)==len(source), (edition,len(observed),len(source))
    byid={x['source_group_id']:x for x in observed}
    assert set(byid)=={r['source_group_id'] for r in source}, edition
    errors=[]
    for r in source:
        x=byid[r['source_group_id']]
        for field in ('edition','locus','source_group_index','source_group_count','left_separator','right_separator','ivtff_group_raw'):
            if str(x.get(field)) != str(r[field]): errors.append((r['source_group_id'],field,x.get(field),r[field]))
        v=lex.get(r['ivtff_group_raw'])
        if edition=='ZL3b':
            if x.get('assigned_value') != (v.get('value') if v else None): errors.append((r['source_group_id'],'value',x.get('assigned_value'),v and v.get('value')))
        else:
            status=x.get('lexical_status')
            if v:
                if status!='same literal assigned form' or x.get('assigned_value')!=v.get('value'):
                    errors.append((r['source_group_id'],'lex_status/value',status,x.get('assigned_value'),v.get('value')))
            else:
                if status!='UNASSIGNED_LITERAL_VARIANT' or x.get('assigned_value') is not None:
                    errors.append((r['source_group_id'],'gap',status,x.get('assigned_value')))
    row_checks[edition]={'source_rows':len(source),'replayed_rows':len(observed),'mismatches':errors}
    assert not errors, (edition,errors[:5])
# Confirm the 23 authored clause spans partition the full primary ZL packet once.
primary_ids={x['source_group_id'] for x in d['all_primary_occurrences']}
clause_ids=[rid for clause in d['clauses'] for rid in clause.get('group_ids',[])]
clause_coverage={'clause_count':len(d['clauses']),'listed_ids':len(clause_ids),
                 'unique_ids':len(set(clause_ids)),
                 'duplicates':[rid for rid,n in Counter(clause_ids).items() if n>1],
                 'missing':sorted(primary_ids-set(clause_ids)),
                 'extra':sorted(set(clause_ids)-primary_ids)}
assert len(d['clauses'])==23 and len(clause_ids)==108 and len(set(clause_ids))==108
assert set(clause_ids)==primary_ids and not clause_coverage['duplicates']
# Verify every per-lexicon occurrence ID against exact raw data, across whole 473-row projection.
all_byid={r['source_group_id']:r for r in rows}
lex_occurrence_errors=[]
for form, entry in lex.items():
    listed=entry.get('all_owned_occurrence_ids',[])
    expected_ids={r['source_group_id'] for r in rows if r['ivtff_group_raw']==form}
    if set(listed)!=expected_ids:
        lex_occurrence_errors.append((form,'incomplete_or_extra_ids',len(listed),len(expected_ids)))
    for rid in listed:
        r=all_byid.get(rid)
        if r is None or r['ivtff_group_raw']!=form:
            lex_occurrence_errors.append((form,rid,None if r is None else r['ivtff_group_raw']))
assert not lex_occurrence_errors, lex_occurrence_errors[:10]
# Rebuild the outside extension-obligation table as every outside row whose exact whole form is in lexicon.
expected_out=[]
for r in outside:
    v=lex.get(r['ivtff_group_raw'])
    if v:
        expected_out.append((r['source_group_id'],r['ivtff_group_raw'],v['value']))
ob=d['outside_assigned_form_obligations']
actual_out=[(x['source_group_id'],x['ivtff_group_raw'],x['assigned_value']) for x in ob]
assert len(expected_out)==47 and len(actual_out)==47, (len(expected_out),len(actual_out))
assert Counter(expected_out)==Counter(actual_out)
by_edition=Counter(all_byid[rid]['edition'] for rid,_,_ in expected_out)
assert by_edition==Counter({'ZL3b':14,'IT2a':18,'RF1b':15}), by_edition
# Build exact literal alternatives and all group count receipts.
alt_gaps={}
for edition in ('IT2a','RF1b'):
    packet=next(x for x in d['alternate_rows_and_gaps'] if x['edition']==edition)
    alt_gaps[edition]=[{'id':x['source_group_id'],'raw':x['ivtff_group_raw'],'separator_before':x['left_separator'],'separator_after':x['right_separator']}
                       for x in packet['rows'] if x.get('lexical_status')=='UNASSIGNED_LITERAL_VARIANT']
result={
 'status':'PASS_LITERAL_REPLAY_ONLY',
 'draft_sha256':sha(DRAFT),'projection_sha256':sha(PROJ),
 'projection_rows':len(rows),'selected_rows':len(sel),'outside_rows':len(outside),
 'selector_guarded_projection_sha256':sha(PROJ),
 'native_groups_projection_sha256':sha(NATIVE),
 'draft_projection_hash_matches_native_groups':d['target_scope']['projection_sha256']==sha(NATIVE),
 'projection_to_native_groups_field_check':{'rows':len(native_rows),'mismatches':native_transform_errors},
 'selected_counts_by_reader':dict(counts),
 'selected_row_comparisons':row_checks,
 'authored_clause_partition':clause_coverage,
 'exact_lexicon_occurrence_ids_checked':sum(len(v.get('all_owned_occurrence_ids',[])) for v in lex.values()),
 'lexicon_occurrence_id_mismatches':lex_occurrence_errors,
 'outside_assigned_obligations_rebuilt':len(expected_out),
 'outside_assigned_by_reader':dict(by_edition),
 'unassigned_variants':alt_gaps,
 'limits':'Literal and metadata bookkeeping only. Does not prove a grammatical parse, meaning, or source compatibility.'
}
OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(result,indent=2,ensure_ascii=False))
