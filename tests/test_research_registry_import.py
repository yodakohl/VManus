"""Independent metadata-import preservation checks; never invokes the importer."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import re
import tempfile
import time
import unittest

SOURCES = {
    'ideas': 'docs/IDEA_BACKLOG.md',
    'families': 'experiments/semantic_assumptions/CLOSED_ROUTE_FAMILIES.tsv',
    'ledger': 'experiments/semantic_assumptions/ACTIVE_EXPERIMENT_LEDGER.tsv',
    'index': 'experiments/EXPERIMENT_INDEX.tsv',
    'anchors': 'experiments/semantic_assumptions/results/translation_anchor_acquisition_registry_v1.tsv',
}


def rows_with_lines(path):
    with path.open(newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle, delimiter='\t')
        assert reader.fieldnames
        while True:
            start = reader.line_num + 1
            try:
                row = next(reader)
            except StopIteration:
                break
            yield start, row


def audit_ledger(ledger, records):
    by_id = {r['id']: r for r in records}
    assert len(by_id) == len(records), 'Duplicate imported record ID'
    histories = {r['imported_fields']['exact_ledger_key']: r for r in records if r['kind']=='history'}
    assert len(histories) == sum(r['kind']=='history' for r in records), 'Merged history keys'
    expected = Counter()
    source_rows = 0
    for line, row in rows_with_lines(ledger):
        key = row['experiment']
        if re.fullmatch(r'GDT\d{3,}', key) and key in by_id and by_id[key]['kind']=='attempt':
            identifier = key
        else:
            assert key in histories, f'Missing history at ledger line {line}'
            identifier = histories[key]['id']
        event = dict(date=row['date'], status=row['status'], summary=row['live_scope'],
                     limitations=row['forbidden_inference'], evidence=row['primary_report'], source_row=line)
        expected[(identifier,json.dumps(event,sort_keys=True))] += 1
        source_rows += 1
    actual = Counter((r['id'],json.dumps(event,sort_keys=True)) for r in records for event in r.get('events',[]))
    assert actual == expected, 'Ledger event content, line, multiplicity or attachment mismatch'
    return source_rows


def audit_actual(root):
    records = [json.loads(line) for line in (root/'research_registry/imported.jsonl').read_text().splitlines() if line]
    manifest = json.loads((root/'research_registry/SOURCE_MANIFEST.json').read_text())
    source_hashes = {x['path']: x['sha256'] for x in manifest['sources']}
    for path in SOURCES.values():
        assert hashlib.sha256((root/path).read_bytes()).hexdigest()==source_hashes[path], 'Imported source stale'
    ledger_count = audit_ledger(root/SOURCES['ledger'], records)
    by_id = {r['id']:r for r in records}
    index = list(rows_with_lines(root/SOURCES['index']))
    index_ids = {r['experiment_id'] for _,r in index}
    assert len(index_ids)==len(index)
    assert {r['id'] for r in records if r['kind']=='attempt'}==index_ids
    for line,row in index:
        target=by_id[row['experiment_id']]
        assert target['source_status']==row['status'] and target['summary']==row['question']
        assert target['title']==(row['question'] or row['experiment_name'])
        assert target['imported_fields']['primary_report']==row['primary_report']
        assert any(s['path']==SOURCES['index'] and s['locator']==f'line:{line}' for s in target['sources'])
    families = list(rows_with_lines(root/SOURCES['families']))
    assert {r['id'] for r in records if r['kind']=='family'}=={'FAMILY:'+r['family'] for _,r in families}
    for _,row in families:
        target=by_id['FAMILY:'+row['family']]
        assert target['summary']==row['what_the_archive_establishes']
        assert target['source_status']==row['status'] and target['legacy_reopen_text']==row['reopen_only_if']
        assert target['imported_fields']['archive_pointer']==row['archive_pointer']
    anchors = list(rows_with_lines(root/SOURCES['anchors']))
    assert {r['id'] for r in records if r['kind']=='anchor'}=={'ANCHOR:'+r['candidate_id'] for _,r in anchors}
    for _,row in anchors:assert by_id['ANCHOR:'+row['candidate_id']]['imported_fields']==row
    idea_text=(root/SOURCES['ideas']).read_text()
    ideas=set(re.findall(r'(?<![A-Za-z0-9_])IP\d{3,}(?![A-Za-z0-9_])',idea_text))
    assert {r['id'] for r in records if r['kind']=='idea'}==ideas
    for identifier in ideas:
        expected=[n for n,line in enumerate(idea_text.splitlines(),1)
                  if re.search(r'(?<![A-Za-z0-9_])'+identifier+r'(?![A-Za-z0-9_])',line)]
        assert by_id[identifier]['imported_fields']['mention_lines']==expected
    return dict(status='PASS',source_files=5,source_hashes_match=True,
                imported_records=len(records),kinds=dict(Counter(r['kind'] for r in records)),
                ledger_events_exact=ledger_count,ledger_fields=['date','status','summary','limitations','evidence','source_row'],
                index_rows_exact=len(index),family_rows_exact=len(families),anchor_rows_exact=len(anchors),idea_ids_and_mention_lines_exact=len(ideas),
                importer_invoked=False,report_bodies_opened=False,manuscript_data_opened=False,
                limitation='Metadata preservation only; imported statuses and prose are not adjudicated scientific findings.')


def benchmark():
    from tools import research_registry as r
    from tests.test_research_registry import record
    with tempfile.TemporaryDirectory() as folder:
        root=Path(folder)
        records=[record(f'IDEA{i:06d}', title=f'Synthetic numerical evidence family {i}',
             summary='Independently owned relation, fixed contrast, unknown meaning. '*8,
             events=[dict(date='2026-01-01',status='SYNTHETIC',summary='Long synthetic history. '*25,
                          limitations='No scientific claim. '*10,evidence='',source_row=j+1)
                     for j in range(10)]) for i in range(10000)]
        started=time.perf_counter();r.write_snapshot(root,records);write_seconds=time.perf_counter()-started
        started=time.perf_counter();built=r.build_index(root);build_seconds=time.perf_counter()-started
        started=time.perf_counter();result=r.search(root,'numerical');query_seconds=time.perf_counter()-started
        detail=r.show(root,'IDEA000001')
        assert built['records']==10000 and len(result['results'])==8
        return dict(records=10000,events=100000,write_seconds=round(write_seconds,6),
                    build_seconds=round(build_seconds,6),query_seconds=round(query_seconds,6),
                    returned_cards=8,search_canonical_characters=len(r.canonical(result)),
                    show_canonical_characters=len(r.canonical(detail)),
                    measurement='Single local wall-clock run; includes freshness checks; not a hardware-independent speed guarantee.')


class IdeaDefinitionTests(unittest.TestCase):
    def test_plain_cross_reference_is_not_an_idea_definition(self):
        from tools.research_registry_import import _ideas
        source={'path':'docs/ideas.md','sha256':'0'*64,'text':
                'IP014 and IP018 were reviewed below.\n| IP014 | Actual checksum mechanism | Source | Risk |\n'}
        record=next(r for r in _ideas(source) if r['id']=='IP014')
        self.assertEqual(record['title'],'Actual checksum mechanism')
        self.assertEqual(record['imported_fields']['definition_lines'],[2])
        self.assertEqual(record['imported_fields']['mention_lines'],[1,2])

    def test_future_four_digit_idea_identifier_is_preserved(self):
        from tools.research_registry_import import _ideas
        rows=_ideas({'path':'docs/ideas.md','sha256':'0'*64,'text':'### IP1000 — Future mechanism\nDetails.\n'})
        self.assertEqual(rows[0]['id'],'IP1000')
        self.assertEqual(rows[0]['title'],'Future mechanism')


class LedgerPreservationTests(unittest.TestCase):
    def fixture(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);p=Path(temp.name)/'ledger.tsv'
        with p.open('w',newline='') as f:
            writer=csv.writer(f,delimiter='\t');writer.writerow(['date','experiment','status','live_scope','forbidden_inference','primary_report'])
            writer.writerow(['day','custom','STOP','line one\nline two','limits','report.md'])
            writer.writerow(['day','custom','STOP','line one\nline two','limits','report.md'])
        events=[dict(date='day',status='STOP',summary='line one\nline two',limitations='limits',evidence='report.md',source_row=n) for n in [2,4]]
        return p,[dict(id='HIST:fixture',kind='history',imported_fields=dict(exact_ledger_key='custom'),events=events)]

    def test_multiline_physical_line_and_duplicate_event_preservation(self):
        path,records=self.fixture();self.assertEqual(audit_ledger(path,records),2)

    def test_dropped_duplicate_or_changed_field_fails(self):
        path,records=self.fixture();records[0]['events'].pop()
        with self.assertRaises(AssertionError):audit_ledger(path,records)
        path,records=self.fixture();records[0]['events'][0]['limitations']='changed'
        with self.assertRaises(AssertionError):audit_ledger(path,records)


if __name__=='__main__':unittest.main()
