# GDT618 — four-witness herbal concordance

Status: `SOURCE_PLAN_CORRECTED__NONREUSED_PHYSICAL_FOLIOS__NO_IMAGES_OPENED`

GDT618 registers a source-only manual-reading packet for five developmental
herbal-entry candidates. Its deterministic builder does not fetch or display a
manuscript canvas,page image,Voynich page,Voynich transcription,or target
feature. The plan separately discloses that developmental source research used
network access to official Mandragore search and notice HTML metadata,
including `Liquiritia` and alternative candidates, and consulted/downloaded
the already hash-bound Wagner PDF/text. The exact aggregate metadata-request
count is not asserted. No external manuscript image bytes or Voynich material
were opened; the deterministic builder and validator themselves make zero
network requests.

The five corrected candidates are `Balsamus`, `Cerfolium`, `Liquiritia`,
`Cucurbita`, and `Diptamus`. Each has a direct Latin 6823 rubric locator in an exact BnF
Mandragore record plus explicit Clm 28531, Masson 116, and Sloane 4016
locators in Wagner's appendix. `Ciclamen` and `Cubebe` remain weaker early
leads outside the registered deck. `Citruli` is now also superseded. Every
four-way join still requires manual verification.

## Physical-folio correction

The first registered deck and validator incorrectly treated side-qualified
locator strings as physical folios. Thus Latin 6823 `f42v` for `Citruli` and
`f42r` for `Cucurbita` passed an exact-string uniqueness check even though they
are the same physical leaf, contrary to GDT617's nonreuse gate. This corrected
revision replaces DEV03 `Citruli` with `Liquiritia` on Latin 6823 `f85v` and
records `Citruli` as superseded for that collision. The validator now strips a
terminal `r`/`v` before asserting within-witness physical-leaf uniqueness.
The replacement search did use the developmental metadata network access
disclosed above. That access was limited to HTML metadata and the already
hash-bound Wagner PDF/text, with no manuscript image bytes or Voynich access.

Only Latin 6823 may supply the later scoring plaintext: the exact heading or
rubric and the first twelve running-text tokens. Clm 28531 is an independent
manual-reading control only. Masson 116 and Sloane 4016 are concordance-locator
witnesses only. Two independent Latin 6823 readings must be submitted before
comparison, then reconciled with every difference recorded before any result
packet exists.

The canonical registration is
[`artifacts/REGISTERED_SOURCE_PLAN.json`](artifacts/REGISTERED_SOURCE_PLAN.json).
It binds the five exact Gallica canvas and image-service identities derived
from GDT617's locally frozen manifest, but registers no image request profile.
That profile may be fixed only after this source plan is public and before any
image request is executed.

`src/run.py --check` reproduces the plan byte-for-byte and `src/validate.py`
audits source roles, locators, inherited GDT617 bindings, the external Wagner
binding, access counters, manifest hashes, and claim ceiling.

See `METHOD.md` and `PREREGISTRATION.md`. No candidate is yet a verified
four-witness entry, and nothing here assigns a Voynich sign, word, language,
object, operation, plant, plaintext, or meaning.
