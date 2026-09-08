#!/usr/bin/env python3
"""Package two frozen native observations; this is not a vision classifier."""
from pathlib import Path
import hashlib
import json
import urllib.request

BASE = Path(__file__).resolve().parents[1]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    art = BASE / 'artifacts'
    source = json.loads((art / 'SOURCE.json').read_text())
    raw = BASE / 'runtime/1006247.jpg'
    if not raw.exists():
        raw.parent.mkdir(exist_ok=True)
        req = urllib.request.Request(source['url'], headers={'User-Agent':'VManus-GDT881-replay/1.0'})
        raw.write_bytes(urllib.request.urlopen(req, timeout=30).read())
    assert digest(raw) == source['sha256']
    packets = [json.loads((art / f'{who}.json').read_text()) for who in ['ROOT', 'B']]
    assert all(p['source_sha256'] == source['sha256'] for p in packets)
    counts = [sum(i['certainty']=='clear' and i['dual_role'] for i in p['interfaces']) for p in packets]
    nominated = all(n >= 2 for n in counts) and packets[0]['construction_rule'] is not None and packets[0]['construction_rule'] == packets[1]['construction_rule']
    owner = 'RETAINED_LOCAL_OBSERVATION_ONLY' if all(p['inside_writing']=='yes' for p in packets) else 'UNRESOLVED_QUARANTINED'
    result = {
        'experiment':'GDT881',
        'status':'DISCOVERY_INTERFACE_NOMINATED' if nominated else 'STOP_NO_SHARED_STROKE_CONSTRUCTION',
        'clear_dual_role_interfaces':dict(zip(['ROOT','B'],counts)),
        'scene_located':{p['observer']:p['scene_located'] for p in packets},
        'inside_writing':{p['observer']:p['inside_writing'] for p in packets},
        'ordinary_lines':{p['observer']:p['ordinary_lines'] for p in packets},
        'historical_single_inside_body_positive':owner,
        'new_visual_keys':1,'total_visual_keys':46,'total_visual_selectors':52,'remaining_discretionary_keys':4,
        'source_sha256':source['sha256'],
        'packet_sha256':{who:digest(art/f'{who}.json') for who in ['ROOT','B']},
        'claim_ceiling':'Native source observation only; no translation, glyph/meaning assignment, statistical score, PVO census rerun, chronology or general iconic-code refutation.'
    }
    (art/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__ == '__main__':
    main()
