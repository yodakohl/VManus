"""Post-result provenance audit; never edits the locked reading or source."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json'
EXPECTED = '667ca3ae0705a6bb3ccfcd09ea7ee04e28747e58d810e8fa9379f28c0f4fc89b'


def main():
    assert hashlib.sha256(CACHE.read_bytes()).hexdigest() == EXPECTED
    source_path = BASE / 'src/SOURCE.json'
    source = json.loads(source_path.read_text())
    paragraphs = json.loads(CACHE.read_text())['ZL3b']
    owned = [p for p in paragraphs if p['id'] == 'f82r|f82r.11-f82r.19']
    assert len(owned) == 1
    paragraph = owned[0]
    rows = []
    for draft, diplomatic in zip(source['records'], paragraph['lines'], strict=True):
        assert draft['locus'] == diplomatic['locus']
        words = draft['raw'].split()
        differences = [dict(group=i, working=a, diplomatic=b)
                       for i, (a, b) in enumerate(zip(words, diplomatic['words'], strict=True), 1)
                       if a != b]
        rows.append(dict(locus=draft['locus'], start=diplomatic['start'],
                         end=diplomatic['end'], anchor_eligible=diplomatic['anchor_eligible'],
                         equal=not differences, differences=differences))
    result = dict(
        status='NORMALIZED_WORKING_COPY_NOT_COMPLETE_DIPLOMATIC_READING',
        chronology='Post-result audit after bf5d29983; not a preregistered test or new reading.',
        source_sha256=hashlib.sha256(source_path.read_bytes()).hexdigest(),
        diplomatic_cache=str(CACHE.relative_to(ROOT)), diplomatic_cache_sha256=EXPECTED,
        paragraph=paragraph['id'], same_line_span=True, same_group_count=True,
        working_groups=len(source['words']), working_types=len(set(source['words'])),
        working_characters=sum(map(len, source['words'])),
        matching_lines=sum(r['equal'] for r in rows), total_lines=len(rows),
        anchor_eligible_lines=sum(r['anchor_eligible'] for r in rows),
        differing_groups=sum(len(r['differences']) for r in rows), rows=rows,
        decision='Retain locked hypothetical arithmetic. Withdraw complete diplomatic coverage claim; no silent source repair.',
        meaning='No confirmed word; no independent meaning or new admission.')
    (BASE / 'artifacts/SOURCE_SCOPE_AUDIT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('status', 'matching_lines', 'total_lines', 'differing_groups', 'anchor_eligible_lines')}))


if __name__ == '__main__':
    main()
