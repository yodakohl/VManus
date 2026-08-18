# GDT322 — executable opaque-cell renderer grammar

This artifact compiles the independently transferable GDT321 wrapper layer
without assigning linguistic or semantic meaning.

For an already known opaque compatibility cell `C`, visible wrapper `w`,
physical-line-start indicator `L`, and immediately-preceding-group-DY
indicator `D`, use

```text
score(w) = log(n[C,w] + 1/2)
         + 1[w=s] * beta_s * L
         + 1[w=q] * beta_q * D
P(w | C,L,D) = softmax_w(score(w))
```

The fixed wrapper inventory is `NONE, ch, che, d, q, s, sh, t`. The published
opaque lexicon covers exactly the 126 GDT318 cells. It is intentionally a
memorized compatibility table: a missing cell is `UNLICENSED_OR_UNKNOWN`, not
an invitation to infer a wrapper from host glyphs.

`beta_s` and `beta_q` are descriptive full-panel estimates for generation and
inspection. Predictive performance is the leave-one-folio-out GDT321 result,
not the in-sample fit. The t and d secondary rules failed GDT319/GDT320 and are
absent.

This grammar is a stochastic formal renderer only. `s`, `q`, cells, and
boundaries receive no morpheme, POS, meaning, sound, language, plaintext, or
translation. No f84 row may be opened, parsed, retained, joined, or scored.
