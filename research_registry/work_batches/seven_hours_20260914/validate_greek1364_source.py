#!/usr/bin/env python3
"""Check external source bindings, never interpret the images or access Voynich."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse, hashlib, json, urllib.request

B = Path(__file__).resolve().parent
S = json.loads((B / 'GREEK1364_SOURCE_RESULT.json').read_text())
P = argparse.ArgumentParser()
P.add_argument('--refetch', action='store_true')
A = P.parse_args()
C = B / 'greek1364_cache'
C.mkdir(exist_ok=True)


def fetch(url, name):
    path = C / name
    if A.refetch or not path.exists():
        with urllib.request.urlopen(url, timeout=60) as r:
            data = r.read()
        path.write_bytes(data)
    return path.read_bytes()


def check_image(x):
    raw = fetch(x['url'], 'reg181_' + x['exact_label'] + '.jpg')
    return x['exact_label'], hashlib.sha256(raw).hexdigest() == x['sha256']


errors = []
try:
    manifest = json.loads(fetch(S['manifest_url'], 'vatlib_manifest.json'))
    canvases = manifest['sequences'][0]['canvases']
    for x in S['images']:
        rows = [c for c in canvases if c['label'] == x['exact_label']]
        if len(rows) != 1 or rows[0]['@id'] != x['canvas']:
            errors.append('exact-canvas-binding:' + x['exact_label'])
            continue
        service = rows[0]['images'][0]['resource']['service']['@id']
        if x['url'] != service + '/full/full/0/default.jpg':
            errors.append('image-binding:' + x['exact_label'])
    with ThreadPoolExecutor(max_workers=6) as pool:
        for label, passed in pool.map(check_image, S['images']):
            if not passed:
                errors.append('image-hash:' + label)
    raw = fetch(S['pdf_url'], 'journalofhelleni10soci.pdf')
    if hashlib.sha256(raw).hexdigest() != S['pdf_sha256']:
        errors.append('article-volume-hash')
    if len(S['source_sentence'].split()) != 11:
        errors.append('editorial-sentence-word-count')
    mapping = {x['exact_label']: x['canvas'] for x in S['images']}
    if mapping['13r'] == mapping['XIIIr']:
        errors.append('roman-arabic-folio-collision')
except Exception as e:
    errors.append(type(e).__name__ + ':external-source-check')

result = {
    'status': 'PASS' if not errors else 'FAIL', 'errors': errors,
    'coverage': 'six exact original canvas/image bindings and hashes; public article-volume hash; eleven editorial words',
    'fresh_network_refetch': A.refetch,
    'native_interpretation_or_greek_transcription_validated': False,
    'voynich_data_accessed': False, 'target_model_tested': False,
    'meaning_confirmed': False,
}
(B / 'GREEK1364_VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
raise SystemExit(bool(errors))
