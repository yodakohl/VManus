# GDT620 Stage-B acquisition preregistration

Registered: 2026-08-29

Status: `STAGE_B_PROFILE_REGISTERED__NO_STAGE_B_REQUEST_EXECUTED`

## Frozen dependency and deck

Execution consumes only public GDT619 commit
`e82d73d6300f51c810ff131711ace31bb2610b69` and canonical Stage-1 artifact
SHA-256
`95457d96fd7c8e4980c3e92bd1a4ac5009daf27090946b91407bbd476eb0d422`.
Its branch is `ADJACENT_SCAN_FALLBACK`, selected delta is `-1`, observations
are scan 26 absent, scan 25 visible, scan 27 absent, and selected Clm canvases
are exactly 25/75/164/96/101.

The only future requests are the ten literal URLs in
`artifacts/REGISTERED_STAGE_B_PROFILE.json`, in their listed order: five BSB
Clm pages followed by five Gallica Latin 6823 pages. No alternate size,
quality, image service, page, witness, or order is available.

## Frozen transport

Each intent is `GET` only, one at a time, socket-operation timeout 60 seconds,
total wall deadline 180 seconds, response cap 50,000,000 bytes and total-body
cap 500,000,000 bytes, with identity encoding and JPEG acceptance. The bound
application headers are exactly `Accept`, `Accept-Encoding`, and
`User-Agent`; opener default addheaders are disabled, while Python may generate
necessary protocol headers such as `Host` and `Connection: close`. No exact
three-member wire-header set is claimed. There are no
redirect follow-ups, retries, HEAD requests, metadata refetches, `info.json`
requests, network crops, or automatic image/text methods. Immediately before
each request in positions 2 through 10, a fixed 4.0-second delay is mandatory,
including after restart; elapsed wall time never shortens it.

The first transport, encoding, media, cap, completeness, decode, dimension, URL, order,
state, or ownership failure stops. Every intent is durable before network and
consumes its slot; unresolved requests cannot be resent within the bound state.
This is at-most-once per execution state; policy forbids a second state
directory. At most five new BSB and five Gallica intents exist. Together with
GDT619 Stage A, the cumulative BSB request cap is ten.

## Access and decision boundary

Registration performs zero network requests, receives zero image bytes, and
opens no source image or Voynich material. Execution is forbidden until the
profile, acquirer, validator, and this preregistration are public. The runtime
commit argument must be reachable from `origin/main`, and registered runtime
files must match its blobs. Successful JPEGs remain in a private 0700 directory
outside the repository.

Only ten exact successes yield
`TEN_SOURCE_PAGES_ACQUIRED__SOURCE_READING_UNOPENED__TARGET_UNOPENED`; every
other terminal outcome is an acquisition stop. A later public artifact may reveal request
metadata, dimensions, byte counts, hashes, and status only. It may not contain
image bytes or private paths.

This experiment supplies source pages without displaying or reading them, not
their running-text transcription.
It cannot assign a Voynich sign, word, language, plant, plaintext, or meaning.
Latin 6823 remains the future scoring-text witness; Clm remains control only.
`f84` and `f84r` are forbidden.
