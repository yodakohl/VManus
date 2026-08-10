# F69M001 — f69v lunar-mansion prefix-equivalence topology

Status: **REGISTERED_UNSCORED**

## Narrow question and route exception

Public human catalogues define 28 inward radial labels on f69v in the complete
cyclic order `X1.1` through `X1.28` and mention the 28 lunar mansions as an
obvious possibility. A human-transcribed table supplies one fixed Latin roster
of Agrippa mansion names. Does the **pattern of which labels share prefixes**
align between these two ordered 28-item systems, without assigning sounds or
matching letters?

The generic NUMBER/CALENDAR route remains closed. This experiment satisfies
only its stated reopen condition—an explicit ordered coordinate—and tests one
narrow roster. Public discussion has already exposed the broad observations
that most roster names begin `A`, most Voynich labels begin EVA `o/y`, and the
roster contains four consecutive `Caad...` names. The method is therefore not
examiner-blind. No complete Voynich prefix-equivalence matrix or alignment
score was inspected before registration.

## Frozen inputs and representation

- `results/f69m001_capacity.json` fixes the 28 current loci, their Stolfi
  `X1.1..28` cyclic order, and the 28-name roster.
- `results/source_sta_family_consensus_loci.tsv` supplies one all-reading
  family sequence per locus. ZL3b/IT2a/RF1b are alternate readings, not three
  samples.
- For the historical name, lowercase ASCII letters and take the first word;
  for the Voynich label, take the complete consensus family sequence.
- At depths `k=1,2,3`, each item is represented only by its first `k` symbols.
  Exact letter/family identities are discarded. The response is the 378-entry
  binary vector over unordered item pairs: 1 when their prefixes are equal and
  0 otherwise.

No retained parser root/role, EVA spelling distance, phonetic mapping, member
code, English gloss, image feature, OCR, or automated vision output may enter.

## Frozen alignment statistic

For each prefix depth, compute the phi correlation between the historical and
Voynich pair-equality vectors. For each of the 28 cyclic rotations and both
directions, average the three phi values. Select the largest mean; break exact
ties by forward before reverse, then smallest rotation. Call it `S`. Every
depth must be nondegenerate.

The primary null has 8,192 deterministic full permutations of the 28 roster
items. A second 8,192-permutation nuisance null permutes roster items only
within their first-letter class, preserving the famous dominant-initial pattern
at every original roster position while scrambling deeper prefixes. For
assignment `a`, order donors by
`SHA256("F69M001|<NULL>|a|<position>")`; the conditional null applies this rule
separately within each first-letter class. Every null assignment is rescored
over all 56 dihedral alignments. Use plus-one p-values with tolerance `1e-15`.

## Frozen controls and gates

Before manuscript prefixes are opened, eight deterministic worlds must recover
a full three-depth equivalence plant and reject exact-null, dominant-first-
letter-only, four-name-block-only, and shallow-two-depth-only fixtures. Rotation,
reflection, anonymous family relabeling, and row serialization must preserve
the registered result. Duplicate, missing, wrong-ordinal, wrong-locus, too-
short, and unknown-family mutations must stop. An independent nonimporting
implementation must reconstruct all controls.

The one manuscript target confirms only if:

1. `S >= .25`;
2. full-permutation p <= `.01`;
3. first-letter-conditioned p <= `.05`;
4. all three selected-alignment phi values are positive and the depth-2 and
   depth-3 values are each at least `.25`; the initial `.15` draft was rejected
   target-blind because a fixture with correct depths 1--2 but deliberately
   scrambled depth 3 still attained `.168` and passed;
5. the best mean exceeds the second distinct dihedral mean by at least `.03`;
6. deleting any one item while retaining the selected original alignment gives
   mean phi at least `.15`;
7. all source, capacity, control, hash, finiteness, uniqueness, isolation, and
   independent-reconstruction gates pass.

No roster, normalization, depth, statistic, phase, direction, threshold, or
subset may change after target prefixes are opened. Runners-up and individual
prefix identities are diagnostic, not discoveries.

## Claim ceiling

On pass: the anonymous three-depth repeated-prefix topology of f69v aligns with
this fixed Latin lunar-mansion roster more strongly than full and dominant-
initial-conditioned permutation controls. This would support that roster as a
system-family candidate and justify a separately preregistered mapping test.

On failure: this exact prefix-topology representation does not support this
fixed roster. The 28-count remains compatible with lunar mansions, days, winds,
or another 28-part system.

Neither outcome identifies a mansion, name, letter, sound, word, language,
cipher, plaintext, or translation.
