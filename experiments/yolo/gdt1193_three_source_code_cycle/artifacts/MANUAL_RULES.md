# Manual rules for the artificial writer

Working glyphs: a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh

Start each recipe with state 0 and no previous character. For each group select style: recipe-first if no previous character; after-punctuation if the previous decoded character is one of . , ; : ! ?; otherwise ordinary. Line wraps do not reset anything.

| Position (zero based) | Ordinary | Recipe-first | After-punctuation |
|---:|---|---|---|
| 0 | i | ch | t |
| 1 | q | ckh | s |
| 2 | d | o | a |
| 3 | n | cfh | cth |
| 4 | y | p | l |
| 5 | r | f | sh |
| 6 | k | cph | m |

Find the first glyph in the applicable row/column bank. If its position is p, the dictionary rank is (p − state) modulo 7 (use a result from 0 to 6). The remaining 22nd entry of the full initial map has no role as an initial.

| Digit | Interior glyph | Final glyph: word ends | Final glyph: word continues |
|---:|---|---|---|
| 0 | o | y | t |
| 1 | e | ch | s |
| 2 | a | l | i |

Read all glyphs after the initial as digits, using the interior column except for the last glyph. The final glyph identifies both its digit and whether the source word ends. The full digit string is the tail. Look up (rank, tail) in MANUAL_INVERSE.tsv. The source_json field is a literal source fragment, not a Voynich meaning. Append the fragment to the pending source word. At an end-final emit that word and clear the pending word.

Then add the character_count of that fragment to the counter and take modulo 6. Set previous character to the fragment’s last decoded character. Repeat. Source spaces do not increment the counter.

For writing, scan each source word from left to right and choose the longest dictionary fragment matching the remaining letters (down to one character). Look up its rank and tail. Use initial position (rank + state) modulo 7 in the applicable style bank. Interior digits use the interior column; the last digit uses end or continue according to whether this fragment completes the source word. Update state as above. A blank recipe boundary resets it.

The full dictionary has 2,130 entries. The procedural steps are small; preparing, copying and searching that table is a substantial cost. A short correct manual read does not establish medieval practicality.
