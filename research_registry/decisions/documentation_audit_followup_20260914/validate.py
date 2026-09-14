"""Check this bounded documentation change without opening manuscript data."""
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main():
    errors = []
    bindings = json.loads((HERE / 'PRESERVATION.json').read_text())
    for name, expected in bindings.items():
        data = (ROOT / name).read_bytes()
        if len(data) != expected['bytes'] or hashlib.sha256(data).hexdigest() != expected['sha256']:
            errors.append(f'changed historical source: {name}')

    baseline = json.loads((HERE / 'BASELINE.json').read_text())
    curation = (ROOT / 'research_registry/curation.jsonl').read_bytes()
    old = baseline['curation_prefix']
    if hashlib.sha256(curation[:old['bytes']]).hexdigest() != old['sha256']:
        errors.append('old curation prefix changed')
    appended = [json.loads(row) for row in curation[old['bytes']:].splitlines() if row.strip()]
    if len(appended) != 1 or appended[0].get('record_id') != 'GDT616':
        errors.append('expected exactly one appended GDT616 review')
    else:
        requested = json.loads((HERE / 'REVIEW.json').read_text())
        for key, value in requested.items():
            if appended[0].get(key) != value:
                errors.append(f'GDT616 review differs from input: {key}')

    route = (ROOT / 'VOYNICH_CURRENT_ROUTE.md').read_bytes()
    if len(route) > 6000 or len(route.splitlines()) > 80:
        errors.append('route exceeds compactness limit')
    mapping = (ROOT / 'docs/VOYNICH_CLAIM_STATUS_MAP.md').read_text()
    ids = re.findall(r'^\| (K\d{2}) —', mapping, flags=re.M)
    if ids != [f'K{i:02}' for i in range(1, 13)]:
        errors.append('expected twelve unique ordered topic rows')

    documents = [ROOT / name for name in (
        'AGENTS.md', 'VOYNICH_CURRENT_ROUTE.md', 'docs/VOYNICH_RESEARCH_BRIEF.md',
        'docs/VOYNICH_CLAIM_STATUS_MAP.md', 'research_registry/README.md',
    )] + [HERE / name for name in ('REPORT.md', 'PEER_AUDIT.md', 'DECISION.md')]
    links = 0
    for document in documents:
        for target in re.findall(r'\[[^\]\n]*\]\(([^)\n]+)\)', document.read_text()):
            parsed = urlsplit(target.strip().strip('<>'))
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            path = (document.parent / unquote(parsed.path)).resolve()
            if not path.is_relative_to(ROOT) or (not path.exists() and path != HERE / 'VALIDATION.json'):
                errors.append(f'invalid local link in {document.relative_to(ROOT)}: {target}')
            links += 1

    result = {
        'status': 'FAIL' if errors else 'PASS',
        'scope': 'historical bytes, review append preservation, local links, topic rows and route size only',
        'scientific_revalidation': False,
        'manuscript_data_opened': False,
        'preserved_sources': len(bindings),
        'appended_reviews': len(appended),
        'topic_rows': ids,
        'local_links_checked': links,
        'route': {'bytes': len(route), 'lines': len(route.splitlines())},
        'errors': errors,
    }
    (HERE / 'VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
