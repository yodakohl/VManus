# GDT588 — concrete carrier vocabulary is mostly mobile, but packet counts needed repair

## Result

The GDT587 noun choices are substantially more portable by occurrence than by
type. Of 1,243 concrete carrier assignments:

| foreign-page route | assignments | share |
|---|---:|---:|
| exact selection and packet context | 970 | 78.04% |
| same action×root cell and same lemma | 146 | 11.75% |
| register×root support only | 121 | 9.73% |
| register×root remains on one page | 6 | 0.48% |

Thus 1,116/1,243 assignments already retain the same contextual noun under the
same action cell on another page. All 146 second-tier cases keep the same
lemma: 138 differ only in carrier-root signature and eight only in packet rule.

The type view is less mature. There are 268 strict selection signatures, but
only 103 occur on more than one page. In other words, frequent working choices
travel well while many rare packet shapes remain singletons. Requiring support
from the same running/local layer gives the deliberately harsher profile
942/152/135/14.

## The 136 observed cells now have an honest transfer profile

| cell profile | cells |
|---|---:|
| every assignment exact elsewhere | 25 |
| partly exact elsewhere | 48 |
| cell crosses pages, signatures do not | 10 |
| single-page cell with register fallback | 51 |
| genuinely page-private cell | 2 |

The two private cells are Source `AIN` under `SH_SOURCE_REST` and
`T_SOURCE_FIX`, six assignments on f1r. Both still read `Teilmenge`; the missing
piece is a second Source page carrying `AIN`, not an empty meaning.

The strongest strict signature is Herbal `T_PHYSICAL_BROAD × Y →
Pflanzenmaterial` with 59 assignments on eleven pages. The most important
context split remains Biological `SH_BIO_BATHE × Y`: a clean host reads
`Körper`, while relation/form/address blockers retain `Stationsansatz`.

## A usable future-page contract now exists

The action gate contains 38 cards:

- 27 fixed GDT583 context rules may run automatically;
- two old source-ID-bound rules fall through on a future page;
- nine carrier-active GDT584 refinements require an explicit manual override.

The automatic rules yield 55 register contexts and 220 possible root cells.
Their declared routes are 111 observed action×root cells, 53
register-invariant fallbacks, and 56 broad register defaults. Every route is
nonempty. The executable host reader takes the complete already-segmented host,
not a raw Voynich surface, and preserves the full blocker test for body/station
readings.

## Packet transfer exposed one real reader defect

The eight special packet rules cover 121 carrier assignments at 74 hosts.
Fifty-five hosts have the same packet-rule×root-multiset on another page;
nineteen multisets remain page-local. The set-like GDT587 root signature hid a
different issue: thirteen hosts contain repeated written roots, and the fluent
sentence stated each noun only once.

The ledger and exact slot trace were already complete. GDT588 repairs only the
fluent channel, for example:

- `G407-S047`: `Ringposition; Ringsegment ×2; Positionswert`;
- `G407-S287`: `Körper; Teil ×2`;
- `G407-S670`: `Arzneiauszug ×2; Drogenmaterial ×2`;
- `P912-E1398`: `Beckeninhalt ×2`.

All thirteen repairs are installed in a complete 793-statement plus 744-card
reader; 782 statements and 742 local cards remain byte-identical to GDT587.
The `×2` marks count written carriers, not real-world objects.

## Bottom line

The concrete noun layer is ready for a restrained next-page attempt: reuse an
exact cell when available, accept only invariant register fallbacks for unseen
cells, otherwise stay broad, and never erase written multiplicity. GDT588 adds
no page or surface prediction and does not turn cross-page reuse into proof of
translation.

Validation passes 79/79 checks with a byte-identical rebuild.
