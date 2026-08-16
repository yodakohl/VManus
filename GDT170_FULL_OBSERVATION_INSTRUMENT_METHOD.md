# GDT170 — full observation-layer synthetic instrument calibration

## Purpose

GDT168 showed that several host-context diagnostics cannot distinguish a true
short lexical codebook from a distributed record code.  GDT170 tests a harder
question: can the normal VManus surface-to-structure workflow recover either
known architecture when it is denied the encoder decomposition itself?

The two frozen GDT168 worlds and real medieval medical source are reused
without changing either encoder or any rendering key.  No parameter is chosen
from Voynich frequencies or outcomes and no Voynich source or image is read.

## Manuscript-like rendering

The already frozen generated groups are laid out mechanically as synthetic
folios.  Six generated records form a folio; each record occupies its original
one-to-three physical lines, with six groups per full line.  The ten aligned
register/scribe renderings remain alternate renderings of the same content,
not independent samples.

## Strict observation layer

`gdt170_observation_corpus.json.gz` may expose only information of a class
available to ordinary VManus work:

- anonymous world and witness identifiers;
- visible rendered source groups;
- confident source separators and physical line boundaries;
- folio, physical-line and within-line group order;
- visible paragraph-opening/continuation and paragraph-end layout roles;
- register and hand metadata;
- neutral, explicitly generated page/layout annotation tags.

It must not contain a concept ID, plaintext/source form, codebook value,
original source-unit identity, encoder slot, true host, true wrapper/frame,
true right/closure value, or true DY/B3 field.

## Sealed oracle

`gdt170_sealed_oracle.json.gz` contains the one-to-one observation join plus
all excluded truth: original medical form and concept, source unit, true record
and slot, canonical and rendered host, and every true encoder component.  The
oracle and codebook are hash committed before blind parsing.  The blind parser
and blind scorer are forbidden to import, name, or open either truth file.

## Frozen parsing levels

### SURFACE_ONLY

Uses rendered groups, separators and physical line/group order only.  It
copies the language-agnostic operation discovery/ranking used by the medieval
positive controls: recurring one-to-three-character left/right operations are
learned from exact surface contrasts, and up to the existing three HPR2 edge
layers are stripped only when the residual has recurrence support.  No
register, hand, paragraph, catalogue tag, or oracle value enters the parse.

### VMANUS_ANNOTATION_ASSISTED

Starts from the same candidate segmentations.  It may additionally use
register/hand and visible line/paragraph roles to prefer segmentations whose
edge operations have stable opening, line-closing, or paragraph-closing
distributions.  It still may not use concept identity, codebook, true record
slot, or any encoder field.

### ORACLE_CEILING

After blind outputs are frozen, uses the exact true encoder fields.  It is a
measurement ceiling, not a parser.

## Diagnostics

The blind pass runs the same diagnostic classes calibrated in GDT168:

- GDT113-style line/record closure and recurrence;
- GDT160 operation compatibility and pairing null;
- GDT162 short-host/codebook structure;
- GDT163 same-group substitution deltas;
- GDT164 parser-independent external substitution deltas;
- GDT165 next-host prediction;
- GDT166 unordered line-context prediction;
- GDT167 cross-register/scribe geometry alignment.

The unblind pass reports component segmentation accuracy, concept information
retained by inferred PAGE_HOST and inferred full tuple, held-source decoder
accuracy/coverage, and architecture classification against the oracle.

## Claim ceiling

This is an instrument calibration.  It may show which VManus diagnostics can
or cannot recover known synthetic lexical/distributed architectures through a
realistic observation boundary.  It establishes nothing about a Voynich word,
code value, language, role, meaning, plaintext, or translation.  f84r is not
an input and is not accessed.
