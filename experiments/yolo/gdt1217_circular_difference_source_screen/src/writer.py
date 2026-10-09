"""The fixed IDEA948 lesson; numeric working glyph IDs, no key fitting."""


def encode(words, escape_characters, start=0):
    if start not in range(21):
        raise ValueError('illegal complete-word entry')
    indices = {c: i for i, c in enumerate(escape_characters)}
    p = start
    out = []
    for word in words:
        if not word:
            raise ValueError('empty word')
        group = []
        for char in word:
            if 'a' <= char <= 'u':
                units = [ord(char) - ord('a')]
            elif char in indices:
                j = indices[char]
                units = [21, j // 21, j % 21]
            else:
                raise ValueError('unsupported character')
            for u in units:
                group.append((u - p) % 22)
                p = u
        out.append(group)
    return out


def decode(groups, escape_characters, start=0):
    if start not in range(21):
        raise ValueError('illegal complete-word entry')
    p = start
    words = []
    for group in groups:
        if not group:
            raise ValueError('empty group')
        units = []
        for delta in group:
            if type(delta) is not int or not 0 <= delta < 22:
                raise ValueError('illegal distance')
            p = (p + delta) % 22
            units.append(p)
        word = []
        i = 0
        while i < len(units):
            u = units[i]
            if u < 21:
                word.append(chr(ord('a') + u))
                i += 1
            else:
                if i + 2 >= len(units):
                    raise ValueError('incomplete escape')
                b, c = units[i+1:i+3]
                j = 21*b + c
                if b == 21 or c == 21 or j >= len(escape_characters):
                    raise ValueError('illegal escape')
                word.append(escape_characters[j])
                i += 3
        words.append(''.join(word))
    return words
