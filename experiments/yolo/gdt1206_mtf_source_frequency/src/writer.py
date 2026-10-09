"""Fixed MTF rule; no target-dependent settings or glyph carrier."""
import string


def encode(words, extra):
    order = list(string.ascii_lowercase)
    emitted = []
    for word in words:
        assert word
        group = []
        for char in word:
            if char in order:
                rank = order.index(char)
                group.append(rank)
                order.insert(0, order.pop(rank))
            else:
                group.append(26 + extra.index(char))
        emitted.append(group)
    return emitted


def decode(groups, extra):
    order = list(string.ascii_lowercase)
    words = []
    for group in groups:
        assert group
        letters = []
        for unit in group:
            assert isinstance(unit, int) and 0 <= unit < 26 + len(extra)
            if unit < 26:
                char = order.pop(unit)
                letters.append(char)
                order.insert(0, char)
            else:
                letters.append(extra[unit - 26])
        words.append(''.join(letters))
    return words
