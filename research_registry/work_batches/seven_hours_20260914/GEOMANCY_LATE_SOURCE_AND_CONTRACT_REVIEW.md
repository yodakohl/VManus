# Geomancy late source and IDEA129 contract review

## Source examined

Primary text: Robert Turner, *Henry Cornelius Agrippa, His Fourth Book of
Occult Philosophy: Of Geomancy* (London, 1655), attributed on the page to
Agrippa. The page is a late English translation of a pseudo-Agrippa text, not
an early fifteenth-century witness:
`https://www.princeton.edu/~ezb/geomancy/agrippa.html`.

The associated source figures are `hcafig1.gif` (named figures), `hcafig2.gif`
(mothers and daughters), `hcafig3.gif` (mothers and produced daughters), and
`hcafig4.gif` (the author's themed house arrangement). The local names image
is `geomancy_cache/turner1655_names.gif`.

## What the common procedure actually says

Turner first says that there are sixteen figure types and shows their names.
The named dictionary visible in the table is:

| Figure names in the source | Source association |
|---|---|
| The greater Fortune / Fortuna major; The lesser Fortune / Fortuna minor | Sun (diurnal / nocturnal qualification is described) |
| Via; Populus | Moon |
| Acquisitio; Laetitia | Jupiter |
| Puella; Amissio | Venus |
| Conjunctio; Albus | Mercury |
| Puer; Rubeus | Mars |
| Carcer; Tristitia | Saturn |
| Dragon's head / Caput Draconis; Dragon's tail / Cauda Draconis | their own natures |

The table supplies four-row dot figures beside the names. It is therefore
source evidence for a sixteen-type dictionary, but the image alone does not
label a target serialization direction. I retain the printed names and do
not normalize the table's dot orientation. There is also a textual
correspondence typo/variant: the zodiac paragraph says “Puella and Rubeus”
for Scorpio where the surrounding table and Mars pairing give Puer/Rubeus.
That does not alter the arithmetic procedure, but it is a reason to preserve
the source's alternate correspondence rather than silently repair it.

The common construction is explicit at the following levels:

1. Points are projected in four courses/lines, with each line reduced by
   even/uneven parity to a one- or two-point row. The resulting four figures
   are called *Matres* (mothers). The prose and diagrams establish four
   mothers, but do not give a modern unambiguous grid convention for whether
   a reader numbers the courses from the left or right, or mirrors the rows.
2. The four mothers are placed in order. Each corresponding course, read from
   the superior row through the two middle rows to the lowest, makes one
   *Filia* (daughter). In matrix notation this is the four-column transpose
   operation, subject to the unresolved left/right and top/bottom convention:
   if `M_i[r]` is row `r` of mother `i`, then daughter `F_r` has rows
   `(M_1[r], M_2[r], M_3[r], M_4[r])`. The source binds the corresponding-row
   operation; it does not by itself bind which physical edge is called the
   first column.
3. Combining two figures means combining corresponding rows by even/uneven
   parity: in binary terms, rowwise XOR. The common house/register order is:

   `1=M1, 2=M2, 3=M3, 4=M4, 5=F1, 6=F2, 7=F3, 8=F4,`
   `9=1 xor 2, 10=3 xor 4, 11=5 xor 6, 12=7 xor 8,`
   `13=9 xor 10, 14=11 xor 12, 15=13 xor 14 (Judge).`

   The text calls 13 and 14 the two Coadjutrices or Testes and 15 the Iudex.
   These are the seven parent pairs required by the common fifteen-position
   calculation. “Four input figures” means the four Matres; the source does
   not state a finite point count for each initial free line.

## The author's alternative arrangement

After presenting the common arrangement, Turner says it is neither wholly
rejected nor extolled and then gives what he calls the true figure according
to astrological reason. This is a distinct house-placement rule and must not
be fused with the common order above.

In that alternative, the four Matres occupy the four angles. The four Filiae
are assigned, in their stated order, to houses 2, 11, 8, and 1. The text then
gives these cadent constructions: house 9 from 4 and 5; house 6 from 10 and 2;
house 3 from 7 and 11; and house 12 from 4 and 8. The sentence's punctuation
and its phrase about “the rule of their triplicity” do not provide a clean
modern numbered serialization for every house without importing conventional
astrological house definitions. In particular, “first/second/third/fourth
angle” is not itself a numbered 1–4 list in the prose. The alternative is
therefore a declared rival arrangement, not evidence that the common
transpose/XOR order is the author's only or preferred computational program.

The page also gives two different triplicity correspondences and explicitly
says one is “rather to be observed” than another. This reinforces that the
named dictionary and the calculation graph are related source material, not a
single unambiguous semantic key.

## IDEA129 target-contract review

The proposed target scope—existing own-edition complete paragraphs containing
exactly fifteen complete groups, with observed paragraph boundaries defining
the population, no rolling windows, no skipped prose, no per-position keys,
and no f57v or reserves—is a valid *limited exploratory contract* if it is
registered as a hypothesis about those paragraphs. It tests whether one fixed
fifteen-position formal program can account for already admitted records. It
does not claim that the paragraphs are geomantic registers, and it does not
claim that the early Cod. Sang. 756 gate has passed.

Three conditions are necessary for that description to remain accurate:

* The runner must name the exact source candidate being tested: the common
  seven-XOR order above, the alternative house arrangement, or two separately
  reported candidates. A fit under the common order cannot be reported as a
  fit to the author's alternative arrangement.
* “Complete group” and the paragraph delimiter must be fixed before target
  reading, with physical page/edition provenance retained. A 15-token crop
  selected because it fits would be a different experiment. A paragraph with
  an incomplete first/last group is capacity/eligibility information, not a
  negative semantic result.
* The sixteen figure names and all dot rows must remain a source dictionary,
  while the target spelling-to-figure map remains an explicitly unknown
  injective hypothesis. No planetary, house, or question meaning should be
  inferred from a surviving arithmetic key.

The early source record remains a compatibility check only. The independent
Cod. Sang. 756 receipt (`proposals/geomancy_early_source/SOURCE_RULES_M.json`)
binds parity reduction, XV as judge, and witness checks, but explicitly does
not bind the full transpose, all seven construction pairs, or numbered
serialization. Its page-3 replay against one provisional vector therefore
cannot be upgraded into an early-source program PASS. The later Turner text
does provide a complete candidate common program, but its date and attribution
must be stated whenever an exploratory target result is reported.

## Decision

Proceeding with IDEA129 would be methodologically defensible only as a
late-source, common-program exploratory test under the fixed paragraph scope,
with the author's alternative arrangement retained as a separately declared
rival or explicitly excluded by design. It would be invalid to merge the two
house orders, to call the early 756 compatibility replay a source gate PASS, or
to translate a formal fit as a natural-language reading.
