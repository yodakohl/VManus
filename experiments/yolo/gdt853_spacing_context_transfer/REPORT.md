# GDT853 — no eligible held metadata pairs

**Capacity stop:25unspaced wholes qualify in discovery, but zero joined/split
pairs satisfy the complete held-folio metadata contract. No predictor was
computed or evaluated.** This is a limit of the selected comparator, not
evidence that spacing lacks information.

## Complete eligibility and gate results

| Partition | Joined one-group spans | Split two-group spans |
|---|---:|---:|
| Even-folio discovery |9476|7192|
| Odd-folio held |8846|6613|

There are32127eligible spans total. Spans may overlap; joined spans are not
duplicated for multiple proposed split points. Eligibility required plain
literal lowercase target and neighbor groups, definite internal and outer
boundaries, consecutive indices and one source line. Annotated groups were
excluded, never normalized. ZL3b only; no alternate-reader replication.

A W qualified only with at least2joined and2split discovery occurrences,
each class on at least2even-numbered physical folios.25W passed that rule.
The complete held pairing additionally fixed W, physical folio, selector,
kind, section, hand and exact starting group index. It produced0candidate
pairs before hashing, therefore0selected pairs and0selected W. No different
hash could change this zero-candidate outcome.

| Registered gate | Required | Observed |
|---|---|---|
| Selected held folios | At least8 |0; fail |
| Distinct selected W | At least3 |0; fail |
| Maximum one-W pair share | At most half, with nonempty selection | Undefined with0pairs; fail |

All three capacity gates fail. The scoring function was not called; no
predictor or scored-pair artifact exists, and the informative-folio and
accuracy thresholds were not evaluated. No UNKNOWN contribution, parameter
fitting, statistical test or semantic judgment entered the result.

## Every discovery-qualified W

J/S denotes joined/split occurrence counts. Discovery folio counts are
separate for the two classes. Held counts below describe retained individual
occurrences only; they are not relaxed pair counts or a rescue comparison.

| Exact unspaced W | Discovery J/S | Discovery folios J/S | Held J/S |
|---|---:|---:|---:|
| `araiin` |3/7|3/5|3/2|
| `arain` |2/2|2/2|1/2|
| `aral` |4/2|4/2|3/5|
| `chykchy` |2/2|2/2|0/1|
| `dalor` |4/2|3/2|2/0|
| `olaiin` |14/2|10/2|17/0|
| `olchdy` |4/2|4/2|0/1|
| `olchedy` |11/7|8/4|12/4|
| `olcheey` |4/2|3/2|2/3|
| `olchey` |4/2|4/2|10/3|
| `olkaiin` |12/3|9/3|12/0|
| `olor` |9/2|5/2|5/0|
| `ols` |4/3|4/3|3/1|
| `olshedy` |4/6|3/4|6/6|
| `oraiin` |6/9|6/6|9/11|
| `orar` |2/4|2/4|1/1|
| `otarar` |3/3|3/3|0/4|
| `qolchedy` |6/5|4/3|4/5|
| `raiin` |27/4|12/3|17/3|
| `rain` |6/4|2/3|5/2|
| `ral` |6/3|5/2|2/0|
| `saiin` |12/7|10/6|22/7|
| `sar` |7/4|5/4|8/1|
| `sor` |5/5|3/5|3/1|
| `ychedy` |3/2|2/2|1/0|

WHOLE_CAPACITY.json also retains every nonqualifying W and its discovery
counts/folios. OCCURRENCES.json contains full metadata and literal neighbors
for all occurrences of the25qualified W; HELD_PAIRS.json is empty. The
complete input remains the lossless GDT851 source file rather than a new
transcription. No relaxed metadata grouping was scored or searched here.

## Decision and reproduction

Stop this fixed spacing-context transfer test. It does not distinguish the
proposed mechanisms because its paired held comparison has no observations.
Do not widen index, page, hand, source, target spans, cuts or reader scope
as an automatic repair. A different design would need a separately justified
research decision and preregistration; none is proposed or executed here.

Registration827fee51 was public before the source was loaded. The frozen
GDT851 SOURCE_ZL3b hash was checked on execution. Its179selector scope and
explicit f84/f84r exclusions were retained. No source query, image or new
page was opened. Even/odd folios were already exposed in prior work; they
were never described as untouched manuscript confirmation.

The independent validator reconstructed source eligibility, every discovery
W count, the complete metadata-pair candidate set and the stopping decision.
It verified that scoring artifacts were absent. Cached replay was byte-identical;
source/result binding passed. Acquisition from cache, validation and replay
took approximately1.2seconds. The experiment stops without consuming the
remainder of its20-minute budget on an unregistered rescue.
