# GDT620 method

## Question

Can the ten already selected GDT619 source pages be acquired at most once
within one bound execution state from their literal institutional IIIF URLs,
with bounded transport and complete public provenance, before any source
transcription or Voynich target access?

## Inputs

The sole dependency is the public GDT619 Stage-1 resolution at commit
`e82d73d6300f51c810ff131711ace31bb2610b69`. Its canonical artifact is
`experiments/yolo/gdt619_five_source_page_acquisition/artifacts/STAGE1_RESOLUTION.json`,
SHA-256
`95457d96fd7c8e4980c3e92bd1a4ac5009daf27090946b91407bbd476eb0d422`.
It fixes Clm global delta `-1`, the five Clm canvases, and their literal BSB
Image API v3 full-page URLs. GDT619's registered profile fixes the five Latin
6823 Gallica Image API 1.1 URLs and dimensions.

## Method

The exact request order is:

| Seq. | Candidate | Witness | Resource | Expected pixels |
|---:|---|---|---|---:|
| 1 | DEV01 Balsamus | Clm 28531 | BSB scan 25 | 1707x2466 |
| 2 | DEV02 Cerfolium | Clm 28531 | BSB scan 75 | 1707x2581 |
| 3 | DEV03 Liquiritia | Clm 28531 | BSB scan 164 | 1707x2562 |
| 4 | DEV04 Cucurbita | Clm 28531 | BSB scan 96 | 1707x2591 |
| 5 | DEV05 Diptamus | Clm 28531 | BSB scan 101 | 1707x2581 |
| 6 | DEV01 Balsamus | Latin 6823 | Gallica f58 | 3302x4581 |
| 7 | DEV02 Cerfolium | Latin 6823 | Gallica f96 | 3451x4553 |
| 8 | DEV03 Liquiritia | Latin 6823 | Gallica f178 | 3284x4557 |
| 9 | DEV04 Cucurbita | Latin 6823 | Gallica f91 | 3333x4388 |
| 10 | DEV05 Diptamus | Latin 6823 | Gallica f122 | 3346x4574 |

Only `GET` is allowed, with `Accept: image/jpeg`, `Accept-Encoding: identity`,
one connection, no redirect follow, no retry, a 60-second socket-operation
timeout, and a 180-second total wall deadline. Environment proxies, cookies,
authentication, and opener default addheaders are disabled. The three bound
application headers are exactly `Accept`, `Accept-Encoding`, and `User-Agent`;
this is not a claim that the wire header set has only three members. Python may
generate necessary protocol headers such as `Host` and `Connection: close`.
Every response is capped at 50,000,000 bytes and the pass at 500,000,000 body
bytes. An advertised larger Content-Length
stops before body consumption; a missing or smaller header never disables the
streaming cap. A present Content-Length must be a single valid decimal and
equal the observed bytes. Content-Encoding may be absent or `identity` only;
Transfer-Encoding may be absent or exactly `chunked` without Content-Length.
HTTP non-200, changed final URL, redirect, wrong media type,
over-cap or partial body, JPEG verification/load failure, or dimension mismatch
stops the entire pass without another request.

The five new BSB requests bring the GDT619/GDT620 cumulative BSB cap to ten,
counting every durable intent including the historical width-only failure.
GDT620 separately permits exactly five Gallica intents. Immediately before
each request in positions 2 through 10, execution performs one fixed 4.0-second
delay. This remains mandatory after restart and elapsed wall time never
shortens it; failed requests consume their slot. No
HEAD, manifest, `info.json`, server crop, OCR, automatic image analysis,
source-reading, or target request is available.

Execution uses a fresh or exactly owned absolute private directory outside the
repository. The directory and path components may not be symlinks; mode is
0700 and regular files are 0600. An advisory nonblocking lock prevents
concurrency. Before each GET, the append-only journal records and fsyncs the
intent and the durable state becomes `IN_FLIGHT`. This gives at-most-once
execution per bound state directory, not a global network guarantee; policy
forbids creating a second execution directory. An unresolved intent consumes
its slot and permanently forbids a resend. A completed success records literal
URL and hash, response URL, redirect count, status, media type, header and
observed bytes, response SHA-256, decoded dimensions, ETag, Last-Modified,
intent/start/completion times, inter-request spacing, and defined delay.

The execution command also requires the public registration commit. Before
network it verifies that this commit is reachable from local `origin/main` and
that every registered executable/configuration path matches its committed
blob. Working-tree-only code cannot authorize a request.

After ten successes the acquirer rereads and hashes every saved JPEG against
its unique success row, redoes full decode and dimension validation, and emits
a private canonical acquisition-result draft. That public-safe draft contains
no local filesystem path or image bytes. Images remain private; institutional
rights/attribution remain attached to later local reading derivatives.

## Decision rule and claim ceiling

`TEN_SOURCE_PAGES_ACQUIRED__SOURCE_READING_UNOPENED__TARGET_UNOPENED` requires
ten successes in the exact order and zero unresolved attempt. The first failure instead yields a
terminal acquisition stop; no retry or alternate URL is licensed.

Registration alone yields
`STAGE_B_PROFILE_REGISTERED__NO_STAGE_B_REQUEST_EXECUTED`. Neither registration
nor acquisition assigns a Voynich correspondence, sign, word, language, plant,
plaintext, or meaning. Latin 6823 remains the sole future scoring-text witness;
Clm 28531 is a separate reading control and may not repair it. GDT620 neither
displays nor reads the acquired pages. `f84` and `f84r` remain forbidden.
