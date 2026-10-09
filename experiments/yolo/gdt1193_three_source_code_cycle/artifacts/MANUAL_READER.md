# Blinded table-only reading

I read only `MANUAL_RULES.md`, `MANUAL_CHALLENGE.md`, and exact matching rows of `MANUAL_INVERSE.tsv`. Each lookup key was calculated by hand before an `rg` lookup. No decoder, generated lookup program, source corpus, expected answer, or other solution file was used. This is an assistant's manual reasoning exercise with electronic table search, not a trial with a medieval reader or a timed human participant.

For each row, rank = (initial position − incoming state) modulo 7. The outgoing state is (incoming state + the table's character count) modulo 6. E emits the pending source word; C retains it. Positions are zero based. Literal source spellings are preserved.

## A

| Group | Incoming | Style | Initial | Position | Rank | Tail | Literal fragment | Count | E/C | Outgoing | Emitted source word |
|---:|---:|---|---|---:|---:|---|---|---:|---|---:|---|
| 1 | 0 | recipe-first | cph | 6 | 6 | 01112 | des | 3 | E | 3 | des |
| 2 | 3 | ordinary | i | 0 | 4 | 220110 | ersten | 6 | E | 3 | ersten |
| 3 | 3 | ordinary | q | 1 | 5 | 1011 | von | 3 | E | 0 | von |
| 4 | 0 | ordinary | d | 2 | 2 | 11021 | hecht | 5 | E | 5 | hecht |
| 5 | 5 | ordinary | r | 5 | 0 | 0002122 | pratten | 7 | E | 0 | pratten |
| 6 | 0 | ordinary | k | 6 | 6 | 101121 | dv | 2 | E | 2 | dv |
| 7 | 2 | ordinary | q | 1 | 6 | 2111 | solt | 4 | E | 0 | solt |
| 8 | 0 | ordinary | y | 4 | 4 | 21102 | nemen | 5 | E | 5 | nemen |

Reconstructed words: `des ersten von hecht pratten dv solt nemen`

The previous decoded characters after these groups are s, n, n, t, n, v, t, n. None triggers the punctuation style. The counter returns to zero inside the block, but that does not restore the recipe-first style.

## B

| Group | Incoming | Style | Initial | Position | Rank | Tail | Literal fragment | Count | E/C | Outgoing | Emitted source word |
|---:|---:|---|---|---:|---:|---|---|---:|---|---:|---|
| 1 | 0 | recipe-first | p | 4 | 4 | 12201 | item | 4 | E | 4 | item |
| 2 | 4 | ordinary | k | 6 | 2 | 0202 | wild | 4 | C | 2 | —; pending wild |
| 3 | 2 | ordinary | i | 0 | 5 | 10122 | w | 1 | E | 3 | wildw |
| 4 | 3 | ordinary | r | 5 | 2 | 101 | machen | 6 | E | 3 | machen |
| 5 | 3 | ordinary | n | 3 | 0 | 002 | ein | 3 | E | 0 | ein |
| 6 | 0 | ordinary | y | 4 | 4 | 002011 | guet | 4 | E | 4 | guet |
| 7 | 4 | ordinary | i | 0 | 3 | 210202 | air | 3 | E | 1 | air |
| 8 | 1 | ordinary | k | 6 | 5 | 1011 | von | 3 | E | 4 | von |

Reconstructed words: `item wildw machen ein guet air von`

The previous decoded characters after these groups are m, d, w, n, n, t, r, n. None triggers the punctuation style. `wildw` is the literal concatenation of the two table fragments; I did not normalize it or supply a guessed missing word.

## Friction and limits

- Each of the sixteen groups required a table lookup. Exact electronic row search avoids the substantial burden of searching a 2,130-entry paper table; that burden was not tested here.
- The supplied glyph-separated display made the sign boundaries explicit. This does not test unaided reading of joined glyph-name strings, handwriting, or manuscript signs.
- The reader must maintain the source-character counter, switch between modulo 7 for the rank and modulo 6 for the state, preserve leading zeroes in tails, and use the final-position mapping rather than the interior mapping for the last sign.
- B requires retaining `wild` across a printed space, appending `w`, and emitting only then. Source-word boundaries are recovered by E/C, not by printed spaces.
- No unstated decoding rule was needed for these groups. The parent reported a correction of the prose about the one unused initial-map entry during the task; it did not change any lookup, equation, or answer.
- These examples exercise recipe-first and ordinary style, one continuation, and state wraparound. They do not exercise after-punctuation style, every dictionary entry, malformed groups, or long reading sessions.
- This result is a completed blinded reading, awaiting the parent's comparison with the sealed expected answer. It is neither a native Voynich translation nor an independent statistical test or evidence of medieval practicality.
