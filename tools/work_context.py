"""Bounded views of live documentation; never traverse experiment/raw-data files."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
ROUTE = 'VOYNICH_CURRENT_ROUTE.md'
CATALOG = 'research_registry/context_navigation.json'
SOURCES = {
    'brief': 'docs/VOYNICH_RESEARCH_BRIEF.md',
    'map': 'docs/VOYNICH_CLAIM_STATUS_MAP.md',
    'scope': 'docs/VOYNICH_DATA_SCOPE.md',
    'guide': 'research_registry/README.md',
}
START_BYTES = 4096
TOPIC_BYTES = 6000
SOURCE_BYTES = 65536
FIELDS = ('Phase', 'Status', 'Task', 'Latest decision', 'Working files', 'Assumptions', 'Resume', 'Running')


def read_doc(root: Path, relative: str, limit: int) -> str:
    path = root / relative
    if path.resolve() != root.resolve() / relative:
        raise ValueError('Context source symlinks are not allowed.')
    with path.open('rb') as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f'{relative} exceeds {limit} bytes; replace/split its live summary.')
    return data.decode('utf-8')


def normalize(value: str) -> str:
    folded = unicodedata.normalize('NFKD', value.casefold())
    return ' '.join(re.findall(r'[a-z0-9]+', ''.join(c for c in folded if not unicodedata.combining(c))))


def navigation(root: Path) -> list[dict]:
    data = json.loads(read_doc(root, CATALOG, 32768))
    if set(data) != {'version', 'topics'} or data['version'] != 1:
        raise ValueError('Unsupported context navigation schema.')
    topics = data['topics']
    if not isinstance(topics, list) or not 1 <= len(topics) <= 32:
        raise ValueError('Keep navigation at 1–32 broad topics; use the existing registry for experiments.')
    names = set()
    for topic in topics:
        if set(topic) != {'id', 'title', 'aliases', 'blocks'}:
            raise ValueError('Topic records may contain navigation selectors only.')
        if not isinstance(topic['id'], str) or not re.fullmatch(r'[a-z][a-z0-9_]{0,31}', topic['id']):
            raise ValueError('Invalid context topic ID.')
        if not isinstance(topic['title'], str) or not 1 <= len(topic['title']) <= 100:
            raise ValueError('Invalid context title.')
        if not isinstance(topic['aliases'], list) or len(topic['aliases']) > 12:
            raise ValueError('At most 12 aliases per topic.')
        local = set()
        for name in [topic['id'], *topic['aliases']]:
            if not isinstance(name, str) or not 1 <= len(name) <= 80 or not normalize(name):
                raise ValueError('Invalid topic alias.')
            key = normalize(name)
            if key in names:
                raise ValueError('A topic alias resolves to multiple topics.')
            local.add(key)
        names.update(local)
        if not isinstance(topic['blocks'], list) or not 1 <= len(topic['blocks']) <= 4:
            raise ValueError('Select 1–4 complete blocks per topic.')
        for block in topic['blocks']:
            if set(block) not in ({'source', 'row'}, {'source', 'bullet'}):
                raise ValueError('Only exact table rows or bullet blocks may be selected.')
            if block['source'] not in SOURCES:
                raise ValueError('Context sources are restricted to four live documentation files.')
            selector = block.get('row', block.get('bullet'))
            if not isinstance(selector, str) or not 1 <= len(selector) <= 100:
                raise ValueError('Invalid block selector.')
    return topics


def start(root: Path = ROOT) -> str:
    text = read_doc(root, ROUTE, START_BYTES)
    if len(text.splitlines()) > 80:
        raise ValueError('Current route exceeds 80 lines.')
    for field in FIELDS:
        matches = re.findall(rf'^{re.escape(field)}: (.+)$', text, re.M)
        if len(matches) != 1 or not matches[0].strip():
            raise ValueError(f'Current route needs one nonempty {field} field.')
    phase = re.search(r'^Phase: (.+)$', text, re.M).group(1)
    status = re.search(r'^Status: (.+)$', text, re.M).group(1)
    if phase not in {'workflow', 'exploration', 'fixed_test', 'reserved_confirmation', 'idle'}:
        raise ValueError('Invalid current work phase.')
    if status not in {'active', 'checkpoint', 'complete', 'parked'}:
        raise ValueError('Invalid current work status.')
    required = ('## Structural baseline', 'f84 and f84r remain sealed.', 'query-tsv', 'VOYNICH_DATA_SCOPE.md',
                'VOYNICH_RESEARCH_BRIEF.md', 'VOYNICH_CLAIM_STATUS_MAP.md')
    if any(item not in text for item in required):
        raise ValueError('Current route lost a baseline or data-scope entry pointer.')
    return text


def excerpt(text: str, block: dict) -> tuple[int, str]:
    lines = text.splitlines()
    if 'row' in block:
        wanted = block['row']
        matches = []
        for i, line in enumerate(lines):
            if line.startswith('|'):
                cell = line.split('|')[1].strip()
                if cell == wanted or cell.startswith(wanted + ' — '):
                    matches.append(i)
        if len(matches) != 1:
            raise ValueError(f'Expected one table row: {wanted}. Refresh the navigation selector.')
        i = matches[0]
        separators = [j for j in range(i) if re.fullmatch(r'\|[\s:|\-]+\|', lines[j])]
        if not separators or separators[-1] == 0:
            raise ValueError('Selected row lacks its table header.')
        j = separators[-1]
        if not lines[j - 1].startswith('|') or any(not line.startswith('|') for line in lines[j + 1:i]):
            raise ValueError('Selected row is detached from its table header.')
        return i + 1, '\n'.join((lines[j - 1], lines[j], lines[i]))
    wanted = '- **' + block['bullet']
    matches = [i for i, line in enumerate(lines) if line.startswith(wanted)]
    if len(matches) != 1:
        raise ValueError('Expected one bullet block. Refresh the navigation selector.')
    i = matches[0]
    end = next((j for j in range(i + 1, len(lines))
                if lines[j].strip() and not lines[j].startswith((' ', '\t'))), len(lines))
    return i + 1, '\n'.join(lines[i:end]).rstrip()


def render_topic(root: Path, topic: dict) -> str:
    output = [f"# {topic['title']} [{topic['id']}]", 'Live excerpts; read cited primaries before scientific selection. No admission or semantic confirmation.']
    cache = {}
    for block in topic['blocks']:
        relative = SOURCES[block['source']]
        if relative not in cache:
            cache[relative] = read_doc(root, relative, SOURCE_BYTES)
        body = cache[relative]
        line, selected = excerpt(body, block)
        sha = hashlib.sha256(body.encode('utf-8')).hexdigest()
        output.extend((f'Source: {relative}:{line} (sha256 {sha})', selected))
    result = '\n\n'.join(output) + '\n'
    if len(result.encode('utf-8')) > TOPIC_BYTES:
        raise ValueError('Topic exceeds 6000 bytes; narrow its blocks. Nothing was silently truncated.')
    return result


def topic(root: Path, query: str) -> str:
    if not 1 <= len(query) <= 80:
        raise ValueError('Use a short topic ID or alias.')
    key = normalize(query)
    for record in navigation(root):
        if key in {normalize(x) for x in [record['id'], *record['aliases']]}:
            return render_topic(root, record)
    raise ValueError('Unknown topic; use context topics, then bounded ideas search/show. No absence-of-research conclusion follows.')


def check(root: Path = ROOT) -> dict:
    boot = start(root)
    sizes = {record['id']: len(render_topic(root, record).encode('utf-8')) for record in navigation(root)}
    return {'status': 'PASS', 'scope': 'live documentation format, block selectors and byte limits only',
            'start_bytes': len(boot.encode('utf-8')), 'max_start_bytes': START_BYTES,
            'topic_count': len(sizes), 'largest_topic_bytes': max(sizes.values()),
            'max_topic_bytes': TOPIC_BYTES, 'manuscript_data_read': False, 'scientific_validation': False}


def main(argv=None, *, root: Path = ROOT) -> int:
    parser = argparse.ArgumentParser(prog='vmanus-work context')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('start', help='bounded current route and resume point')
    listing = commands.add_parser('topics', help='paged topic names and aliases, not source content')
    listing.add_argument('--offset', type=int, default=0)
    listing.add_argument('--limit', type=int, default=8)
    selected = commands.add_parser('topic', help='one complete bounded topic from current documentation')
    selected.add_argument('query')
    commands.add_parser('check', help='check live navigation and limits; no manuscript access')
    args = parser.parse_args(argv)
    try:
        if args.command == 'start':
            output = start(root)
        elif args.command == 'topic':
            output = topic(root, args.query)
        elif args.command == 'check':
            output = json.dumps(check(root), indent=2) + '\n'
        else:
            if args.offset < 0 or not 1 <= args.limit <= 8:
                raise ValueError('Use offset >=0 and limit 1–8.')
            records = navigation(root)
            rows = [{k: record[k] for k in ('id', 'title', 'aliases')}
                    for record in records[args.offset:args.offset + args.limit]]
            output = json.dumps({'topics': rows, 'total': len(records),
                                 'next_offset': args.offset + args.limit if args.offset + args.limit < len(records) else None},
                                ensure_ascii=False, indent=2) + '\n'
            if len(output.encode('utf-8')) > TOPIC_BYTES:
                raise ValueError('Topic list exceeds 6000 bytes; reduce --limit. Nothing was truncated.')
        sys.stdout.write(output)
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        # Do not print arbitrary file contents or private absolute paths in errors.
        message = str(error) if isinstance(error, ValueError) else 'Invalid or unavailable context metadata.'
        parser.error(message[:240])


if __name__ == '__main__':
    raise SystemExit(main())
