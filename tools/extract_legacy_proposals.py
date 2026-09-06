"""Extract explicit authored proposal cards from tracked prose, not manuscript tables.

Output is a provenance inventory, not semantic deduplication. Markdown fences,
sealed-selector lines, raw/source/transcription JSON and untracked files are
excluded. The first JSONL row documents the exact scanning boundary.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

EXCLUDED = ('docs/IDEA_BACKLOG.md', 'research_registry/',
            'experiments/yolo/gdt600_complete_object_surface_grammar/',
            'experiments/yolo/sidequest_theory_candidates_v81/',
            'experiments/yolo/sidequest_theory_candidates_v81_creative/',
            'experiments/yolo/SIDEQUEST_V81_ATOMIC_CODEBOOK_VOCABULARY_PROTOCOL.md')
KEY = re.compile(r'idea|hypothes|hypothes[ei]|proposal|candidate|theor[yi]|modell?|rival|interpretation|iteration|version\s+\d', re.I)
SEALED = re.compile(r'(?<![A-Za-z0-9])f84[a-z0-9]*', re.I)
HEADING = re.compile(r'^\s*(#{1,6})\s+(.+?)\s*#*\s*$')
NUMBERED = re.compile(r'^\s*(?:\d+[.)]|[A-Z][.)])\s+(.+)')
STATUS = re.compile(r'^\s*(?:\*\*)?(?:status|confidence|decision|verdict|state)(?:\*\*)?\s*:', re.I)
EXPLICIT = re.compile(r'\b(?:ideas?|ideen?|hypothes(?:is|es|e|en)|hypothèse|proposals?|vorschl[aä]g\w*|candidates?|kandidaten?)\b', re.I)
PROCEDURAL = re.compile(r'\b(?:protocol|method|procedure|steps?|workflow|validation|validator|reproduction|execution|checklist|controls?|implementation|audit|gate|test|preregistration|protokoll|schritte|prüfung|umsetzung)\b', re.I)


def candidates(root):
    paths = subprocess.check_output(['git', 'ls-files', '-z', '--', '*.md', '*.json'], cwd=root).decode().split('\0')
    selected = []
    for path in sorted(filter(None, paths)):
        if any(path == x or path.startswith(x) for x in EXCLUDED):
            continue
        p = Path(path)
        if SEALED.search(path):
            continue
        if any(part.lower() in {'raw', 'transcription', 'transcriptions', 'images', 'cache', 'runtime'} for part in p.parts):
            continue
        if p.suffix == '.json':
            if re.search(r'proposal|hypothes', p.name, re.I) and not re.search(r'prediction|validation|audit|result', p.name, re.I):
                selected.append(path)
        elif (path in {'VOYNICH_WORKLOG.md','VOYNICH_HANDOFF.md','VOYNICH_ACTIVE_STATE.md','EXPERIMENT_LOG.md','README.md'}
              or path.startswith(('docs/', 'experiments/semantic_assumptions/', 'experiments/yolo/sidequest_', 'candidates/'))
              or KEY.search(p.name) or re.search(r'(?:REPORT|METHOD|PREREGISTRATION|SPEC)\.md$', p.name)
              or p.name == 'WORKING_THEORY.md'):
            selected.append(path)
    return selected


def markdown_cards(text, path):
    lines = text.splitlines()
    visible = []
    fence = None
    excluded_lines = 0
    for number, line in enumerate(lines, 1):
        match = re.match(r'^\s*(`{3,}|~{3,})', line)
        if match:
            token = match.group(1)
            if fence is None:
                fence = token[0]
            elif token[0] == fence:
                fence = None
            visible.append(''); excluded_lines += 1
        elif fence or SEALED.search(line):
            visible.append(''); excluded_lines += 1
        else:
            visible.append(line)
    file_title = next((HEADING.match(x).group(2) for x in visible if HEADING.match(x)), Path(path).stem)
    file_status = next((x.strip() for x in visible[:100] if STATUS.match(x)), 'UNSPECIFIED_IN_SOURCE')
    collection = bool(KEY.search(path))
    starts = {}
    heading_context = ''
    table_hypothesis = False
    table_context = ''
    for i, line in enumerate(visible):
        heading = HEADING.match(line)
        if heading:
            heading_context = heading.group(2)
            if KEY.search(heading_context) or (collection and len(heading.group(1)) == 1):
                explicit = bool(EXPLICIT.search(heading_context)) and not PROCEDURAL.search(heading_context)
                starts[i] = ('heading', heading_context, heading_context, explicit)
            table_hypothesis = False
        numbered = NUMBERED.match(line)
        if numbered and (collection or KEY.search(heading_context)):
            explicit = bool(EXPLICIT.search(heading_context)) and not PROCEDURAL.search(heading_context)
            starts[i] = ('numbered_card', numbered.group(1), heading_context, explicit)
        if line.lstrip().startswith('|'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            next_is_rule = i + 1 < len(visible) and bool(re.match(r'^\s*\|?\s*:?-{3}', visible[i + 1]))
            if next_is_rule:
                table_hypothesis = any(KEY.search(c) for c in cells)
                table_context = ' | '.join(cells)
            elif table_hypothesis and not all(re.fullmatch(r'[:\-\s]*', c) for c in cells):
                explicit = bool(EXPLICIT.search(table_context)) and not PROCEDURAL.search(heading_context)
                starts[i] = ('table_card', cells[0] if cells else file_title, heading_context + ' / ' + table_context, explicit)
        elif line.strip():
            table_hypothesis = False
    cards = []
    for start, (kind, title, context, explicit) in sorted(starts.items()):
        end = start + 1
        if kind != 'table_card':
            while end < len(visible):
                if HEADING.match(visible[end]) or end in starts:
                    break
                end += 1
        kept = [(i + 1, visible[i]) for i in range(start, end) if visible[i].strip()]
        if not kept:
            continue
        cards.append(dict(line=start + 1, end_line=end, title=title,
                          hypothesis='\n'.join(value for _, value in kept),
                          source_lines=[n for n, _ in kept],
                          source_status=next((value.strip() for _, value in kept if STATUS.match(value)), file_status),
                          candidate_type='explicit_proposal' if explicit else 'source_excerpt',
                          classification_context=context,
                          classification_basis='Lexical section/table context only; unreviewed and not a uniqueness judgment.',
                          extraction_rule=kind,
                          verbatim_policy='Individual retained lines verbatim; fenced/sealed lines and blank lines omitted.'))
    return cards, excluded_lines


def json_cards(text, path):
    value = json.loads(text)
    cards = []
    admitted = {'hypothesis', 'proposal', 'mechanism', 'prediction', 'fixed_sense', 'description', 'rationale', 'motivation', 'gloss_de', 'gloss_en', 'title', 'name', 'contrast'}
    def walk(node, pointer=''):
        if isinstance(node, dict):
            fields = {k: v for k, v in node.items() if k in admitted and isinstance(v, str) and not SEALED.search(v)}
            if fields and any(k in fields for k in ('hypothesis', 'proposal', 'mechanism', 'prediction', 'fixed_sense', 'description')):
                first_key = next(iter(fields))
                found = re.search(re.escape(json.dumps(first_key)) + r'\s*:', text)
                line = text[:found.start()].count('\n') + 1 if found else 1
                cards.append(dict(line=line, end_line=line, title=fields.get('title', fields.get('name', pointer or Path(path).stem)),
                                  hypothesis='\n'.join(fields.values()), authored_fields=fields,
                                  source_lines=[line], json_pointer=pointer or '/',
                                  source_status=str(node.get('status', value.get('status', 'UNSPECIFIED_IN_SOURCE') if isinstance(value, dict) else 'UNSPECIFIED_IN_SOURCE')),
                                  extraction_rule='json_authored_fields', verbatim_policy='Decoded authored string values only; JSON pointer is authoritative, line is key-navigation hint.'))
                cards[-1]['candidate_type'] = 'explicit_proposal' if ('proposal' in pointer.lower() or 'hypothes' in pointer.lower() or 'hypothesis' in fields or 'proposal' in fields) else 'source_excerpt'
                cards[-1]['classification_context'] = pointer
                cards[-1]['classification_basis'] = 'Explicit authored proposal field, not a reviewed idea.'
            for key, item in node.items():
                if key.lower() in {'raw', 'lines', 'sources', 'source_lines', 'transcription', 'local_seed', 'contexts', 'tokens'}:
                    continue
                if isinstance(item, (dict, list)):
                    walk(item, pointer + '/' + str(key).replace('~','~0').replace('/','~1'))
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, pointer + '/' + str(i))
    walk(value)
    return cards, 0


def extract(root):
    records, inventory = [], []
    for path in candidates(root):
        raw = (root / path).read_bytes()
        text = raw.decode('utf-8-sig')
        sha = hashlib.sha256(raw).hexdigest()
        cards, excluded = (json_cards if path.endswith('.json') else markdown_cards)(text, path)
        inventory.append(dict(path=path, sha256=sha, cards=len(cards), omitted_fenced_or_sealed_lines=excluded))
        for card in cards:
            key = path + ':' + str(card['line']) + ':' + card.get('json_pointer', '') + ':' + card['title']
            records.append(dict(id='LEGACY_PROPOSAL:' + hashlib.sha256(key.encode()).hexdigest()[:24],
                                record_type='authored_card', path=path, source_sha256=sha,
                                review_status='extracted_unreviewed', uniqueness='not_assessed', **card))
    selected_paths = {item['path'] for item in inventory}
    tracked = sorted(filter(None, subprocess.check_output(
        ['git', 'ls-files', '-z', '--', '*.md', '*.json'], cwd=root).decode().split('\0')))
    unresolved = [dict(path=item['path'], reason='SCANNED_NO_EXPLICIT_CARD_RECOGNIZED' if not item['cards'] else 'SOURCE_REMAINDER_NOT_COMPLETE_SEMANTIC_PARSE')
                  for item in inventory]
    # Inventory-only pointers, never open an omitted artifact to infer content.
    for path in tracked:
        if path in selected_paths or any(path == x or path.startswith(x) for x in EXCLUDED):
            continue
        if KEY.search(path):
            unresolved.append(dict(path=path, reason='PATH_MATCHES_PROPOSAL_FAMILY_NOT_SAFE_PROSE_INPUT'))
    manifest = dict(record_type='extraction_manifest', version=1, sources=inventory,
                    unresolved_source_pointers=unresolved,
                    counts=dict(scanned_sources=len(inventory), sources_with_cards=sum(bool(x['cards']) for x in inventory), cards=len(records)),
                    exclusions=list(EXCLUDED),
                    boundaries=['Tracked selected Markdown prose and explicitly named proposal/hypothesis JSON only; no TSV inputs.',
                                'Explicit hypothesis/model/iteration headings, numbered cards in proposal collections, and hypothesis-table rows.',
                                'Not all narrative sentences are proposals; procedural numbered items may be false positives pending review.',
                                'No semantic deduplication, eligibility judgment or historic claim validation.',
                                'Source line identifiers stable for unchanged source bytes; changed line layout requires re-extraction.',
                                'Fenced blocks and sealed-selector lines excluded before card construction.'])
    manifest['counts']['unresolved_source_pointers'] = len(unresolved)
    manifest['counts']['explicit_proposal_fragments'] = sum(r['candidate_type'] == 'explicit_proposal' for r in records)
    manifest['counts']['source_excerpts'] = sum(r['candidate_type'] == 'source_excerpt' for r in records)
    manifest['boundaries'].append('candidate_type distinguishes explicit proposal-language context from other source excerpts; both remain unreviewed fragments, not unique ideas.')
    return manifest, records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--output', type=Path, default=Path('research_registry/decisions/legacy_proposal_extraction.jsonl'))
    args = parser.parse_args()
    manifest, records = extract(args.root)
    target = args.root / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(''.join(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n' for row in [manifest, *records]))
    print(json.dumps(manifest['counts'], sort_keys=True))


if __name__ == '__main__':
    main()
