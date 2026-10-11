# GDT1327 — the small-forward-step word wheel is excluded

**FORWARD_WORD_WHEEL_EXCLUDED_ALL_READINGS. Implementation validation PASS.**
A complete invented writer maps each lowercase source character or SPACE to a
forward step1..27 on a shared circular list of distinct whole codewords, and
writes the reached word. Exact repeats are explicit nulls. Its source inverse
works; the fixed native binding fails independently of every bank ordering.

| Reading | First qualifying page | Distinct forms V | Reciprocal pair | Qualifying pages |
|---|---|---:|---|---:|
| IT2a | f102r1 |59| dol / doleodaiin |65|
| RF1b | f103r |191| chal / okaiin |52|
| ZL3b | f102v2 |80| okey / shey |55|

IT2a f102r1.10G006–008 reads dol, doleodaiin, dol. ZL3b
f102v2.23G002–004 reads okey, shey, okey. RF1b has chal→okaiin
at f103r.31G004–005 and okaiin→chal at f103r.3G009–010. These
are exact transcription witnesses, not new image adjudications or glosses.
Selection was fixed as first lexicographic qualifying page/pair, not strongest
or prettiest example. Alternate readings are not independent manuscripts.

For different A,B, the two forward distances sum to the bank size M. Both must
be at most27, hence M<=54. But M>=V>54 on each selected page. Even page-specific
banks and arbitrary line-start anchors cannot satisfy this contradiction.
The existing words are only lower bounds on M; unobserved entries worsen it.
No ring-order search, sourcebook fit or native meanings are needed.

Validator rebuilt all61,181 strict group joins and46,836 original same-line
consecutive pairs from guarded GDT915 source windows, independently of the
runner's GDT1319 pair packet. All page summaries and selected witnesses match.
The writer/reader passes2,271 source-free roundtrips (all source lengths0..2,
three repeat-null counts);75 small ring cases and12,500 independently enumerated
index pairs verify the threshold. At M=2S the antipodal pair is feasible, so
this necessary bound does not exclude all wheels. These checks are same-author
engineering verification, plus a bounded source-free proof review; they are
not historical evidence. Probability p of repeat nulls is irrelevant to the bound.

The protocol uses one explicitly framed line per source message; the stated
multi-line/page option is a more permissive necessary-test relaxation with
paid anchors. No typographic newline is claimed as a source character.
The bank pays for word shapes and ordering; this writer never explained their
internal structure for free. No native source-language or actual bank was found.

Only unique whole-word bank positions, positive steps1..27 and exact repeated
current-word nulls are excluded under the retained packet/adjacency premises.
Signed or arbitrarily large jumps, duplicate printed forms at different places,
other kinds of nulls, hidden resets and changed boundaries are different
contracts, not tested or selected repairs. The elementary obstruction is not a
claim of new mathematics. A general stateful cipher remains open. No semantic
word boundaries or word meanings follow. Earlier1301/1217 failures are unchanged.

Decision: close IDEA995's stated native writer family; do not optimize its ring
ordering. Reopen only with independently supported changed binding or a genuinely
different complete writer and falsifier, not more search. No new image, reserve,
f84/f84r or f116v access; all inputs were previously exposed. No semantic relation
packet was scored. The full scoped protocol and assumption list are in METHOD.md.
