"""Independent inventory, exact-algebra and complete mask audit.

No image decoding. Random integer samples are regression checks, not proofs.
Soundness follows from exact determinant identities and outward interval laws.
"""
import argparse
import gzip
import hashlib
import itertools as it
import json
from pathlib import Path
from random import Random
import geometry_reference as ref


def require(ok, why):
    if not ok:
        raise ValueError(why)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def boxcheck(b):
    require(len(b) == 4 and all(type(x) is int for x in b), 'integer bbox')
    require(0 <= b[0] <= b[2] <= 1000 and 0 <= b[1] <= b[3] <= 1000, 'bbox bounds')


def inventory(directory):
    directory = Path(directory)
    names = ['OBSERVER_ROOT.json', 'OBSERVER_INDEPENDENT.json',
             'OBSERVER_REVISIT.json', 'TARGET_INVENTORY.json']
    root, other, revisit, target = [json.loads((directory / n).read_bytes()) for n in names]
    require(revisit['initial_inventory_sha256'] == sha(directory / names[1]), 'revisit seal')
    require(root['image_sha256'] == other['image']['sha256'] ==
            revisit['image_sha256'] == target['image_sha256'], 'image provenance')
    require((target['image_width'], target['image_height']) ==
            (other['image']['width'], other['image']['height']) == (7993, 3828), 'native metric')
    require(set(target['fields']) == {'LEFT', 'MIDDLE'}, 'target fields')
    require(other['complete'] is True, 'independent completeness')
    matched = []
    for field, count in [('LEFT', 29), ('MIDDLE', 59)]:
        a = root['fields'][field]['objects']
        b = [x for x in other['objects'] if x['field'] == field.lower()]
        c = target['fields'][field]['definite']
        require(root['fields'][field]['complete'] is True, 'root completeness')
        require(len(a) == len(b) == len(c) == count, 'complete definite counts')
        require(len({x['id'] for x in a}) == len({x['id'] for x in b}) == count, 'observer IDs')
        bm = {x['id']: x for x in b}
        expected = []
        for x in a:
            xb = x['bbox']; boxcheck(xb)
            require(x['status'] == 'definite_star', 'root classification')
            distances = []
            for y in b:
                yb = y['whole_ink_bbox']; boxcheck(yb)
                require(y['classification'] == 'definite_star_shaped_ink_mark', 'independent classification')
                d4 = sum((xb[k] + xb[k+2] - yb[k] - yb[k+2])**2 for k in (0, 1))
                distances.append((d4, y['id']))
            distances.sort()
            require(distances[0][0] < distances[1][0], 'unique nearest match')
            distance, yi = distances[0]; yb = bm[yi]['whole_ink_bbox']
            require(max(xb[0], yb[0]) <= min(xb[2], yb[2]) and
                    max(xb[1], yb[1]) <= min(xb[3], yb[3]), 'paired ink overlap')
            union = [min(xb[0], yb[0]), min(xb[1], yb[1]), max(xb[2], yb[2]), max(xb[3], yb[3])]
            expected.append({'id': x['id'], 'bbox': union, 'observer_ids': [x['id'], yi]})
            matched.append({'field': field, 'root': x['id'], 'independent': yi,
                            'squared_center_distance': distance / 4})
        require(len({x['observer_ids'][1] for x in expected}) == count, 'bijection')
        require(c == expected, 'union boxes/order changed')
    require(target['matching'] == matched, 'matching receipt')
    require(len(other['possible_objects']) == 1, 'uncertain inventory')
    u = other['possible_objects'][0]
    require(u['id'] == revisit['object_id'] == 'U001' and u['field'] == 'left', 'uncertain ID')
    require(u['whole_ink_bbox'] == revisit['whole_ink_bbox'], 'uncertain unchanged box')
    require(revisit['status'] == 'UNRESOLVED', 'uncertain status')
    require(target['fields']['LEFT']['uncertain'] == [dict(id='U001', bbox=u['whole_ink_bbox'],
                                                         status='unresolved_star_or_stain')], 'uncertain retained')
    require(target['fields']['MIDDLE']['uncertain'] == [], 'middle uncertainty')
    require(target['inventory_alternatives'] == {'LEFT': ['all29definite', 'all29definite_plus_U001'],
                                                'MIDDLE': ['all59definite']}, 'both alternatives')
    return target, {n: sha(directory / n) for n in names}


def exact_det(rows):
    n = len(rows)
    total = 0
    for p in it.permutations(range(n)):
        v = (-1)**sum(p[i] > p[j] for i in range(n) for j in range(i+1, n))
        for i, j in enumerate(p):
            v *= rows[i][j]
        total += v
    return total


def anchored(boxes, mode):
    # Translation by each actual anchor makes its row zero except the last1.
    # The shared uncertain anchor is overapproximated by interval subtraction.
    anchor = boxes[0]
    differences = []
    for b in boxes[1:]:
        x = (b[0]-anchor[2], b[2]-anchor[0])
        y = (b[1]-anchor[3], b[3]-anchor[1])
        differences.append((x, y, ref.add(ref.square(x), ref.square(y))))
    if mode == 'gnomonic':
        a,b = differences
        return ref.sub(ref.mul(a[0], b[1]), ref.mul(a[1], b[0]))
    require(mode == 'stereographic' and len(boxes) == 4, 'anchor mode')
    return ref.neg(ref.determinant3(differences))


def arithmetic_tests():
    ref.selftest()
    import prepare as implementation
    rng = Random(897)
    checks = 0
    for mode,k in [('gnomonic', 3), ('stereographic', 4)]:
        for _ in range(100):
            points = [(rng.randrange(-1000,1001), rng.randrange(-1000,1001)) for j in range(k)]
            rows = [[x,y,1] if k == 3 else [x,y,x*x+y*y,1] for x,y in points]
            want = exact_det(rows)
            boxes = [(x,y,x,y) for x,y in points]
            require(anchored(boxes,mode) == (want,want), 'exact anchor/raw-origin identity')
            require(ref.target_sign(boxes,mode) == ref.signs((want,want)), 'raw reference signs')
            require(implementation.target_mask(boxes,mode) == independent_target_mask(boxes,mode),
                    'implementation exact point mask')
            enlarged = [(x-rng.randrange(8),y-rng.randrange(8),x+rng.randrange(8),y+rng.randrange(8))
                        for x,y in points]
            require(implementation.target_mask(enlarged,mode) == independent_target_mask(enlarged,mode),
                    'implementation interval mask')
            lo,hi = anchored(enlarged,mode)
            for j in range(10):
                sample = [(rng.randint(a,c),rng.randint(b,d)) for a,b,c,d in enlarged]
                rows = [[x,y,1] if k == 3 else [x,y,x*x+y*y,1] for x,y in sample]
                value = exact_det(rows)
                require(lo <= value <= hi, 'integer sample containment')
                checks += 1
    for bad in (0.5, True, float('inf')):
        try:
            implementation.target_mask([(bad,0,1,1)]*3,'gnomonic')
        except (ValueError,TypeError):
            pass
        else:
            raise ValueError('inexact target input accepted')
    for k in (3,4):
        n = 5
        calc = lambda indices: (1 if sum(indices) % 2 else 4)
        values = implementation.tensor(n,k,calc)
        tensor_check(values,n,k,calc)
        for index in (0, sum(j*n**(k-j-1) for j in range(k))):
            corrupt = values.copy(); corrupt[index] = 7
            try:
                tensor_check(corrupt,n,k,calc)
            except ValueError:
                pass
            else:
                raise ValueError('tensor corruption not rejected')
    return checks


def interval_det(matrix):
    """Generic Laplace recursion, independent of preparation's specialized code."""
    if len(matrix) == 1:
        return matrix[0][0]
    result = (0, 0)
    for col in range(len(matrix)):
        minor = [[row[j] for j in range(len(matrix)) if j != col] for row in matrix[1:]]
        term = ref.mul(matrix[0][col], interval_det(minor))
        result = ref.add(result, ref.neg(term) if col % 2 else term)
    return result


def independent_target_mask(boxes, mode):
    a = boxes[0]
    matrix = []
    for b in boxes[1:]:
        dx = (b[0]-a[2], b[2]-a[0]); dy = (b[1]-a[3], b[3]-a[1])
        row = [dx, dy]
        if mode == 'stereographic':
            row.append(ref.add(ref.square(dx), ref.square(dy)))
        matrix.append(row)
    interval = interval_det(matrix)
    if mode == 'stereographic':
        interval = ref.neg(interval)
    return sum({-1: 1, 0: 2, 1: 4}[s] for s in ref.signs(interval))


def tensor_check(values, n, k, calculate):
    require(len(values) == n**k, 'complete tensor length')
    require(all(type(v) is int and 0 <= v <= 7 for v in values), 'tensor mask types')
    seen = bytearray(len(values))
    permutations = [(p, sum(p[i] > p[j] for i in range(k) for j in range(i+1,k)) % 2)
                    for p in it.permutations(range(k))]
    canonical = 0
    for indices in it.combinations(range(n), k):
        m = calculate(indices)
        require(m != 0, 'distinct-index empty sign enclosure')
        canonical += 1
        for p, odd in permutations:
            pos = sum(indices[p[j]] * n**(k-j-1) for j in range(k))
            expect = ((m & 1)*4 + (m & 2) + (m & 4)//4) if odd else m
            require(values[pos] == expect, 'canonical/permuted tensor cell')
            seen[pos] = 1
    require(all(seen[i] or value == 0 for i,value in enumerate(values)), 'repeated-index sentinel')
    return canonical, len(values)


def packet_check(path, directory):
    directory = Path(directory)
    target, provenance = inventory(directory)
    source_path = directory / 'SOURCE_UNITS.json'
    source = json.loads(source_path.read_bytes())
    lock = json.loads((directory / 'SOURCE_LOCK.json').read_bytes())
    require(sha(source_path) == lock['source_units_sha256'], 'source lock')
    require(source['raw_sha256'] == lock['raw']['sha256'] ==
            'd405be669287fb814aebc7a5dcde3a329afdcd34e8bb728314b6608142c0d75f', 'raw catalogue binding')
    raw = gzip.decompress(Path(path).read_bytes())
    packet = json.loads(raw)
    require(packet['schema'] == 'GDT897_SEARCH_PACKET_V1', 'packet schema')
    require(packet['source_sha256'] == sha(source_path), 'packet source hash')
    require(packet['target_sha256'] == provenance['TARGET_INVENTORY.json'], 'packet target hash')
    require(packet['mask_encoding'] == dict(negative=1, zero=2, positive=4, repeated_index=0), 'mask encoding')
    require(packet['flat_index'] == 'left-to-right base n', 'flat index')
    require(packet['source_vectors_scale'] == ref.SCALE, 'vector scale')
    records = {r['id']: r for r in source['records']}
    require(list(records) == list(range(1,1029)), 'source ordered IDs')
    units = {u['case_id']: u for u in source['units']}
    require(len(units) == 96, 'all source cases')
    # Independently reconstruct both complete source-authored memberships.
    expected_units = {}
    for c in range(1,49):
        for mode in ('FORMED','FULL'):
            expected_units[f'C{c:02d}:{mode}'] = [i for i,r in records.items()
                if r['constellation'] == c and (mode == 'FULL' or not r['outside'])]
    require(set(units) == set(expected_units), 'source case universe')
    require(all(units[c]['member_ids'] == v for c,v in expected_units.items()), 'source memberships')
    alternatives = {'LEFT29': target['fields']['LEFT']['definite'],
                    'LEFT30': target['fields']['LEFT']['definite'] + target['fields']['LEFT']['uncertain']}
    expected_cases = []
    expected_sources = set()
    target_masks = {}
    source_masks = {}
    canonical_checks = cell_checks = vector_checks = 0
    for target_id, objects in alternatives.items():
        n = len(objects)
        boxes = [[o['bbox'][0]*7993,o['bbox'][1]*3828,o['bbox'][2]*7993,o['bbox'][3]*3828]
                 for o in objects]
        for mode,k in [('gnomonic',3),('stereographic',4)]:
            key = target_id+':'+mode
            require(packet['targets'][key] == {'objects': [o['id'] for o in objects], 'boxes': boxes}, 'native target boxes')
            for unit in source['units']:
                if len(unit['member_ids']) != n:
                    continue
                case_id = target_id+'|'+unit['case_id']+'|'+mode
                expected_cases.append(case_id); expected_sources.add(unit['case_id'])
    require(set(packet['targets']) == {a+':'+m for a in alternatives for m in ('gnomonic','stereographic')}, 'target universe')
    require([c['case_id'] for c in packet['cases']] == expected_cases, 'all cases and order')
    require(set(packet['sources']) == expected_sources, 'eligible source universe')
    for name in sorted(expected_sources):
        members = units[name]['member_ids']
        vectors = [ref.source_vector(records[i]['longitude_arcmin'], records[i]['latitude_arcmin']) for i in members]
        require(packet['sources'][name] == {'member_ids':members,
                  'vectors':json.loads(json.dumps(vectors))}, 'rigorous source vectors')
        vector_checks += len(vectors)
    for case in packet['cases']:
        name,tid,mode = case['source_case'],case['target_id'],case['mode']
        require(case['case_id'] == tid+'|'+name+'|'+mode, 'case components')
        n = len(units[name]['member_ids']); k = 3 if mode == 'gnomonic' else 4
        require(case['n'] == n == len(alternatives[tid]), 'case cardinality')
        tk = tid+':'+mode; sk = name+':'+mode
        if tk not in target_masks:
            boxes = packet['targets'][tk]['boxes']
            a,b = tensor_check(case['target_masks'],n,k,
                    lambda t: independent_target_mask([boxes[i] for i in t],mode))
            canonical_checks += a; cell_checks += b
            target_masks[tk] = case['target_masks']
        else:
            require(case['target_masks'] == target_masks[tk], 'shared target masks')
        if sk not in source_masks:
            vectors = packet['sources'][name]['vectors']
            a,b = tensor_check(case['source_masks'],n,k,
                    lambda t: sum({-1:1,0:2,1:4}[s] for s in ref.source_sign([vectors[i] for i in t])))
            canonical_checks += a; cell_checks += b
            source_masks[sk] = case['source_masks']
        else:
            require(case['source_masks'] == source_masks[sk], 'shared source masks')
    maximum = max(map(len,expected_units.values()))
    require(len(target['fields']['MIDDLE']['definite']) > maximum, 'middle complete-count contradiction')
    require(packet['cardinality'] == {'MIDDLE': {'definite':59,'source_maximum':maximum,'status':'UNSAT_CARDINALITY'}}, 'middle receipt')
    return {'schema':'GDT897_GEOMETRY_VALIDATION_V1','status':'PASS',
            'scope':'inventory provenance and complete rigorous necessary-sign packet; no continuous projection or correspondence claim',
            'packet_sha256':sha(path),'source_sha256':sha(source_path),'inventory_hashes':provenance,
            'source_vectors_checked':vector_checks,'canonical_tuples_checked':canonical_checks,
            'tensor_cells_checked':cell_checks,'cases':len(expected_cases)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifacts',type=Path,default=Path(__file__).resolve().parents[1]/'artifacts')
    parser.add_argument('--packet',type=Path)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    samples = arithmetic_tests()
    if args.packet:
        result = packet_check(args.packet,args.artifacts)
    else:
        _,hashes = inventory(args.artifacts)
        result = {'status':'PASS','scope':'inventory and synthetic arithmetic only; packet not provided',
                  'inventory_hashes':hashes}
    result['strict_integer_sample_checks'] = samples
    result['sample_qualification'] = 'Regression only; rigor follows from interval algebra and exact identities.'
    raw = json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.output:
        args.output.write_text(raw)
    print(raw,end='')


if __name__ == '__main__':
    main()
