# GDT1061 preregistration — public ZFD case-study source lines

Registered 2026-09-28 before opening f56r/f77r comparison content. The f88r
ZL3b and cross-reader page had already been inspected exploratorily; this is
disclosed and no holdout or significance is claimed. Earlier project exposure
to these pages also exists (GDT784, GDT790 and others).

## Decision and smallest adequate test

The pinned public ZFD `CASE_STUDIES.md` at commit
`3f030a9293b8db15dc2c7b0d0e7c703e71711f62` presents one f56r, three
f88r and two f77r strings as `Raw EVA`. Whether these six strings are faithful
source readings is unknown. GDT784 has an independently bounded f88r.22 whole
reading, but no confirmed lexemes; broad semantic reinterpretation of that
page cannot arbitrate ZFD's source transcription. If all six lines are genuine
in any current reader, ZFD provides concrete candidate text for future meaning
tests. If none is even a contiguous span on its claimed page, these case studies
cannot serve as an immediate semantic bridge; this does not refute every
possible ZFD mapping or prove its author invented them.

The six source strings are fixed in `src/claims.tsv` by case-study order. The
public Markdown bytes have SHA-256
`234c7689f9d1ee4cb3592009b8c468151399fff55015c971b633dfff45a75fb3`.
Compare
each only with its claimed page: f56r, f88r, or f77r. Use all P loci from the
guarded cross-reader TSV and all three ZL3b/IT2a/RF1b readings. Convert the
source's dot separators to spaces and collapse whitespace; preserve every EVA
character and group boundary. Score (1) exact entire P line, (2) exact
contiguous same-line group span, (3) exact contiguous span in the page's P-line
stream crossing at most one adjacent P-line boundary. Report each tier and
coverage for each of six claims and each reader; do not cherry-pick. Check
`kostain` as an exact group on f77r/f88r as a secondary traceability note,
without making it a separate significance test. No fuzzy matching, alternative
spellings or post-hoc conversion rules.

Inputs are existing admitted text selectors only. f84/f84r, f1r and reserves
remain closed. No image/OCR, page admission or physical-leaf confirmation.
Claim ceiling: source alignment only, no translation, no probabilistic
significance or historical language inference. Budget: <=15 minutes source
pinning/preparation, <=15 implementation, <=10 validation, <=10 publication;
stop expansion at 50 minutes.
