# GDT1334 — canonical two-port planning cannot merge observed whole units

**NONTRIVIAL_TWO_PORT_ALIAS_FAMILY_EXCLUDED in every reader.** Under the fixed
atomic22-unit binding, no pair of observed signs can be two variants of one body
in a global canonical minimum-join-cost writer with two entry/exit heights.
The proof covers all nontrivial body partitions through single-pair refinement;
it does not identify a native alphabet or exclude other handwriting systems.

| Reader | Groups / types | Pairs contradicted by identical actual flanks | Remaining pairs | Remaining pair/port branches, all UNSAT |
|---|---:|---:|---:|---:|
| IT2a | 22528 / 4272 | 223 | 8 | 96 |
| RF1b | 19321 / 3818 | 225 | 6 | 72 |
| ZL3b | 19332 / 3773 | 218 | 13 | 156 |

All231pairs and12ordered distinct port assignments per pair are covered in each
reader:7,992assignments by the local replacement proof and324by independently
verified2SAT. No SAT writer survives. Consequently the full-word check count
on native SAT witnesses is ZERO, not a successful forward reproduction claim.
The22-singleton identity writer remains trivial and outside this question.

## The human writing rule that was actually tested

Every visible working sign is hypothesized to be one complete letter body with
fixed entry and exit at LOW or HIGH. Variants of one body may have different
ports. The writer preserves source letters and word spaces, chooses the entire
word's variants to minimize incompatible joins, and writes a pen lift when needed.
Outer word ports are free. Equal-cost plans use a fixed lexicographic port-code
preference. There is no per-word table, page convention, extra internal stroke
cost, random choice, segmentation change or error correction.

This was a generous unknown-binding capacity family motivated by1001, not a
physical fit of that RAW's49allographs or a reading of native ink. Ports are
abstract possibilities, not observed pen trajectories. A real scribe could use
a different objective, uncertain units or optional conventions; none is tested
or installed as a post-result rescue here.

## Why a small exact calculation covers a global word planner

Refining all body classes to singletons except one pair deletes alternatives
without deleting any observed rendering. A canonical optimum stays optimal.
Thus every nontrivial larger alias system would imply a valid single-pair system.
For a single pair, only contiguous runs of that shared body can vary. Fixed
singleton signs split the total cost into independent run costs. Shared glyph
entry/exit bits still occur globally in the resulting constraints.

For every run and each possible outside port context, a two-state dynamic program
finds its unique canonical rendering. Each disallowed outside-bit combination
becomes a clause of at most two Boolean literals. Their conjunction is exactly
equivalent to global canonical rendering of all observed words. This is stronger
than checking single-center changes: hxxh can be locally stable but hyyh globally
better when x=LOW/LOW and y,h=HIGH/HIGH. The run reduction and refinement were
reviewed and fixed before native counting; no broad CEGIS search was implemented.

The original1295literal conflicts remain, but here the uniform rule also matches
identical visible flanks across different pages, lengths and positions.1310's
additional SOURCE-neighbor merger conflicts were not silently imported. Its
arbitrary context lookup witnesses belong to a different forward-rule family.
Passing separate pairs would not have proved joint compatibility.

## Concrete post-result explanation: n/q

n/q survives the initial visible-flank screen in all three readers, making it a
useful illustration of why that screen alone is insufficient. All twelve port
assignments fail. After the main result, all36reader/assignment branches were
reduced to inclusion-minimal contradictory clause sets. These are not minimum
numbers of erroneous words or newly selected experimental success criteria.

For example, suppose n=LOW/LOW and q=HIGH/HIGH. In ZL and IT, the actual complete
forms `chon` (f37v.3) and `oqaiin` (f103v.18) already contradict this assignment.
The terminal n after o in chon requires o's exit LOW; otherwise q would join
better. But with that LOWexit, the q after o in oqaiin cannot beat n: if the next
entry is LOW, n costs less; if HIGH, costs tie and n wins the fixed preference.
Thus oqaiin requires the same o exit HIGH. RF supplies chon and oqd(f44r.7) for
the corresponding contradiction. No meaning is assigned to these forms.

Another branch, n=LOW/LOW and q=HIGH/LOW, already cannot write an initial q:
with a free left edge the two variants have identical future cost, and n wins
the tie. The saved qaiin/qaedy examples certify that narrow obstruction. The
other assignments are not inferred from these examples; their own complete
certificates are retained. All96original run certificates were independently
checked against the frozen groups, explicit rendering enumeration and brute
truth tables. Native source images were not consulted.

## Boundaries of the conclusion

This excludes alias identifications BETWEEN observed working units only under
the exact one-body-per-unit, fixed-port, equal internal-cost, canonical-selection
contract. It does not exclude true ligatures containing several source letters,
other segmentation, unobserved variants, stochastic spelling, non-port-dependent
allography or meanings. It does not make the working22units phonemes. The source
word frequencies would be preserved by the deterministic injective family; old
fixed-source distribution failures remain separately binding.

No uncertainty budget was granted. Rare readings were retained; these exact
proofs do not estimate copying/transcription error rates or show robustness to
changes of the data.1332's distinction between exact constraints and historical
plausibility remains essential. No larger port alphabet, new cost weights,
exception removal, page-specific rule or source-language decoder is selected.
1001remains a coherent symbolic teaching writer with missing native physical
binding, not a successful or universally disproved historical script.

## Reproduction and validation

The primary SCC solver and independent Z3solver agree on every remaining branch.
The independent program resegmented every raw group and verified all61,181original
915joins,666literal pair contradictions and324port decisions. The pre-run fixtures
compare648run cases with exhaustive renderings and900small2CNFs with brute truth
tables. The independent validator additionally checks540run cases exhaustively.
A separate post-result program retains n/qclause certificates; its checker imports
no main solver and uses brute truth tables and2^run rendering enumeration.

The report of two independent algorithms is computational only: both main code
paths are root-authored; the bounded proof review had no new1334native data.
No new manuscript text, mixed TSV, image, reserve, language source or semantic
packet was opened. Original frozen groups and all residual witnesses remain.
Use the two manifest commands. Their wrappers run the locked primary/checker
and then the explicitly post-result explanatory certificate/checker, which did
not select the main decision. Wrappers were added after results solely because
the repository manifest permits exactly run/validate command fields.
