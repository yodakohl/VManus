# GDT1238 — necessary runs in previous-written-glyph tables

Let a source word x1...xn produce y1...yn, one sign per source letter.
At a noninitial position t, yt=f_(y[t-1])(xt), with one fixed injective row
for each previous output sign. A word-entry/reset row is arbitrary but fixed
where used. No interior reset, extra state, position row, deletion or expansion
is permitted. Word or paragraph entry conventions do not affect the proof.

If y[a]...y[a+k-1]=g^k, then for every j=a+1...a+k-1 the same row f_g
has output g. Injectivity forces x[j]=f_g^(-1)(g), one constant letter.
The first source letter of the run need not equal that letter: its preceding
output may differ or it may use the reset row. Thus a k-sign output run
requires at least k-1 consecutive equal source letters. A two-sign output
run imposes no source repetition; a three-sign run does. Reversing whole
source words leaves maximal run lengths unchanged. Arbitrary global glyph
renaming preserves the obstruction.

If a source population has maximum same-letter run R, every one of its word
outputs, under any permitted entering row/state and any row tables, has
maximum run at most R+1. This is a form-envelope consequence. It does not
equate the source population's word count/frequencies with a larger target
cache or claim a particular native word aligns with a particular source word.
It also does not exclude unknown source words with larger runs.

The primary manuscript-side result is the required source run bound, separately
in each reading, with exact full-form support. The secondary fixed Deot
comparison can reject coverage of any out-of-envelope native word by that
projection under this writer, or remain inconclusive. It is not a new native
language choice, a full statistical test or an encoder.

A recurrent output substring has a fixed decoded suffix from its second
sign onward. Its first decoded letter can depend on the incoming sign.
This limited structural property is not a proof of a complete native stem
meaning or a morpheme boundary.

GDT001's previous_context.py already indexed observed previous glyphs despite
its preceding-source wording. Its unrestricted27-value inverse search and
STOP_PREVIOUS_CONTEXT_UNSTABLE are retained. GDT1230 instead constrained the
previous decoded source letter; its entropy theorem is not imported here.
The new contribution is a cheap necessary run falsifier, not a new cipher
mechanism or an optimizer repair.
