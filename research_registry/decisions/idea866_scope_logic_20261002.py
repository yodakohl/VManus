"""Illustrative logic only: no manuscript data or clinical efficacy model."""
import itertools

def rows():
    for hs, hl, bs, bl in itertools.product((False, True), repeat=4):
        dg = (not hs or bs) and (not hl or bl)
        ng = bs and (not hl or bl)
        joint = not (hs and hl) or (bs and bl)
        yield tuple(map(int, (hs, hl, bs, bl, dg, ng, joint)))

if __name__ == '__main__':
    result = list(rows())
    assert len(result) == 16
    assert all(not n or d for _, _, _, _, d, n, j in result)
    assert all(not d or j for _, _, _, _, d, n, j in result)
    assert any(d and not n for _, _, _, _, d, n, j in result)
    assert any(j and not d for _, _, _, _, d, n, j in result)
    print('Hs\tHl\tBs\tBl\tDg\tNg\tJ')
    for row in result:
        print('\t'.join(map(str, row)))
