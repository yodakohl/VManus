"""Exact incremental integer row lattices, with original-row certificates.

No manuscript data or third-party packages are used here.  A returned basis H
is accompanied by sparse integer rows C satisfying C * input_rows = H.  If H
is the identity, that equality alone certifies the unit lattice independently
of this implementation's reduction algorithm.
"""


def _egcd(a, b):
    """Return positive gcd g and integers s,t with s*a + t*b == g."""
    aa, bb = abs(a), abs(b)
    old_r, r = aa, bb
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    return old_r, old_s * (1 if a >= 0 else -1), old_t * (1 if b >= 0 else -1)


def _combine(a, left, b, right):
    result = {i: a * value for i, value in left.items() if a * value}
    for i, value in right.items():
        total = result.get(i, 0) + b * value
        if total:
            result[i] = total
        else:
            result.pop(i, None)
    return result


def _row_hnf(rows, coefficients, dimension):
    """Unimodular integer row operations; discard only zero basis rows."""
    pivot_row = 0
    for column in range(dimension):
        found = next((i for i in range(pivot_row, len(rows)) if rows[i][column]), None)
        if found is None:
            continue
        rows[pivot_row], rows[found] = rows[found], rows[pivot_row]
        coefficients[pivot_row], coefficients[found] = coefficients[found], coefficients[pivot_row]
        for i in range(pivot_row + 1, len(rows)):
            b = rows[i][column]
            if not b:
                continue
            a = rows[pivot_row][column]
            g, s, t = _egcd(a, b)
            left, right = rows[pivot_row], rows[i]
            lc, rc = coefficients[pivot_row], coefficients[i]
            rows[pivot_row] = [s * x + t * y for x, y in zip(left, right)]
            rows[i] = [-(b // g) * x + (a // g) * y for x, y in zip(left, right)]
            coefficients[pivot_row] = _combine(s, lc, t, rc)
            coefficients[i] = _combine(-(b // g), lc, a // g, rc)
        if rows[pivot_row][column] < 0:
            rows[pivot_row] = [-x for x in rows[pivot_row]]
            coefficients[pivot_row] = {i: -x for i, x in coefficients[pivot_row].items()}
        pivot = rows[pivot_row][column]
        for i in range(pivot_row):
            q = rows[i][column] // pivot
            if q:
                rows[i] = [x - q * y for x, y in zip(rows[i], rows[pivot_row])]
                coefficients[i] = _combine(1, coefficients[i], -q, coefficients[pivot_row])
        pivot_row += 1
        if pivot_row == len(rows):
            break
    assert all(not any(row) for row in rows[pivot_row:])
    return rows[:pivot_row], coefficients[:pivot_row]


def analyze(rows, dimension):
    """Return a JSON-serializable certified row basis, in input source order.

    Sparse coefficient row keys are stringified zero-based input row indices.
    `index` is null for a rank-deficient lattice, otherwise [Z^dimension : L].
    The input iterator is not consumed further once the unit lattice is proved.
    `used_indices` lists the rows present in the final certificate, while
    `rows_processed` counts all rows consumed, including dependent rows.
    """
    if type(dimension) is not int or dimension < 0:
        raise ValueError("dimension must be a nonnegative integer")
    basis, coefficients = [], []
    processed = 0
    identity = [[int(i == j) for j in range(dimension)] for i in range(dimension)]
    if dimension:
        for index, original in enumerate(rows):
            row = list(original)
            if len(row) != dimension or any(type(x) is not int for x in row):
                raise ValueError("input rows must have exactly dimension integer entries")
            processed = index + 1
            if any(row):
                basis.append(row)
                coefficients.append({index: 1})
                basis, coefficients = _row_hnf(basis, coefficients, dimension)
            if basis == identity:
                break
    rank = len(basis)
    index = None
    if rank == dimension:
        index = 1
        for i in range(dimension):
            index *= basis[i][i]
        assert index > 0
    return {
        "dimension": dimension,
        "rank": rank,
        "index": index,
        "unit_lattice": basis == identity,
        "basis": basis,
        "coefficients": [{str(i): value for i, value in sorted(row.items())} for row in coefficients],
        "used_indices": sorted({i for row in coefficients for i in row}),
        "rows_processed": processed,
    }


def selftest():
    """Four independent arithmetic cases, with exact certificate replay."""
    cases = [
        # No single 2x2 input minor has determinant +/-1; gcd(6,2,3)=1.
        ("unit_lattice_requires_integer_combinations", [[2, 0], [0, 3], [1, 1]], 2, 2, 1, None),
        ("torsion_two", [[4], [6]], 1, 1, 2, ([1], 2)),
        ("free_dimension", [[1, -1, 0], [2, -2, 0]], 3, 1, None, ([1, 1, 0], None)),
        # Rational full rank does not exclude nonzero modular weights.
        ("rational_full_rank_with_torsion_six", [[2, 1], [0, 3]], 2, 2, 6, ([1, 0], 2)),
    ]
    results = []
    for name, rows, dimension, rank, index, witness in cases:
        result = analyze(rows, dimension)
        assert result["rank"] == rank, name
        assert result["index"] == index, name
        for basis_row, coefficient_row in zip(result["basis"], result["coefficients"]):
            replay = [sum(value * rows[int(i)][j] for i, value in coefficient_row.items()) for j in range(dimension)]
            assert replay == basis_row, name
        if witness:
            weights, modulus = witness
            assert any(weights), name
            for row in rows:
                value = sum(x * w for x, w in zip(row, weights))
                assert (value % modulus == 0) if modulus else (value == 0), name
        else:
            assert result["basis"] == [[1, 0], [0, 1]], name
        results.append({"case": name, "status": "PASS", "rank": rank, "index": index})
    return results


if __name__ == "__main__":
    import json

    print(json.dumps(selftest(), indent=2))
