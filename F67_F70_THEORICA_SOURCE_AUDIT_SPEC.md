# TPQ001 — f67--f70 Theorica planetarum source audit

Date: 2026-08-10

## Question

Can the published proposal that seven circular Voynich diagrams form a
seven-planet sequence use Gotha Chart. A 472, or the canonical *Theorica
planetarum* tradition, as a one-to-one externally labelled seven-slot key?

This is a source audit, not a Voynich-string experiment. The source pages were
read before this audit was formalized, so this is not presented as a blind
preregistration. Its purpose is to prevent an exposed historical resemblance
from becoming an invented dictionary.

## Admitted evidence

- the public article that states the seven-planet/*Theorica* proposal;
- the official Gotha Chart. A 472 manuscript catalogue;
- a scholarly history of the canonical *Theorica* diagrams;
- the public voynich.nu Quire 9 catalogue and its already independently
  refreshed local v2 table.

Only human-authored HTML, born-digital PDF text, and the manual public
catalogue are read. No OCR, image model, automated image matching, Voynich
string, parsed root, or semantic score is admitted.

## Exact checks

1. Bind the retrieved bytes and the local v2 table by SHA-256 and size.
2. Recover the seven consecutive titles stated for Gotha f3r--f8r.
3. Count which of those titles are individual classical planets.
4. Recover the scholarly canonical diagram grouping.
5. Check the public Voynich descriptions for apparent Sun figures on f68v1
   and f70r2. This is only a uniqueness warning; it is not an authorial planet
   identification.
6. Record the Gotha catalogue date relative to the 1404--1438 parchment
   interval as a chronology diagnostic, not an impossibility proof.

## Decision

`STOP_NO_ONE_TO_ONE_THEORICA_LABEL_DONOR` if either the Gotha seven-title
sequence is not seven individual classical planets or the canonical
*Theorica* diagrams group multiple planets. The apparent duplicate-Sun and
chronology checks are supporting diagnostics only.

This stop rejects only an exact seven-slot label donation. It does not reject
an astronomical, cosmological, planetary, computistical, or instrumental role
for any Voynich diagram.

## Reopening criterion

Reopen only with a human-catalogued, contemporary or earlier witness that has
seven explicitly named one-to-one diagram units and a non-post-hoc order or
topology correspondence to the complete Voynich block. Generic circles,
volvelles, seven-item lists, or isolated Sun/Moon resemblance are insufficient.
