"""Deterministic full imported-record coverage; links never imply semantic merging.

Reads registry metadata locally and emits only bounded summary plus a navigational
TSV. No report body, transcription or image is read. Exact shared report strings
are navigation evidence only; absent links remain unresolved.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json
from collections import Counter,defaultdict
from pathlib import Path
from tools import research_registry as registry
ROOT=Path(__file__).resolve().parents[1]
DIRECTORY='research_registry/decisions'
TABLE='full_history_coverage.tsv'

def compact(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def references(record):
    fields=record.get('imported_fields',{})
    values=[fields.get(k,'') for k in ['primary_report','archive_pointer','evidence_path']]
    values.extend(event.get('evidence','') for event in record.get('events',[]))
    # Exact literal path strings only, no fuzzy matching or inferred folder repair.
    return {v for v in values if isinstance(v,str) and registry.safe_relative_path(v)}

def build(root):
    imported=registry.read_jsonl(root/'research_registry/imported.jsonl')
    assert len({r['id'] for r in imported})==len(imported)
    assembled=registry._assemble(root)
    ids={r['id'] for r in imported}
    family_sources=defaultdict(set)
    for record in imported:
        if record['kind']=='family':
            for path in references(record):family_sources[path].add(record['id'])
    incoming=defaultdict(list)
    for record in assembled.values():
        for link in record.get('relations',[]):
            incoming[link['target']].append(dict(source=record['id'],type=link['type']))
    catalog_path=root/'research_registry/decisions/semantic_catalog.json'
    group_membership=defaultdict(list);catalog_counts=Counter()
    if catalog_path.exists():
        from tools.semantic_catalog import validate_catalog
        catalog=json.loads(catalog_path.read_text());validate_catalog(catalog,root)
        for group in catalog['groups']:
            if group['id'].startswith('DOSSIER-'):category='SINGLE_EXISTING_DOSSIER'
            elif group['assessment_basis'] in ['registry_summary_only','registry_pointer_identity_only']:category='INHERITED_COMPARISON_NAVIGATION'
            else:category='TARGETED_REVIEWED_COMPARISON_NOT_BLANKET_MEMBER_REVIEW'
            catalog_counts[category]+=1
            for member in group['member_ids']:
                group_membership[member].append(dict(group_id=group['id'],category=category,relationship=group['relationship'],basis=group['assessment_basis']))
    table=[];counts=Counter();relation_types=Counter();review_bases=Counter();event_total=0
    for original in sorted(imported,key=lambda r:r['id']):
        identifier=original['id'];record=assembled[identifier]
        links=sorted([dict(type=l['type'],target=l['target']) for l in record.get('relations',[])],key=compact)
        explicit_families=sorted({l['target'] for l in links if assembled[l['target']]['kind']=='family'})
        shared=[dict(family=f,path=p) for p in sorted(references(original)) for f in sorted(family_sources[p]) if f!=identifier]
        inward=sorted(incoming[identifier],key=compact)
        if original['kind']=='family':coverage='FAMILY_RECORD_NOT_MEMBER_DEDUP'
        elif explicit_families:coverage='EXPLICIT_FAMILY_LINK_NOT_DUPLICATE_DECISION'
        elif links or inward:coverage='EXPLICIT_RELATION_NAVIGATION_ONLY'
        elif shared:coverage='EXACT_SHARED_REPORT_NAVIGATION_ONLY'
        else:coverage='UNRESOLVED_NO_EXPLICIT_LINK'
        events=len(original.get('events',[]));event_total+=events;counts[coverage]+=1
        relation_types.update(l['type'] for l in links)
        basis=record.get('assessment_basis','unreviewed_import');review_bases[basis]+=1
        table.append(dict(record_id=identifier,kind=original['kind'],ledger_event_count=events,
            scope=record.get('scope','unknown'),assessment_basis=basis,
            review_status=record.get('review_status','imported_unreviewed'),coverage=coverage,
            explicit_links=compact(links),incoming_links=compact(inward),
            explicit_family_targets=compact(explicit_families),
            exact_shared_report_family_navigation=compact(shared),
            catalog_associations=compact(sorted(group_membership[identifier],key=compact)),
            semantic_dedup='NOT_ESTABLISHED_BY_THIS_AUDIT'))
    buffer=io.StringIO(newline='');writer=csv.DictWriter(buffer,fieldnames=list(table[0]),delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(table)
    raw=buffer.getvalue()
    source_paths=['research_registry/imported.jsonl','research_registry/curation.jsonl','research_registry/SOURCE_MANIFEST.json','tools/research_priority_coverage.py','tools/research_registry.py']
    if (root/'research_registry/ideas.jsonl').exists():source_paths.append('research_registry/ideas.jsonl')
    if catalog_path.exists():source_paths+=['research_registry/decisions/semantic_catalog.json','tools/semantic_catalog.py']
    report=dict(status='COVERAGE_ENUMERATED_SEMANTIC_DEDUP_NOT_ESTABLISHED',
        imported_records=len(imported),covered_rows=len(table),ledger_events=event_total,
        kinds=dict(Counter(r['kind'] for r in imported)),coverage_counts=dict(counts),
        outgoing_explicit_relation_types=dict(relation_types),assessment_bases=dict(review_bases),
        unique_hypotheses=None,semantic_duplicate_groups=None,
        catalog_group_categories=dict(catalog_counts),
        imported_records_with_catalog_association=sum(bool(group_membership[i]) for i in ids),
        imported_records_with_targeted_group_association=sum(any(g['category']=='TARGETED_REVIEWED_COMPARISON_NOT_BLANKET_MEMBER_REVIEW' for g in group_membership[i]) for i in ids),
        imported_records_without_catalog_association=sum(not group_membership[i] for i in ids),
        table=f'{DIRECTORY}/{TABLE}',table_sha256=hashlib.sha256(raw.encode()).hexdigest(),
        input_sha256={p:digest(root/p) for p in source_paths},
        source_freshness_errors=registry.source_freshness(root),
        limitations=[
          'Ledger events, attempts, historical keys, proposals and families are different units; no count is a count of unique meaning hypotheses.',
          'Every imported record gets a row; authored ideas can supply incoming links but are not extra imported rows.',
          'Existing duplicate_of links are displayed declarations, not independently adjudicated here.',
          'same_experiment_reference links preserve separate records and denote experiment navigation only.',
          'Explicit family links retain their declared relation type; related_to does not imply duplicate_of.',
          'Exact shared report paths are navigation hints, not family membership or semantic equivalence.',
          'Family scope can include structural, methodological and acquisition work; family records are not all semantic ideas.',
          'Missing links remain unresolved; this audit neither merges records nor approves reopening.',
          'No lexical candidate generation, report-body reading, manuscript data or images.'])
    return raw,report

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    raw,report=build(ROOT);folder=ROOT/DIRECTORY;folder.mkdir(exist_ok=True)
    payload=json.dumps(report,sort_keys=True,indent=2)+'\n'
    if args.check:
        assert (folder/TABLE).read_text()==raw
        assert (folder/'coverage_audit.json').read_text()==payload
    else:
        (folder/TABLE).write_text(raw);(folder/'coverage_audit.json').write_text(payload)
    print(compact({k:report[k] for k in ['status','imported_records','covered_rows','ledger_events','coverage_counts','outgoing_explicit_relation_types','source_freshness_errors']}))
if __name__=='__main__':main()
