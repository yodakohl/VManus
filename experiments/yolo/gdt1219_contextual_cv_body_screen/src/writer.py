"""The complete fixed body/continuation contract. Numeric working glyphs."""
from collections import Counter

VOWELS = 'aeiouy'
CONSONANTS = 'bcdfghjklmnpqrstvwxz'
ORDINARY = 'bcdfghklmnpqrstvxz'
GLYPHS = ['a','o','n','d','y','s','r','l','m','k','t','p','f','ch','sh','ckh','cth','cph','cfh','q','e','i']
CHOICES = ['', *VOWELS]
MARKS = [[], [20], [20,20], [20,20,20], [21], [21,21], [21,21,21]]
CARRIER = '@'
ROWS = [*CONSONANTS, CARRIER]


def atoms(word, extras):
    pos = 0
    while pos < len(word):
        c = word[pos]
        pos += 1
        if c in CONSONANTS:
            v = ''
            if pos < len(word) and word[pos] in VOWELS:
                v = word[pos]
                pos += 1
            yield c, v
        elif c in VOWELS:
            yield CARRIER, c
        elif c in extras:
            yield '#', c
        else:
            raise ValueError('unsupported source character')


def train(source, extras):
    counts = {s: {b: Counter() for b in ROWS} for s in VOWELS}
    for book in ('b4', 'w1'):
        for recipe in source[book]:
            state = 'a'
            for word in recipe['words']:
                for body, v in atoms(word, extras):
                    if body != '#':
                        counts[state][body][v] += 1
                        if v:
                            state = v
    table = {}
    for state in VOWELS:
        table[state] = {}
        for body in ROWS:
            allowed = CHOICES[1:] if body == CARRIER else CHOICES
            table[state][body] = max(allowed, key=lambda v: counts[state][body][v])
    return table, {s: {b: dict(counts[s][b]) for b in ROWS} for s in VOWELS}


def continuation_order(default):
    return [default] + [v for v in CHOICES if v != default]


def encode(words, extras, table, start='a'):
    state = start
    output = []
    for word in words:
        if not word:
            raise ValueError('empty source word')
        group = []
        for body, v in atoms(word, extras):
            if body == '#':
                index = extras.index(v)
                group.extend([19,1,3,index//19,index%19])
                continue
            mark = MARKS[continuation_order(table[state][body]).index(v)]
            if body == 'j':
                base = [19,1,0]
            elif body == 'w':
                base = [19,1,2]
            elif body == CARRIER:
                base = [] if not group and mark else [18]
            else:
                base = [ORDINARY.index(body)]
            group.extend(base+mark)
            if v:
                state = v
        assert group
        output.append(group)
    return output


def decode(groups, extras, table, start='a', canonical=True):
    state = start
    words = []
    for group in groups:
        if not group or any(type(x) is not int or x < 0 or x >= 22 for x in group):
            raise ValueError('invalid group/glyph')
        pos = 0
        out = []
        while pos < len(group):
            leading = pos == 0 and group[pos] in (20,21)
            if leading:
                body = CARRIER
            elif group[pos] == 19:
                if pos+2 >= len(group) or group[pos+1] != 1:
                    raise ValueError('incomplete q escape/guard')
                selector = group[pos+2]
                if selector == 3:
                    if pos+4 >= len(group) or any(x >= 19 for x in group[pos+3:pos+5]):
                        raise ValueError('bad literal escape digits')
                    index = group[pos+3]*19+group[pos+4]
                    if index >= len(extras):
                        raise ValueError('out-of-range literal escape')
                    out.append(extras[index])
                    pos += 5
                    continue
                if selector not in (0,2):
                    raise ValueError('bad consonant escape selector')
                body = 'j' if selector == 0 else 'w'
                pos += 3
            elif group[pos] < 19:
                body = CARRIER if group[pos] == 18 else ORDINARY[group[pos]]
                pos += 1
            else:
                raise ValueError('modifier without body')
            end = pos
            while end < len(group) and group[end] in (20,21):
                end += 1
            run = group[pos:end]
            if run not in MARKS:
                raise ValueError('mixed/overlong modifier')
            choice = continuation_order(table[state][body])[MARKS.index(run)]
            if body == CARRIER:
                if not choice:
                    raise ValueError('NONE carrier')
                out.append(choice)
            else:
                out.append(body+choice)
            if choice:
                state = choice
            pos = end
        words.append(''.join(out))
    if canonical and encode(words, extras, table, start) != groups:
        raise ValueError('noncanonical grouping/carrier')
    return words
