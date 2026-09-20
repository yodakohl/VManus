# GDT993 / IDEA432 component audit

Status: bounded correction audit, not a replacement proposal. The original
`IDEA000432` JSON is preserved byte-for-byte. This audit checks it against the
frozen GDT993 `src/SPEC.json`, `REPORT.md`, the 63-group RAW377 draft, and its
ZL source packet. No target data, reserve, decoder, root experiment, route, or
ledger was changed.

## Exact frozen family

The RAW377 ZL draft and frozen GDT993 63-group stream contain these distinct
words beginning with `qok`, `che`, or `ch`:

| Surface | RAW377/GDT993 output | Occurrences | Audit status |
|---|---|---:|---|
| `qokedol` | `FAR_BANK` | 1 | omitted by 432 |
| `qokeey` | `TAKE_OUT` | 1 | covered |
| `qokedy` | `G` / `CargoRef(G)` | 5 | covered |
| `qoky` | `FERRY` | 1 | covered |
| `qokchedy` | `UNATTENDED` | 1 | covered |
| `qokeedy` | `CONVEY_OUT` | 1 | **432 overstates output** |
| `qokal` | `TRAVEL_TOGETHER` | 1 | covered |
| `ched` | `WITHOUT_AGENT` | 1 | omitted by 432 |
| `cheeety` | `RETURN_EXCLUDING` | 1 | omitted by 432 |
| `chedy` | `C` / `CargoRef(C)` | 3 | covered |
| `chckhdy` | `WOULD_BE` | 1 | omitted by 432 |
| `chedain` | `NEXT` | 1 | omitted by 432 |
| `checthy` | `ALL` | 1 | omitted by 432 |
| `chety` | `UNHARMED` | 1 | omitted by 432 |

`cheey` is absent from the RAW377 lexicon and this frozen 63-group stream. The
IT2a/RF variants are alternate readings of the same manuscript and are not
silently added to the ZL family.

## Concrete correction to IDEA432

The frozen SPEC pattern is `CONVEY_OUT`, `NEXT`, `@CargoRef`; the `NEXT` atom is
owned by the separate word `chedain` in the complete clause
`qokeedy chedain chedy`. Therefore the following claims in 432 are wrong and
must not be inherited:

- `qokeedy -> CONVEY_OUT_NEXT` as the output of one word;
- `qokeedy(chedy) = CONVEY_OUT_NEXT(C)`;
- the claim that the `dy` terminal itself supplies a next-cargo mode.

The exact compositional application is `CONVEY_OUT(chedy)` followed by the
separate `chedain` sequencing function, or equivalently
`NEXT(CONVEY_OUT(C))` after two independently reduced words. The word
`qokeedy` alone emits `CONVEY_OUT`.

The remaining 432 table entries preserve the frozen labels, but they do not yet
cover the whole family. Its `e_count` and terminal branches are a finite state
hypothesis rather than observed semantic functions. They are not whole-form
aliases, but the state names were chosen to reproduce the nominated outputs and
there is no independent clause showing that the same state must have the same
meaning elsewhere. The omitted `qokedol`, `ched`, `cheeety`, `chckhdy`,
`chedain`, `checthy`, and `chety` also prevent 432 from being a complete family
writer.

No V2 is registered here. A corrected table that merely changes
`CONVEY_OUT_NEXT` to `CONVEY_OUT` would be a byte-level repair, not a new
meaning-bearing derivation. The two new raw alternatives registered alongside
this audit supply different semantic consequences: one tests operation identity
versus sequence scope, and the other tests hypothetical safety modality versus
actual voyage state.

## Surviving exact claims and limits

`qokedy` remains the inherited unconfirmed `G` reference; `qokeey` remains the
frozen `TAKE_OUT` operator; `qoky` remains `FERRY`; `qokchedy` remains
`UNATTENDED`; `qokal` remains `TRAVEL_TOGETHER`; and `chedy` remains `C`.
These are retained outputs of the conditional GDT993 reading, not confirmed
meanings. GDT608 supplies only directed formal component backoff and residual
identity. GDT993 and RAW377 explicitly leave TAKE_OUT/CONVEY_OUT synonymy and
all component meanings unresolved.
