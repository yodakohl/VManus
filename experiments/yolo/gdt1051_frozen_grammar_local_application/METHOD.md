# GDT1051 method

## Question and registration

Does applying the project's already frozen formal word structure to the
complete saved f68r2 ring and f89v1 paragraph packets preserve the proposed
`okaiin`/`okoaiin` family identity or expose distinctions that a future
meaning hypothesis must explain? [Registration](PREREGISTRATION.md) fixes
the scope, alternatives and work budget before this execution.

## Inputs and scope

The published ring and paragraph source JSONs are referenced by byte hash in
[RESULT.json](artifacts/RESULT.json). Their selector-first guarded exports
contain 58 ring groups (six reader/locus units) and 230 paragraph groups
(24 reader/locus units). No new transcription query is needed. They are known
development data, not reserved confirmation. f84/f84r are sealed.

The fixed GDT605 merge file has 64 ordered rules. The imported
`collapse`/`apply_bpe`, GDT012 `strip_layers`, and GDT062 `preparse` functions
are used unchanged and bound by source-file hashes. No learner is called.

## Complete transformation

Every original group remains in the output with its reader, locus, position,
raw spelling and both source separator classes. Only lowercase a–z groups
enter the formal transforms. Groups with uncertainty marks/entities remain
unresolved. Within each line, groups separated by `UNCERTAIN_SMALL_SPACE` are
concatenated for BPE; definite spaces and line ends remain hard boundaries.
All 279 resulting hard chunks are saved, including 19 containing marked
groups; the 260 eligible chunks receive final units and recursive ordered
merge trees. BPE segmentation is lossless for its collapsed spelling.

GDT012 and the fixed part of GDT062 are applied to each eligible original
group. The later GDT062 O/OT local-frame stage **learns** a license set from
its input inventory. It is not refitted here; every newly computed group
explicitly marks that stage as not frozen for new input. GDT062's published
inventory is a predecessor cross-check for rows it actually contains.
There is no stripping rule beyond the unchanged, registered functions.

No probabilities are assigned to these local outputs. Position/entry effects
from GDT286/318 remain constraints, not deterministic glosses. GDT608's exact
pair residual, GDT326's failed unseen recombination and GDT915/916's narrow
known-family transfer bound interpretation. The two representations do not
share a proven linguistic morpheme inventory.

## Validation and decision ceiling

The validator matches all 288 saved source rows by exact reader/locus/index,
all separators and all 279 chunks, reapplies the unchanged pure functions,
checks all64 merge rules and their trees, and reconstructs the four target
forms. Its PASS means faithful formal replay and complete packet coverage.
It cannot validate a word meaning, prefix function, phonetic alphabet,
sentence, SUN hypothesis or historical language.
