# GDT006 blinded cut-review report

## Outcome

**STOP_LOCALIZATION_CAPACITY_3_OF_34_NO_BLIND_REVIEW.**

The use of a fresh blinded subagent was authorized and registered. The
source-aware localizer then found that the planned packet did not have a valid
matched physical basis:

| Arm | Registered cuts | Securely localized | Unresolved |
|---|---:|---:|---:|
| target | 17 | 3 | 14 |
| control | 17 | 0 | 17 |
| total | 34 | 3 | 31 |

Five control pseudo-cuts fall inside one STA sign rather than at a source-sign
boundary. Two earlier GDT004 target boxes were definitely wrong: f34v.4 was
cropped on the following physical line, and the f37v.1 box contained group 1
instead of registered group 3. Five further legacy target boxes remain
unresolved. Only f114r.18 and f58v.38 securely contain the registered targets.

## Blinding record

A fresh `fork_turns=none` reviewer was instantiated. A provisional packet was
withdrawn when its underlying localization was invalidated. The reviewer was
stopped before making any call, and no valid final matched packet was
delivered. The review table therefore has zero rows and no target/control
spacing score exists.

This is preferable to manufacturing a result from guessed cut coordinates.
It also demonstrates why a subagent alone is not enough: blinding protects
the judgment, but a separate source-aware step must first prove that every
opaque marker corresponds to the registered physical cut.

## Corrections to GDT004 and GDT005

- GDT004's former nine-target physical atlas is withdrawn. Two target groups
  and three cut calls remain secure; the seven other visual rows are wrong or
  unresolved.
- GDT005's former `0/17` target versus `0/17` control headline is withdrawn.
  With zero securely localized controls, a matched comparison was never
  available.
- GDT003 remains `NOT DISTINGUISHABLE FROM STRING STATISTICS`.

The source-formal inventories remain useful; the correction concerns their
binding to the selected image regions and cuts.

## Claim ceiling

GDT006 establishes only a localization-capacity and provenance correction. It
does not supply a spacing effect, grapheme boundary, morpheme, linguistic
slot, language, meaning, semantic role, plaintext, or translation. No f84r
image or formal payload was opened.
