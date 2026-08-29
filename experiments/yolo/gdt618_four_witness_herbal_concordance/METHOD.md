# GDT618 method

## Question

Can five already exposed developmental entry leads be converted into a
reproducible four-witness source concordance whose scoring text comes from one
declared witness and is independently double-read before any Voynich target is
opened?

This registration answers only whether the source plan is complete and
internally reproducible. It does not answer the concordance question yet.

## Bound sources

GDT618 inherits the exact six-response official metadata registry from GDT617,
bound by registry SHA-256
`f4bffe9a24931a175c726a9e0cc1dca9c73cbd69053c78cb1345357a6cc58089`
and its 42/42 validation artifact SHA-256
`333b94e54f3426021f9513a6f71e2ef8204bca46fa93196603783fc9d5896762`.
Those bindings identify:

- BnF Latin 6823 through the official Gallica OAI record and IIIF manifest;
- Masson 116 through the official Beaux-Arts Paris item API and IIIF manifest;
- Sloane MS 4016 through the official British Library catalogue JSON and IIIF
  manifest.

GDT618 additionally registers the official BSB IIIF Presentation manifest for
Clm 28531. It was inspected as developmental metadata before public
registration but is not retained here. Eva-Maria Wagner's dissertation was
likewise accessed during the declared source search and is bound as an external
large source at its University of Freiburg landing page and PDF URL: 62,861,131
bytes, SHA-256
`8f57e7aaee4fe049ecf3fbf201ba2bf13bd6c446438ed59098afe2d28ee7a4fe`.
The PDF is not retained in Git.

The exact URLs,access disclosure and all inherited source hashes are
machine-readable in `artifacts/REGISTERED_SOURCE_PLAN.json`. The deterministic
builder and validator perform no network request. The five Latin 6823
canvas/service identities were derived
from GDT617's already frozen BnF manifest; no canvas or image bytes were
requested. Five exact BnF Mandragore ARKs register the direct Latin-rubric
locator leads. An exact image-request profile is deliberately absent and must
be registered after publication of this plan and before source images are
opened.

## Developmental candidate deck

| Candidate | Latin 6823 | Gallica canvas / service suffix | Clm 28531 | Masson 116 | Sloane 4016 |
|---|---:|---:|---:|---:|---:|
| Balsamus | f25v | f58 | f10v | p96 | f10v |
| Cerfolium | f44v | f96 | f35v | p68 | f30v |
| Citruli | f42v | f92 | f40r | p77 | f32v |
| Cucurbita | f42r | f91 | f46r | p121 | f36r |
| Diptamus | f57v | f122 | f48v | p126 | f37v |

All locators are distinct within each witness. They are developmental leads,
not verified entries. Wagner PDF pages 220 and 222 explicitly bind the last
three witness columns beginning with Clm 28531. The Latin 6823 column instead
has a direct-rubric Mandragore ARK per row and is not supplied by Wagner.
`Ciclamen` and `Cubebe` were replaced before registration because they lacked
this mechanically stronger direct-rubric-plus-explicit-Wagner combination.

## Manual source pass

For each candidate, the source pass must proceed in this order:

1. verify the four physical locators and record any correction without using
   Voynich material;
2. have reader A and reader B independently transcribe the Latin 6823 heading
   or rubric plus the first twelve running-text tokens, without seeing the
   other's reading;
3. compare the two submissions, record every codepoint, spacing,
   abbreviation, expansion, and token-boundary difference, then make a joint
   reconciled reading;
4. separately read the corresponding Clm 28531 heading and opening text only
   as a locator and transcription control; never copy or repair Latin 6823
   from Clm;
5. retain Masson 116 and Sloane 4016 only as entry-identity/locator controls;
   and
6. publish a compact source result containing the raw independent readings,
   difference ledger, reconciled diplomatic reading, declared normalization,
   and exact scoring string before any target packet is opened.

“First twelve running-text tokens” means the first twelve whitespace-delimited
lexical tokens after the heading/rubric in the Latin 6823 entry. Rubric tokens
do not count toward twelve. Marginalia, catchwords, folio headers, later hands,
line-end hyphen artifacts, punctuation-only marks, and decoration do not count.
If heading/body separation or tokenization cannot be reconciled, the candidate
is ineligible rather than silently repaired.

The source result must preserve a diplomatic layer. A separate normalized
Latin-letter scoring layer may lowercase, join a line-break split, and expand
an abbreviation only when the source packet records the exact diplomatic
source and the agreed expansion. It may not modernize spelling, substitute a
synonym, import wording from Clm, or change word order. The precise
normalization table and resulting scoring bytes must be published before any
Voynich pairing.

## Decision rule and claim ceiling

The registered source-only outcomes are:

- `SOURCE_PLAN_REGISTERED__NO_IMAGES_OPENED` for this registration;
- `FOUR_WITNESS_LOCATOR_FAILURE` if any proposed four-way locator cannot be
  verified;
- `INDEPENDENT_READING_UNRESOLVED` if the required readings or reconciliation
  cannot be completed; or
- `FIVE_SOURCE_TEXTS_READY__TARGET_UNOPENED` only if all five rows have verified
  locators and complete double-read Latin 6823 packets.

Even the last outcome licenses only five external source texts and locators.
It does not establish a botanical identification of a Voynich drawing or any
Voynich correspondence, sign value, word, language, plaintext, or meaning.
