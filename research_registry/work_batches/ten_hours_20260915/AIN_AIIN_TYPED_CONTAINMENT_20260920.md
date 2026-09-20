# AIN/AIIN typed containment candidate in ZL3b f106r.42–47

Status: **RAW_UNREVIEWED, unselected.** This is a target-side content
constructor proposal over an already exposed report-owned paragraph. It does
not adopt qokain=water, qokaiin=air/vessel, or any old renderer value. No new
target data, image, reserve, sealed folio, decoder, experiment, route or ledger
change was used.

## Exact owned scope

The existing W80 report prints the complete ZL3b paragraph f106r.42–47 in
`research_registry/proposals/translation_programs_20260912/work/W80/READING.md`
(lines 119–143; SHA256
`049ba86d835168322243e2eb0a81220898f06fc887b12b578529fb80a4d184ed`). All six
lines and every group remain in scope:

```text
f106r.42 pcheodar shol ka[in:ir] ok{e'e}chedy qoteey shotchy qoty lpaiin shedy lar
f106r.43 daiiral sheol daiin otedy qokain okar cheor al taiin chekal otaras
f106r.44 dshedy qoteey otaiin chy chealol chlchd aiin oty otair otaiikam
f106r.45 y sheedal okain okain otar kaiin chdalkair olkai[?:r] al keedy okal
f106r.46 sotchdaiin shodaiin otedy qokeedy qokaiin ykar qokain cheedy lol
f106r.47 ycheoar okain qokain char oky cheokam
```

The source file’s actual f106r.43 spelling is `daiiral`. The exact machine-owned
bytes are in W80/PARAGRAPHS.json (SHA256
`85a81f23a765c24c38454d9ecad3b522a7a2d932d482242d918ffedbf218677e`). No
claim is made that ZL3b and IT2a are independent witnesses.

The key local clause is the complete nine-group f106r.46 line:

```text
sotchdaiin shodaiin otedy qokeedy qokaiin ykar qokain cheedy lol
```

It contains both whole forms and a written relation candidate in one local
scope. The same paragraph repeats qokain at .43 and .47, so its proposed type
is constrained across three occurrences rather than assigned only at .46.

## Finite typed constructor

The hypothesis treats the `-ain`/`-aiin` contrast as a whole-form family
property. It does **not** claim that the final strings are independently
identified morphemes. Under one global constructor:

| Written whole | Opaque typed role |
|---|---|
| qokain | `CONTENT(x)` |
| qokaiin | `CONTAINER_FOR(x)` |
| ykar | `BIND(container, content)` bridge |
| cheedy | `CONTAINS(container, content)` relation |

The local reduction is fixed and consumes all nine groups:

```text
PREFACE_A(sotchdaiin) PREFACE_B(shodaiin) ORIGIN(otedy)
ASSERT(qokeedy) CONTAINER(qokaiin) BIND(ykar)
CONTENT(qokain) CONTAINS(cheedy) CLOSE(lol)
```

`PREFACE_A`, `PREFACE_B`, `ORIGIN`, `ASSERT` and `CLOSE` are finite structural
slots with opaque values; they are not English filler. The content/container
claim rests only on the typed pair and its written relation. No nearest-line
reference, unprinted object, or extra participant is added. The repeated
qokain forms in .43 and .47 retain the same `CONTENT` type under the same
global rule, even though this note does not invent their missing relation
arguments.

## Consequence and rival

The constructor predicts a typed edge `CONTAINS(qokaiin, qokain)` at f106r.46.
Swapping the two forms, or treating both as the same content type, breaks that
edge’s declared domain/codomain while leaving the surface unchanged. The
quantity-carrier account in GDT559 predicts no such edge: AIN and AIIN are
different values in one argument slot. The GDT818 account predicts a different
content system centered on `solkeey` and `chedy`, with qokaiin used in an
air/conditional tail; it does not type qokaiin as the container of qokain in
this f106r paragraph.

This is a structural discriminator only. It becomes useful if the same global
typed roles explain another complete exposed paragraph without changing the
AIN/AIIN assignment and without adding an unprinted container or content.

## Predecessor checks and failure debt

- **GDT559** (`experiments/yolo/gdt559_argument_carrier_substitution_grammar/REPORT.md`, SHA256 `c1f3518d7996c041335ed1abac9899e53079de22ed0f6321065c8f7442559bc4`) explicitly makes AIIN=WERT and AIN=ANTEIL interchangeable carrier values. That is a direct rival, not an inherited meaning.
- **GDT817** (`experiments/yolo/gdt817_solkeey_external_content/REPORT.md`, SHA256 `91b5d68ee69b58542dda9f4d5c4df8b6d33e848dc1378012c9b7a2e425146923`) keeps qokain as a tentative water medium and qokaiin unresolved.
- **GDT818** (`experiments/yolo/gdt818_fixed_material_container_relation/REPORT.md`, SHA256 `70297594bd7dbffabe4f00558b1d0c0f29ec7186a388771acc62403e9d692757`) tests vapour/basin × becomes/contains on f77r.25–37 and a conditional tail; all four worlds remain C0 and do not select this typed qokaiin container role.
- **W94–W96** (`research_registry/proposals/translation_programs_20260912/work/W94/REPORT.md`, W95/REPORT.md, W96/REPORT.md) constrain mass/grade and same/new identity assumptions. They do not provide a container relation and cannot license one here.

The strongest failure is that `qokain`, `qokaiin`, `ykar` and `cheedy` may be
independent values in a different clause grammar, while the apparent
AIN/AIIN distinction may be purely orthographic. The singleton frame slots
also remain unbound. A source-side containment relation does not independently
identify any target participant or meaning. No selection or experiment follows
from this raw card alone.

## V2 local nine-group derivation (development only)

This section is a new worked development; the original raw proposal above is
preserved unchanged. It is a complete interpretation of the nine groups at
f106r.46, not a claim to have read the surrounding six-line paragraph.

The finite state is
`S = (scope, qualifier, origin, frame, pending_bind, containers, contents,
assertions)`. The initial state is
`({}, {}, {}, {}, none, {}, {}, [])`. `C0`, `X0`, `Q0`, `O0`, `F0` and `S0`
are opaque typed constants introduced by the observed groups; they are not
English nouns.

| # | Written group | Fixed function | State/result |
|---:|---|---|---|
| 1 | `sotchdaiin` | `OPEN_SCOPE(S0)` | `scope := S0` |
| 2 | `shodaiin` | `QUALIFY(S0,Q0)` | `qualifier(S0) := Q0` |
| 3 | `otedy` | `SET_ORIGIN(S0,O0)` | `origin(S0) := O0` |
| 4 | `qokeedy` | `OPEN_RELATION_FRAME(S0,F0)` | `frame := F0`, no endpoints yet |
| 5 | `qokaiin` | `ALLOCATE_SUITABLE_CONTAINER(C0)` | `containers := {C0: contents=[]}` |
| 6 | `ykar` | `BIND_LEFT(F0,C0); EXPECT(CONTENT)` | `pending_bind := (F0,C0,CONTENT)` |
| 7 | `qokain` | `ALLOCATE_CONTENT(X0); FILL_RIGHT(F0,X0)` | `pending_bind := none`, `contents(X0)` not asserted |
| 8 | `cheedy` | `ASSERT_CONTAINS(F0.left,F0.right)` | append `CONTAINS(C0,X0)` and set `contents(C0):=[X0]` |
| 9 | `lol` | `CLOSE(S0,F0)` | return the sole clause result `CONTAINS(C0,X0)` |

Thus suitability and actual content are separate states. Before group 8,
`C0` is merely a suitable empty container. `ykar` binds the left endpoint and
opens a typed content slot; it does not assert a physical relation. `qokain`
fills that slot but does not assert containment. Only `cheedy` commits the
edge and mutates the container's content set. `sotchdaiin`, `shodaiin`,
`otedy`, `qokeedy` and `lol` cannot rebind either endpoint. A later predicate
would need an explicitly declared `REPLACE_CONTENT` function to change the
binding; none exists in this V2 grammar.

The deterministic output is therefore:

```text
scope=S0; qualifier(S0)=Q0; origin(S0)=O0;
container C0 is suitable and initially empty;
F0 binds C0 to content X0;
cheedy asserts CONTAINS(C0,X0);
close(S0,F0).
```

The only observed fact supplied to this reduction is the nine-group written
order. No observed semantic label says that C0 is suitable, that X0 is
content, or that the final edge is physical containment. The rival swap
`qokaiin=CONTENT`, `qokain=CONTAINER` produces a different typed AST under
the same positions; the spelling alone cannot choose between those ASTs.
Neither output is a meaning validation.

## Search for an unchanged-rule second clause

The bounded report-owned W80 excerpt contains no second local line with the
same complete endpoint pattern `qokaiin … ykar qokain cheedy`. The neighboring
whole lines retain constraints: f106r.43 and .47 repeat `qokain` but lack the
full binder/assertion sequence, while f107r.5 has `... chedy ... qokain` but
not `qokaiin` and uses a different surface predicate. I therefore do not
reinterpret either as a second containment example. The six-line paragraph
remains fully retained as unknown context.

The expected cross-paragraph consequence is only conditional: a later
complete clause using the same `qokaiin–ykar–qokain–cheedy` contract would have
to produce the same container/content edge types, and a qokain occurrence in
the container slot would be rejected. No independently observed semantic
fact currently tests that consequence, so it remains an unexecuted prediction.

## Root review and registered follow-up, 20 September2026

Original raw proposal and V2 above remain unchanged. V2 introduces a discourse
referent, calls it a physically empty container, then conflates ASSERT_CONTAINS
with a physical filling mutation. An assertion need not perform the asserted
physical change; absence of stored assertions need not mean physical emptiness.
No historical observation chooses either semantics. These are undeclared
content assumptions, not manuscript contradictions.

GDT999 separately froze four literal stem-frame candidates and two distinct
claims (local recognition versus universal ykar writer), then inspected every
ykar in1349 complete exposed paragraphs. All62cases/248candidate decisions
were independently validated. Only the original qok frame matches, once per
reader; no new stem or other-leaf instance. All four universal writers are
contradicted. The original optional local interpretation remains unverified,
with no additional transfer capacity. Meanings CONTAINS/SUITABLE_FOR/FILLED_WITH/
WHOLE_HAS_PORTION remain indistinguishable. No automatic relaxed-distance or
spelling repair. See experiments/yolo/gdt999_typed_pair_frame_transfer/REPORT.md.
