# GDT619 method

## Question

Can the five GDT618 Latin 6823 scoring pages and five Clm 28531 control pages be
acquired through one reproducible, institution-specific IIIF request profile,
without opening any source image or Voynich material during registration?

## Inputs

The sole experiment dependency is GDT618's corrected registered source plan at
public commit `c0266e78`, bound by SHA-256
`2df86904b38212ba37ea3d0dcb0def241600e6f900c94bcb44d87ecd9f969502`.
GDT619 imports its five candidate identities and witness roles without changing
them.

The exact official Clm manifest URL is
`https://api.digitale-sammlungen.de/iiif/presentation/v3/bsb00107549/manifest`.
The five Latin 6823 canvas IDs, service IDs, labels, dimensions, and native
resource URLs are already bound in `REGISTERED_REQUEST_PROFILE.json` from the
frozen Gallica manifest SHA-256
`f22ea8cf697c5598f914bd92e101dd2da62a60df59561d67ef7384d5f5de7187`.

## Registration builder

`src/run.py` constructs the complete request profile from constants and emits
canonical UTF-8 JSON with sorted keys, two-space indentation, and one terminal
newline. It imports no networking module and performs no network access. Its
default mode checks the committed artifact byte for byte.

## Stage A: resolve Clm services

The BSB response must be the byte-bound Presentation API v3 manifest for object
`bsb00107549`, contain 316 canvases, and expose one JPEG painting resource plus
one `ImageService3`/`level2` service for every selected canvas. Redirects are
rejected before a follow-up request.

The direct metadata map is f10v=26, f35v=76, f80r=165, f46r=97, and f48v=102.
It follows `recto=2n+5`, `verso=2n+6` over II+154 leaves and four cover/mirror
scans. The convention is controlled by the byte-bound official Cod.icon.222 v3
manifest and METS response plus the Clm 4623 v3 manifest; Wagner's foliation
note fixes physical bound order after the manuscript's disorder.

Only scan 26 is requested for primary calibration, at width 1200. Its manual
result is one of `VISIBLE`, `VISIBLY_ABSENT`, or
`AMBIGUOUS_OR_UNREADABLE`. Only `VISIBLY_ABSENT` authorizes scan 25 followed by
scan 27; fallback passes only with exactly one `VISIBLE` and one
`VISIBLY_ABSENT`. Ambiguity and every transport/decode failure stop. No other
neighbor, second anchor, OCR, synonym, botanical picture match, or image model
is available.

Stage A emits a compact resolution packet with exact response hashes,
observations, selected service identities, rights metadata, and literal
Stage-B URLs. That packet must be committed publicly in a later material pass
before any Stage-B request.

## Stage B: ten full pages

The five Clm URLs are the manifest-advertised Image API v3 bodies with
`/full/max/0/default.jpg`. Their service objects are exactly `ImageService3`,
profile `level2`; their exact widths are all 1707 and heights are
2547/2563/2624/2576/2587. The five Gallica URLs are the registered Image API
1.1 native full resources. `default` and `native` are deliberately not
interchanged: the witnesses advertise different Image API generations.

The fixed access order is Clm DEV01--DEV05 followed by Latin 6823 DEV01--DEV05.
Only GET is permitted. Concurrency is one; BSB starts are separated by at least
four seconds; successful responses are reused by exact URL and hash; there are
no retries, redirect follow-ups, HEAD requests, `info.json` requests, server
crops, OCR, or target requests.

Every request log row binds sequence, stage, candidate, resource class, URL and
URL hash, status, response URL, redirects, media type, byte counts, raw hash,
decoded dimensions, ETag, and Last-Modified. A later local crop is derivative,
never an additional network request, and must retain complete rectangle and
hash provenance.

`src/acquire_stage_a.py` implements the registered state machine without any
network action at import. `acquire-primary`, `record-primary`,
`acquire-fallback`, and `record-fallback` require an absolute private directory
outside the repository. Before every GET, an intent row is fsynced; the journal
then preserves UTC start/completion timestamps, the defined four-second delay,
measured spacing, response hashes, and all failures. There are no retries.
An auto-releasing nonblocking advisory private-directory lock prevents
concurrency while permitting recovery after process death. Before every GET,
the durable state also becomes `IN_FLIGHT`; any crash, interrupt, or unresolved
attempt permanently refuses that resend. Only complete within-cap body bytes
that fail decode or semantic validation are preserved. No preservation claim
is made for HTTP errors, redirects, wrong media types, or over-cap responses.

Before producing its private Stage-1 draft, the implementation rereads,
rehashes, and fully revalidates the saved manifest and every branch thumbnail
against its unique success record. Each public thumbnail-evidence row contains
the literal URL and URL hash, response hash and byte count, decoded dimensions,
timestamps, status/final URL/redirect count, request and response headers, and
its linked manual observation; it contains no private path.
The directory must be fresh or already carry the exact atomically created
GDT619 ownership marker. Manifest and scan-25 successes persist distinct
next-request phases; restart can therefore issue only scan 26 or scan 27,
respectively. A URL with any prior intent or success row is rejected pre-send.
JPEG success requires Pillow `verify()` followed by reopen and full `load()`;
truncated and SOF-only streams stop. The supplied path and every component must
be non-symlinks. Parent directories are fsynced after durable-file creation and
every atomic state replacement.
The decoder runtime is pinned by `requirements.txt` to `Pillow==10.2.0` and
checked against the imported version. Immediately after creating a new private
directory, its parent is fsynced so the directory entry itself is durable.

## Rights

Latin 6823 retains BnF attribution and its manifest-provided Gallica terms URL.
Stage A preserves the raw top-level `/rights`, `/requiredStatement`, and
`/provider` nodes verbatim. Rights must equal
`https://creativecommons.org/publicdomain/mark/1.0/`; requiredStatement must
remain multilingual and the provider must retain its BSB logo. Missing or
changed rights metadata stops acquisition. IIIF availability is not itself
treated as permission.

## Decision rule and claim ceiling

This registration's only passing decision is
`PROFILE_REGISTERED__NO_IMAGE_REQUEST_EXECUTED`. Future acquisition may end in
`TEN_SOURCE_PAGES_ACQUIRED__TARGET_UNOPENED`, `SOURCE_PAGE_ACQUISITION_FAILURE`,
or `SOURCE_LOCATOR_FAILURE` under the registered rules.

No outcome in this experiment establishes a Voynich correspondence, botanical
identification, sign value, lexeme, language, plaintext, or translation.

## Executed redirect stop and recovery method

The first Stage-A run produced one byte-identical manifest success and one
scan-26 redirect stop. It did not follow the redirect or read an image body.
The public correction in `REDIRECT_AMENDMENT.md` adds two explicit commands:
`authorize-redirect-recovery` is offline-only and accepts only the exact
published pre-recovery state/journal hashes, manifest hash, request history,
redirect detail, and five-file private packet; `resume-canonical-primary`
accepts only that authorization and requests only
`/full/1200,1790/0/default.jpg`.

The manifest and old width-only URL cannot be resent. The canonical response
must fully decode as exactly 1200x1790. The Stage-1 evidence builder accepts
the canonical URL as the actual scan-26 evidence URL. No fallback or Stage-B
request is added by this correction.

A canonical `VISIBLY_ABSENT` observation stops and cannot enter the original
fallback transition without another public amendment. Counting the consumed
width-only request, the amended canonical-visible direct path is capped at
eight BSB requests rather than the original profile's historical seven.
