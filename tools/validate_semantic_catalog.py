"""Independent catalog/queue metadata validation; no semantic adjudication."""
import argparse,collections,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D='research_registry/decisions/'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def safe(root,relative):
    p=Path(relative)
    assert isinstance(relative,str) and not p.is_absolute() and '\\' not in relative and ':' not in relative
    assert all(x not in ['..','runtime','private'] and not x.startswith('.') for x in p.parts)
    path=root/p;assert path.resolve().is_relative_to(root) and path.is_file()
    return path

def validate(root=ROOT):
    cat=json.loads((root/(D+'semantic_catalog.json')).read_text());groups=cat['groups']
    records={json.loads(x)['id'] for x in (root/'research_registry/imported.jsonl').read_text().splitlines() if x}
    ids={g['id'] for g in groups};assert len(groups)==len(ids)==90
    sources=set();duplicates=[]
    for g in groups:
        assert g['member_ids'] and len(set(g['member_ids']))==len(g['member_ids']) and set(g['member_ids'])<=records
        assert g['ready_to_run'] is False and g['sources']
        assert set(g['sources'])==set(g['source_sha256'])
        for relative in g['sources']:
            assert sha(safe(root,relative))==g['source_sha256'][relative];sources.add(relative)
        if g['relationship']=='exact_duplicate':
            assert 'okaiin' in g['claim'] and any(x in g['claim'] for x in ['powder','ist/is'])
            assert set(g['member_ids'])<= {'GDT813','GDT814','GDT815'}
            duplicates.append(g['id'])
    assert len(duplicates)==2
    queue=json.loads((root/(D+'idea_queue_triage.json')).read_text());entries=queue['entries']
    assert len(entries)==82 and {e['id'] for e in entries}=={f'IP{i:03d}' for i in range(1,83)}
    for e in entries:
        assert e['assessment_basis']=='proposal_only' and e['ready'] is False and e['novelty']=='not_established'
        if e['canonical_group_association']:assert e['canonical_group_association'] in ids
        for relative in e['source_paths']:safe(root,relative);sources.add(relative)
    dispositions=dict(collections.Counter(e['disposition'] for e in entries))
    assert dispositions==dict(archived=17,conditional=32,source_review=7,raw_unreviewed=26)
    inputs=[D+'semantic_catalog.json',D+'idea_queue_triage.json','tools/semantic_catalog.py','tools/validate_semantic_catalog.py','research_registry/imported.jsonl']
    return dict(status='PASS',catalog_groups=90,
        single_existing_dossiers=sum(g['id'].startswith('DOSSIER-') for g in groups),
        targeted_comparison_groups=sum(not g['id'].startswith('DOSSIER-') for g in groups),
        basis_counts=dict(collections.Counter(g['assessment_basis'] for g in groups)),
        exact_duplicate_claim_components=2,exact_component_group_ids=sorted(duplicates),whole_experiments_merged=0,
        idea_triage_entries=82,dispositions=dispositions,ready_entries=0,imported_record_ids_checked=len(records),
        source_sha256={p:sha(root/p) for p in sorted(sources)},input_sha256={p:sha(root/p) for p in inputs},
        reproduction='python -m tools.validate_semantic_catalog --check',
        limitation='Reference/identity/source validation only; broad group association is not a scientific assessment of every member. Proposal dispositions establish no novelty, hypothesis truth or execution approval.')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    result=validate();path=ROOT/(D+'semantic_catalog_validation.json');raw=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.check:assert path.read_text()==raw,'Validation artifact stale'
    else:path.write_text(raw)
    print(json.dumps({k:v for k,v in result.items() if k not in ['source_sha256','input_sha256']},sort_keys=True))
if __name__=='__main__':main()
