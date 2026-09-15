# Common measure and two paths to a reduced fraction

2026-09-15; bounded source-only continuation, checkpoint 15:16 UTC.
Status: RAW_UNREVIEWED_NOT_SELECTED. No TP15 or target material accessed.

One distinct proposal is retained: a complete rational account can express
different calculation paths whose results agree in value and whose claimed
final representation is irreducible. The latter condition rejects a result
that is numerically correct but still has a common factor. This is a content
constraint, not another fixed-length division record or an alloy writer.

## Complete owned example from the existing scan

Fibonacci's Liber abbaci, revised 1228, Boncompagni's 1857 edition, printed
pp.50–51 / PDF pages57–58, chapter VI part1. The complete subsection starts
near the foot of p.50 with “Rursus si uolueris multiplicare” and ends on p.51
at the explicit end of the chapter part. Both complete pages were rendered
from the previously owned PDF and actually viewed natively during this review.
No new source was downloaded. The [existing public scan](https://archive.org/download/bub_gb_CrdUBgtAZFoC/bub_gb_CrdUBgtAZFoC.pdf)
has SHA-256 `e0617041071d181ae61a5109fc21ad48b8503927ed9f8f2a1378575de797ed1a`.
The exact cached text-layer excerpt is retained in the proposal, marked as OCR
with errors rather than a corrected diplomatic transcription. The native-page
render hashes are recorded there without distributing pixels or private paths.

The first complete construction multiplies `18 + 3/8` by `24 + 4/9`.
Source-written actions and assertions, including its alternative, are:

1. Multiply18 by8 and add3, obtaining147; multiply24 by9 and add4, obtaining220.
2. Multiply220 by147 and divide by the fraction denominators. Give whole449
   with the source's compound remainder notation, and a stated `pensa` of0
   modulo11. The checksum convention is not fully reconstructed here.
3. Explain the remainder by multiplying1 by8 and adding4, obtaining12, while
   multiplying8 by9 gives72. State12/72 as one sixth, invoking the proportion
   of whole to whole and corresponding parts, with a reference to Euclid.
4. Give a second path: use the third part of147, namely49, and the fourth part
   of220, namely55; divide their product by the corresponding third part of9,
   namely3, and fourth part of8, namely2. Division by6 gives the same449+1/6.
5. Explain reduction of a numerator and denominator by their greatest common
   measure. The written elementary examples include6/9 reduced to2/3 and
   5/10 reduced to1/2; both numerator and denominator are explicitly changed.
6. Give the general successive-remainder instruction, including the exact-
   division stopping case, first/second/further remainder cases, and the claim
   that the final common measure is greatest, citing Euclid's demonstrations.
7. Its worked pair22,10 gives remainder2 and then exact division of10 by2.
   Its worked pair20,12 gives remainder8, then12 divided by8 leaves4, and
   explicitly checks12 divided by4 as exact. The general register-reference
   wording must not be silently replaced by a modern trace.

The source also explains where the reduced numerator and denominator are
written above and below the fraction bar. That positional convention belongs
to its arithmetic exposition, not to a manuscript cipher. The displayed
base-case fraction in the general rule is retained in the source image/OCR;
its digits were not independently resolved in this bounded review. The two
explicitly narrated remainder examples above were read directly from the print.

## Written quantities versus derived checks

The following equalities are modern exact checks of the source actions:

```
(18 + 3/8)(24 + 4/9) = (147 * 220)/(8 * 9)
                       = 32340/72 = 449 + 12/72 = 449 + 1/6
(147/3)(220/4) / ((9/3)(8/4)) = (49 * 55)/(3 * 2)
                              = 2695/6 = 449 + 1/6
```

147,220,49,55,3,2,6,12,72,449 and the one-sixth result occur in the printed
explanation. The products32340 and2695 are our calculated values, not claimed
printed numbers. The quotient multipliers in
`22=2*10+2`, `10=5*2`, `20=1*12+8`, `12=1*8+4`, and `12=3*4`
are also our explicit arithmetic expansions of the narrated divisions.
The source's final12/4 check is preserved; it is not rewritten as8/4.

Under the stated greatest-common-measure claim, the pair20,12 has greatest
common divisor4. Thus reducing12/20 to3/5 is fully reduced. Reducing it to6/10
preserves exactly the same rational value but fails irreducibility. These two
reductions are our consequences of the printed pair and general rule, not an
additional printed worked comparison.

A newly generated account, explicitly not historical source text, reduces
84/126 directly by42 to2/3, or first by6 to14/21 and then by7 to2/3. Stopping
at14/21 preserves value but leaves a common factor7. This gives variable-length
complete paths without using a source event count as a paragraph length.

## Proposed meaning system and meaningful rivals

The prospective semantic language distinguishes positive integer quantities,
rational-value expressions, exact division/cancellation, remainder steps,
equivalence assertions, and a claim of complete reduction. A fraction keeps its
ordered numerator and denominator; simultaneous cancellation uses the same
nonzero factor in both. A common-measure claim must divide both quantities,
and a greatest claim must be supported by the remainder relation or an equivalent
complete certificate. No freely assigned real-valued label for each written
amount can substitute for the shared integer arithmetic.

For a modern conditional kernel, each division relation is `a=q*b+r` with
`0<=r<b`; a reused remainder keeps its identity, and successive active pairs
decrease until exact division. This is explicitly a modern semantic option.
The source's “larger/smaller” references and its12/4 final check do not supply
an unambiguous ready-made register serializer. A source-literal compiler would
need that reference audit first. The source proof call to Euclid is preserved;
the cited demonstrations were not newly acquired or silently inserted.

The three non-equivalent checks are:

- **Value alone:** accepts both12/20→3/5 and12/20→6/10.
- **Common divisor alone:** accepts dividing both numbers by2, although4 is
  their greatest common divisor.
- **Complete reduction:** requires value equality and a coprime final pair;
  it rejects6/10 and the generated14/21 stopping rival.

The cross-cancellation path also forces one divisor to act on a numerator and
a denominator. Dividing both numerator factors while leaving the denominator
unchanged does not preserve the product; merely seeing repeated division
operations is insufficient. These are multi-step semantic distinctions that
survive changes in prose order and explanation length. They do not establish
any numeric target spelling or predict that a complete paragraph begins with
two literal numbers. A globally shared writing/constituent grammar is still
unfrozen; no implicit filler, fixed opcode fields or source-order copy is proposed.

## Predecessors, symmetries and scope

The live route, numbers topic, bounded common-measure/gcd/antiphairesis/fraction
searches and division-route navigation were checked. Empty exact-term queries
were not treated as proof of absent research; the targeted arithmetic primary
was read. [GDT909](../../../experiments/yolo/gdt909_worked_division_chains/REPORT.md)
excludes its at-least-three equal-width steps within whole paragraphs, with four
single-group roles and literal transfers. That closed result is unchanged.
The present source does contain related division/remainder semantics; novelty
is not claimed for Euclidean division. The different proposed consequence is
value-preserving alternative calculation plus a separately asserted maximal/
irreducible endpoint, without selecting another writing template.

The earlier GDT902 and GDT969 work retains its fixed multiplication-copy and
generated root-trace contracts. [GDT971](../../../experiments/yolo/gdt971_alloy_numeral_binding_control/REPORT.md)
retains its source-known-role result and free-quantity-label counterexample:
arithmetic under known roles is not target meaning, and a second path need not
add discrimination in a particular code family. IDEA354's simultaneous grouping
has modular-residue ambiguity; this proposal instead constrains a canonical
rational representative. Neither predecessor is repaired or re-added.

Different common factors and paths can produce the same final rational; source
numerals and references must remain globally shared to constrain a reading.
Without a lowest-terms claim, unreduced equal fractions are legitimate and may
not be rejected. No source number system, modern decimal key, target owner or
common paragraph boundary is established. This is one raw source-supported
proposal with complete worked content and explicit uncertainty, not a target
decoder, experiment selection, global register edit or publication.
