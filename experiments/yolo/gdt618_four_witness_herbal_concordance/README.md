# GDT618 — four-witness herbal concordance

Status: `SOURCE_PLAN_REGISTERED__NO_IMAGES_OPENED`

GDT618 registers a source-only manual-reading packet for five developmental
herbal-entry candidates. Its deterministic builder does not fetch or display a
manuscript canvas,page image,Voynich page,Voynich transcription,or target
feature. The plan separately discloses the earlier developmental access to BSB
manifest metadata,five Mandragore notices and Wagner's PDF;no external
manuscript page image or Voynich material was opened.

The five candidates are `Balsamus`, `Cerfolium`, `Citruli`, `Cucurbita`, and
`Diptamus`. Each has a direct Latin 6823 rubric locator in an exact BnF
Mandragore record plus explicit Clm 28531, Masson 116, and Sloane 4016
locators in Wagner's appendix. `Ciclamen` and `Cubebe` were weaker early leads
and are not in the registered deck. Every four-way join still requires manual
verification.

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
