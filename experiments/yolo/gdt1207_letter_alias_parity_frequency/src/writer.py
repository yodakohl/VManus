"""Independent per-letter fixed aliases with one26-bit writer state."""

def encode(words, extra):
    state = 0
    emitted = []
    for word in words:
        assert word
        group = []
        for char in word:
            index = ord(char)-ord('a')
            if 0 <= index < 26:
                group.append(2*index+((state >> index) & 1))
                state ^= 1 << index
            else:
                group.append(52+extra.index(char))
        emitted.append(group)
    return emitted


def decode(groups, extra):
    state = 0
    words = []
    for group in groups:
        assert group
        letters = []
        for unit in group:
            assert type(unit) is int and 0 <= unit < 52+len(extra)
            if unit < 52:
                index, bit = divmod(unit,2)
                if bit != ((state >> index) & 1):
                    raise ValueError('Noncanonical alias parity')
                letters.append(chr(ord('a')+index))
                state ^= 1 << index
            else:
                letters.append(extra[unit-52])
        words.append(''.join(letters))
    return words
