# GDT285 — exact-host reuse and wrapper terminal localization

## Question

GDT284 found that the standard Voynich wrapper fingerprint is
`INITIAL+/INTERNAL+/FINAL-/EOS-`, but becomes `++++` when an entire immutable
host bucket is withheld.  GDT285 asks whether the negative terminal half
specifically requires training occurrences of the exact target PAGE_HOST, or
whether it is merely a consequence of removing training material.

PAGE_HOST identities are opaque.  No substring, meaning, semantic field, new
parser, or new architecture is introduced.  GDT283 and GDT284 are frozen.

## Frozen panels and recurrence bins

Use the 8,448-event native panels for Voynich and the three GDT283 Latin
diplomatic controls.  In every held-physical-folio fold, count training events
whose exact PAGE_HOST equals the target host and assign the target to one fixed
bin: `ZERO`, `ONE`, `TWO_TO_THREE`, `FOUR_TO_SEVEN`, or `EIGHT_PLUS`.

## Frozen three-way score

Score the exact GDT283 no-wrapper and full-wrapper character models in three
modes:

1. `STANDARD`: use all non-held-folio training events;
2. `EXACT_HOST_EXCLUDED`: also subtract every training event with the exact
   target PAGE_HOST identity; and
3. `MATCHED_NONHOST_EXCLUDED`: instead subtract the same number of training
   events whose PAGE_HOST differs from the target.

Matched donor events are selected separately for each held folio and target
host.  Traverse the target host's training occurrences in observation-ID
order.  For each occurrence choose one unused non-host donor, using the first
available pool in this frozen hierarchy:

0. section × Currier × hand × within-field position × host length × first host
   character × wrapper;
1. section × Currier × hand × host length × first host character × wrapper;
2. host length × first host character × wrapper;
3. host length × first host character;
4. any non-host training event.

Within a pool, order candidates by
`SHA256("GDT285_DONOR_ORDER|panel|held_folio|observation_id")`, rotate that
order by `SHA256("GDT285_DONOR_START|panel|held_folio|target_host|source_id|tier")`,
and take the first unused candidate.  Thus exact and matched modes always
remove the same number of events.  Report donor-tier usage; do not discard
hard matches.

## Frozen endpoints and decision

Partition gain into the GDT283 components and define:

- `ONSET_BODY = INITIAL + INTERNAL`;
- `TERMINAL = FINAL + EOS`.

Report all five recurrence bins, every folio, and all controls.  The primary
Voynich comparison uses events with training recurrence at least one.

Report `TERMINAL_PENALTY_REQUIRES_EXACT_HOST_REUSE` only if all four conditions
hold:

1. standard recurrent `TERMINAL < 0`;
2. exact-host-excluded recurrent `TERMINAL >= 0`;
3. the exact-host exclusion raises terminal gain more than the matched
   non-host exclusion does; and
4. exact-host-excluded recurrent `ONSET_BODY > 0`.

Otherwise report `TERMINAL_PENALTY_NOT_LOCALIZED_TO_EXACT_HOST_REUSE`.
This exact subtraction is a mechanistic sensitivity, not an independent new
sample or a claim that PAGE_HOST is lexical.

## Claim ceiling and seal

At most this localizes an opaque wrapper-conditioned character penalty to
reuse of exact parsed host identities.  It cannot establish morphology,
abbreviation, a lexical code, sound, language, meaning, plaintext, or
translation.  Only the published f84-free native inventory is read; no f84
row may be opened, parsed, retained, joined, or scored.
