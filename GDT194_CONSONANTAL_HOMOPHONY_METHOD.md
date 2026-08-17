# GDT194 — compiler-stripped consonantal homophony

## Question and frozen model

GDT193 found that a consonant-only target is less incompatible than literal
alphabetic text, but its injective key still failed. GDT194 allows multiple
active PAGE_HOST signs to emit the same one-letter consonant.

Use the identical non-f84 PAGE_HOST source stream, six consonant-only language
models, and three retained GDT193 mappings. For each active sign, exhaustively
test all 21 consonants until one-coordinate local optimality. Pay
`20 log2(21)` mapping bits, `log2(6)` language bits, and an exact
Dirichlet-1/2 reverse-source channel for every collided consonant. Physical
lines and source SPACE remain fixed. Compare with the identical anonymous
order-2 KT source channel.

Pass requires a negative paid gap and one identical map across all starts.
This tests fixed global consonantal homophony only, not context-dependent
restoration, syllabograms, page keys, or word/phrase codes. Target consonants
are optimizer states, not sound assignments. Every `f84*` row is rejected
before parsing.
