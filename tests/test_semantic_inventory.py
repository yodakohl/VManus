"""Synthetic full-history inclusion tests; source records are not independent ideas."""
import json
from pathlib import Path
import tempfile
import unittest
from tools import research_registry as registry
from tools import semantic_inventory as inventory
from tests.test_research_registry import record


class SemanticInventoryTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.root=Path(temp.name)

    def build(self, rows):
        registry.write_snapshot(self.root,rows)
        return inventory.build(self.root)

    def stored(self):
        return [json.loads(x) for x in (self.root/'research_registry/semantic_inventory.jsonl').read_text().splitlines() if x]

    def test_all_source_ids_including_empty_unknown_summary_are_retained(self):
        rows=[record('IP001',summary=''),record('GDT001',kind='attempt',summary=''),
              record('HIST:one',kind='history',title='Technical validation',summary=''),
              record('FAMILY:ONE',kind='family'),record('ANCHOR:ONE',kind='anchor')]
        self.build(rows);stored={x['id']:x for x in self.stored()}
        self.assertEqual(set(stored),{x['id'] for x in rows})
        for row in rows:
            self.assertEqual(stored[row['id']]['item_type'],row['kind'])
            self.assertEqual(stored[row['id']]['scope'],'unknown')
            self.assertEqual(stored[row['id']]['disposition'],'candidate_needs_scope_review')
        page=inventory.get_page(self.root)
        self.assertEqual({x['id'] for x in page['results']},set(stored))

    def test_source_events_and_spans_preserved_even_when_summary_empty(self):
        events=[dict(date='d',status='FAIL',summary='Earlier hypothesis',limitations='Not meaning',evidence='reports/one.md',source_row=7),
                dict(date='e',status='PASS',summary='Later conflicting hypothesis',limitations='Same source',evidence='reports/two.md',source_row=8)]
        sources=[dict(path='docs/synthetic.md',locator='line:7',sha256='fixture')]
        self.build([record('HIST:one',kind='history',summary='',events=events,sources=sources)])
        item=self.stored()[0]
        self.assertEqual(item['events'],events)
        self.assertEqual(item['sources'],sources)

    def test_identical_text_never_merges_distinct_source_records(self):
        self.build([record('IP001'),record('IP002')])
        self.assertEqual({x['id'] for x in self.stored()},{'IP001','IP002'})

    def test_ten_thousand_unknown_records_page_without_loss(self):
        self.build([record(f'HIST:{i:05d}',kind='history',summary='') for i in range(10000)])
        first=inventory.get_page(self.root)
        self.assertLessEqual(len(first['results']),8)
        ids=[];offset=0
        while offset is not None:
            page=inventory.get_page(self.root,limit=20,offset=offset)
            self.assertLessEqual(len(page['results']),20)
            ids.extend(x['id'] for x in page['results']);offset=page['next_offset']
        self.assertEqual(len(ids),10000)
        self.assertEqual(len(set(ids)),10000)

    def test_exact_extracted_statement_span_and_unresolved_remainder_survive(self):
        import hashlib
        registry.write_snapshot(self.root,[record('GDT001',kind='attempt')])
        folder=self.root/'research_registry/decisions';folder.mkdir()
        source=self.root/'reports/example.md';source.parent.mkdir();source.write_text('Heading\nOld candidate meaning\nOther unparsed prose\n')
        sha=hashlib.sha256(source.read_bytes()).hexdigest()
        rows=[dict(record_type='extraction_summary',count=2),
              dict(record_type='hypothesis_component',kind='explicit_mapping_candidate',record_id='COMPONENT:one',parent_gdt='GDT001',source_path='reports/example.md',source_sha256=sha,line_start=2,line_end=2,exact_statement='Old candidate meaning'),
              dict(record_type='unresolved_block',record_id='COMPONENT:remainder',parent_gdt='GDT001',source_path='reports/example.md',source_sha256=sha,line_start=1,line_end=3,reason='Unreviewed remainder')]
        (folder/'legacy_semantic_components.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
        inventory.build(self.root);stored={r['id']:r for r in self.stored()}
        self.assertEqual(set(stored),{'GDT001','COMPONENT:one','COMPONENT:remainder'})
        self.assertEqual(stored['COMPONENT:one']['statement'],'Old candidate meaning')
        self.assertEqual(stored['COMPONENT:one']['source_record_id'],'GDT001')
        self.assertEqual(stored['COMPONENT:one']['sources'][0]['locator'],'line:2')
        self.assertEqual(stored['COMPONENT:one']['extraction']['line_end'],2)
        self.assertEqual(stored['COMPONENT:remainder']['item_type'],'unresolved_source_block')
        self.assertTrue(all(r['ready'] is False for r in stored.values()))
        source.write_text('Changed evidence\n')
        with self.assertRaises(ValueError):inventory.get_page(self.root)

    def test_manifest_unresolved_source_pointer_is_an_operational_item(self):
        import hashlib
        registry.write_snapshot(self.root,[record('IP001')])
        folder=self.root/'research_registry/decisions';folder.mkdir()
        pointer=dict(path='reports/unparsed.md',reason='No extracted card; requires review')
        manifest=dict(record_type='extraction_manifest',unresolved_source_pointers=[pointer])
        (folder/'legacy_proposal_extraction.jsonl').write_text(json.dumps(manifest)+'\n')
        inventory.build(self.root);rows=self.stored()
        identifier='LEGACY_SOURCE:'+hashlib.sha256(registry.canonical(pointer).encode()).hexdigest()[:24]
        indexed={r['id']:r for r in rows}
        self.assertEqual(set(indexed),{'IP001',identifier})
        self.assertEqual(indexed[identifier]['extraction']['path'],pointer['path'])
        self.assertEqual(indexed[identifier]['extraction']['reason'],pointer['reason'])
        self.assertIs(indexed[identifier]['ready'],False)

    def test_unextracted_safe_prose_is_searchable_without_fence_or_sealed_payload(self):
        import hashlib
        registry.write_snapshot(self.root,[record('IP001')])
        folder=self.root/'research_registry/decisions';folder.mkdir()
        source=self.root/'reports/old.md';source.parent.mkdir()
        source.write_text('An old lexicon conjecture mentions unobtainium.\n\n```text\nfencedonlytoken\n```\n\nf84r forbiddenonlytoken\nContinuation of that excluded block.\n')
        pointer=dict(path='reports/old.md',reason='Unparsed prose')
        manifest=dict(record_type='extraction_manifest',sources=[dict(path='reports/old.md',sha256=hashlib.sha256(source.read_bytes()).hexdigest())],unresolved_source_pointers=[pointer])
        (folder/'legacy_proposal_extraction.jsonl').write_text(json.dumps(manifest)+'\n')
        inventory.build(self.root)
        found=inventory.get_page(self.root,query='unobtainium')
        self.assertEqual(found['matched'],1)
        self.assertIn('unobtainium',found['results'][0]['statement_preview'])
        self.assertEqual(inventory.get_page(self.root,query='fencedonlytoken')['matched'],0)
        self.assertEqual(inventory.get_page(self.root,query='forbiddenonlytoken')['matched'],0)
        page=inventory.source_page(self.root,found['results'][0]['id'])
        self.assertEqual(len(page['source_blocks']),1)

    def test_local_overlay_visible_without_changing_public_inventory(self):
        import hashlib
        self.build([record('IP001')])
        public=(self.root/inventory.DATA).read_bytes()
        source=self.root/'local_proposal.md';source.write_text('A local hypothesis')
        overlay=self.root/inventory.LOCAL;overlay.parent.mkdir(exist_ok=True)
        row=dict(record_type='authored_card',id='LOCAL:one',candidate_type='explicit_proposal',path='local_proposal.md',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),line=1,title='Local idea',hypothesis='A local hypothesis')
        overlay.write_text(json.dumps(row)+'\n')
        page=inventory.get_page(self.root)
        self.assertEqual({r['id'] for r in page['results']},{'IP001','LOCAL:one'})
        self.assertEqual((self.root/inventory.DATA).read_bytes(),public)
        source.write_text('Changed local source')
        with self.assertRaises(ValueError):inventory.get_page(self.root)

    def test_invalid_page_limits_rejected(self):
        self.build([record('IP001')])
        for limit in [0,21,10000]:
            with self.subTest(limit=limit),self.assertRaises(ValueError):inventory.get_page(self.root,limit=limit)


def audit_actual(root):
    """Independent coverage against canonical metadata/extractions, not importer."""
    import hashlib
    from collections import Counter
    base=[]
    for name in ['imported.jsonl','ideas.jsonl']:
        p=root/'research_registry'/name
        if p.exists():base.extend(json.loads(x) for x in p.read_text().splitlines() if x)
    items=[json.loads(x) for x in (root/'research_registry/semantic_inventory.jsonl').read_text().splitlines() if x]
    indexed={x['id']:x for x in items};assert len(indexed)==len(items)
    expected={r['id'] for r in base};assert len(expected)==len(base)
    for row in base:
        target=indexed[row['id']]
        assert target['item_type']==row['kind']
        assert target['events']==row.get('events',[]) and target['sources']==row.get('sources',[])
        assert target['ready'] is False
    extraction_counts=Counter();metadata_rows=0
    for name in ['legacy_proposal_extraction.jsonl','legacy_semantic_components.jsonl']:
        for line in (root/'research_registry/decisions'/name).read_text().splitlines():
            if not line:continue
            row=json.loads(line)
            if row.get('record_type')=='extraction_manifest':
                for pointer in row.get('unresolved_source_pointers',[]):
                    canonical=json.dumps(pointer,ensure_ascii=False,sort_keys=True,separators=(',',':'))
                    identifier='LEGACY_SOURCE:'+hashlib.sha256(canonical.encode()).hexdigest()[:24]
                    assert identifier not in expected
                    expected.add(identifier);target=indexed[identifier]
                    assert target['ready'] is False
                    assert target['extraction']['record_type']=='unresolved_source_pointer'
                    assert all(target['extraction'][k]==v for k,v in pointer.items())
                    extraction_counts['manifest_unresolved_source_pointers']+=1
            if row.get('record_type') in ['extraction_manifest','extraction_summary','source_coverage','manifest','coverage']:
                metadata_rows+=1;continue
            identifier=row.get('id',row.get('record_id'))
            assert identifier and identifier not in expected
            expected.add(identifier);target=indexed[identifier]
            assert target['extraction']==row and target['ready'] is False
            if 'exact_statement' in row:assert target['statement']==row['exact_statement']
            elif 'hypothesis' in row:assert target['statement']==row['hypothesis']
            if 'line_start' in row:assert target['sources'][0]['locator']==f"line:{row['line_start']}"
            extraction_counts[name]+=1
    assert set(indexed)==expected
    manifest=json.loads((root/'research_registry/INVENTORY_MANIFEST.json').read_text())
    assert manifest['items']==len(items) and manifest['source_records']==len(base)
    assert manifest['inventory_sha256']==hashlib.sha256((root/'research_registry/semantic_inventory.jsonl').read_bytes()).hexdigest()
    for relative,sha in {**manifest['input_sha256'],**manifest['external_source_sha256']}.items():
        path=root/relative
        assert not Path(relative).is_absolute() and '..' not in Path(relative).parts and path.resolve().is_relative_to(root)
        assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
    return dict(status='PASS',source_records_exact=len(base),ledger_events_exact=sum(len(r.get('events',[])) for r in base),
                operational_items=len(items),extraction_items_by_input=dict(extraction_counts),coverage_metadata_rows_not_mislabeled_items=metadata_rows,
                item_types=dict(Counter(x['item_type'] for x in items)),ready_entries=sum(x['ready'] is True for x in items),
                empty_summary_source_records_retained=sum(not r.get('summary') for r in base),
                statement_and_source_spans_preserved=True,source_hashes_match=True,
                unique_semantic_ideas=None,synthetic_tests=9,
                validator_source='tests/test_semantic_inventory.py',
                limitation='Full coverage of current registered metadata and retained extraction records only. Candidate, source excerpt, unresolved block and historical record are distinct units, not independently deduplicated ideas; omitted or unavailable historical source material is not reconstructed.')


if __name__=='__main__':unittest.main()
