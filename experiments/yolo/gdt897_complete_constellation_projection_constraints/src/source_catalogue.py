"""Frozen Ptolemaios historical fields; no modern identifications or target inputs.

Usage: source_catalogue.py --catalogue ptolema.dat --output SOURCE_UNITS.json
Only bytes 1..39 are interpreted after verifying the entire original byte hash.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

RAW_SHA256 = 'd405be669287fb814aebc7a5dcde3a329afdcd34e8bb728314b6608142c0d75f'
FIELDS = {'id': (0, 4, 1, 1028), 'constellation': (5, 7, 1, 48),
          'number': (13, 15, 1, 45), 'zodiac': (18, 20, 1, 12),
          'longitude_degree': (21, 23, 0, 30),
          'longitude_minute': (24, 26, 0, 59),
          'latitude_degree': (28, 30, 0, 90),
          'latitude_minute': (31, 33, 0, 60),
          'magnitude': (37, 38, 1, 9)}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parse_record(line):
    require(39 <= len(line) <= 78, 'record width')
    s = line[:39]
    require(all(s[i] == ' ' for i in
                (4, 7, 12, 16, 17, 20, 23, 26, 27, 30, 33, 35, 36)),
            'fixed-width separators')
    values = {}
    for name, (a, b, low, high) in FIELDS.items():
        require(re.fullmatch(r' *[0-9]+', s[a:b]) is not None, name + ' syntax')
        values[name] = int(s[a:b])
        require(low <= values[name] <= high, name + ' range')
    require(re.fullmatch(r'=[A-Za-z]{3}', s[8:12]) is not None, 'constellation code')
    require(s[15] in ' a' and s[34] in 'AB' and s[38] in ' bf', 'flags')
    require(values['magnitude'] in (1, 2, 3, 4, 5, 6, 7, 9), 'magnitude class')
    longitude = ((values['zodiac'] - 1) * 30 + values['longitude_degree']) * 60
    longitude += values['longitude_minute']
    latitude = values['latitude_degree'] * 60 + values['latitude_minute']
    require(0 <= longitude <= 21600 and 0 <= latitude <= 5400, 'coordinate bounds')
    values.update(constellation_code=s[8:12], outside=s[15] == 'a',
                  latitude_sign=s[34], magnitude_qualifier=s[38].strip(),
                  longitude_arcmin=longitude,
                  latitude_arcmin=latitude * (-1 if s[34] == 'A' else 1))
    return values


def build(raw):
    require(hashlib.sha256(raw).hexdigest() == RAW_SHA256, 'original SHA256 mismatch')
    rows = [parse_record(line) for line in raw.decode('ascii').splitlines()]
    require([r['id'] for r in rows] == list(range(1, 1029)), '1028 ordered record IDs')
    require(sorted({r['constellation'] for r in rows}) == list(range(1, 49)), '48 groups')
    require([r['constellation'] for r in rows] ==
            sorted(r['constellation'] for r in rows), 'constellation order')
    units = []
    for c in range(1, 49):
        group = [r for r in rows if r['constellation'] == c]
        require(len({r['constellation_code'] for r in group}) == 1, 'group code')
        require([r['number'] for r in group] == list(range(1, len(group) + 1)),
                'within-constellation order')
        for mode in ('FORMED', 'FULL'):
            members = [r['id'] for r in group if mode == 'FULL' or not r['outside']]
            units.append({'case_id': f'C{c:02d}:{mode}', 'constellation': c,
                          'constellation_code': group[0]['constellation_code'],
                          'mode': mode, 'member_ids': members})
    return {'schema': 'gdt897-source-units-v1', 'raw_sha256': RAW_SHA256,
            'coordinate_contract': 'raw catalogue 137 CE; integer arcminutes; no epoch adjustment',
            'magnitude_use': 'metadata only; never membership',
            'records': rows, 'units': units}


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(',', ':')) + '\n').encode('utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalogue', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.write_bytes(encode(build(args.catalogue.read_bytes())))
