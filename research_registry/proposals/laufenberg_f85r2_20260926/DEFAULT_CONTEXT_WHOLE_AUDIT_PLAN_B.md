# Pre-audit literal obligations for the IDEA583 whole pass

This is a bounded preparation note from the frozen first contract and the owned GDT1042 `native_groups.tsv` only. It precedes inspection of any whole draft. It records fixed obligations, not a parser, semantic reading, or global impossibility claim. It deliberately separates failures of the frozen register interface on alternate readers from merely unknown neighboring forms.

First-contract exposure: `DEFAULT_CONTEXT_AUTHOR_CONTRACT.md` SHA-256 `8c5b5ca7c9792a3d98d2524c46f3984fd14df08ae1a7ced1a5e6acb34caea4d9`; companion JSON `b254870d081812cdb3d3afec63856f382eaaef251ab9a7f5b73d1ecbc4545e6f`; source `experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/native_groups.tsv` SHA-256 `e50307f834b04ff2ce17a97f14fd2c7b3f24b4818bc7fda3f57c372afc6b9d3c`. No whole draft, root review, new image, or new target source was read for this plan. The first-contract review had been frozen before this audit plan.

## Four family pairs: every exact occurrence

The counts and group IDs below are recomputed by exact literal match within each reader. Each entry remains a separate native occurrence; ZL/IT/RF are alternate readings, not independent witnesses.

| Reader | Pair | Base occurrences | O-form occurrences |
|---|---|---|---|
| ZL3b | `dar` / `odar` | `.1 G032; .15 G002` | `.1 G017, G021` |
| ZL3b | `tedy` / `otedy` | `.13 G003` | `.1 G002; .9 G004` |
| ZL3b | `tchedy` / `otchedy` | `.9 G003` | `.1 G015, G019; .8 G001` |
| ZL3b | `chedy` / `ochedy` | `.15 G003; .19 G005` | `.24 G004` |
| IT2a | `dar` / `odar` | `.1 G032; .15 G002` | `.1 G017, G021` |
| IT2a | `tedy` / `otedy` | `.13 G003` | `.1 G002, G007; .9 G004` |
| IT2a | `tchedy` / `otchedy` | `.9 G003` | `.1 G015, G019; .8 G001` |
| IT2a | `chedy` / `ochedy` | `.15 G003; .19 G005` | `.24 G004` |
| RF1b | `dar` / `odar` | `.1 G032; .15 G002` | `.1 G017, G021` |
| RF1b | `tedy` / `otedy` | `.13 G003` | `.1 G002` |
| RF1b | `tchedy` / `otchedy` | `.9 G003` | `.1 G019` |
| RF1b | `chedy` / `ochedy` | `.15 G003; .19 G005` | none |
| RF1b | `che@152;y` / `oche@152;y` | `.24 G007` | `.24 G004` |

This is 41 forms in all, matching the preselection count. No other visible o-initial spelling is admitted as an O family member. In particular, RF's encoded family is distinct from ordinary `chedy`; missing paired spellings are missing occurrences, not permission to alias them. Contract assignment to a form does not mean that all occurrences are already parsed.

## Fixed state-bearing forms and references

These are exact-form occurrences under the contract's frozen values; every future complete-reader tree must preserve their stated effect/reference behavior.

- Context binders: `opaees` (write fresh c1) only ZL `.1 G003`; `otody` (write fresh c0) ZL `.1 G007` and `.24 G005`, IT `.24 G005`, RF `.24 G005`.
- Input binders: `ar` (fresh x each occurrence) ZL `.1 G004, .22 G002, .24 G008, G012`; IT `.1 G004, .20 G001, .22 G002, .24 G008, G013, G014`; RF `.1 G004, .20 G001, .22 G002, .24 G009, G014, G015`.
- Role binder `qopchas` (fresh d:PHYSICIAN): ZL `.1 G014`; RF `.1 G014`; no IT occurrence. `fcheey` is fixed as `REF d` in all readers at `.7 G005`.
- `otchdy` (`SET_DEFAULT`): all readers `.1 G006`, plus IT/RF `.1 G031`. `pchedeey` (`SET_DEFAULT`): all readers `.7 G001`. `aram` (`CLEAR_DEFAULT`): ZL `.24 G013` only. There is no layout-boundary reset.
- c0 references: `olkaiin` `.1 G016`, `aloees` `.1 G018`, `olkey` `.7 G002`, `qotchdy` `.9 G005`, each all readers.
- c1 references: `qotedaiin` `.1 G020`, `octhody` `.1 G022`, `chotey` `.8 G002`, `oteey` `.8 G004 and .16 G001`, each all readers.
- Input references: `chckhey` `.9 G006` all readers; `or` ZL/IT/RF `.2 G002/G003`, `.13 G001`, `.15 G004`, `.22 G006` (RF `.22 G007`), `.24 G009` (IT/RF only); `sodaiiin` `.13 G004` all readers; `olchedy` `.24 G006` ZL/IT only.
- List/assessment and delimiters: `qopchas` above; `shedaiin` (`END_REQUIRE_LIST`) all readers `.1 G023, .11 G003`; `olfor` (basis of last conduct plan in last closed list) all readers `.1 G025`. These depend on actual list/basis and earlier explicit contexts, not on a convenient unknown token.

An `ar` occurrence is always a fresh x binder, never an x reference. Likewise `.24 G005 otody` creates a fresh c0 register without changing the default. It can make a later c0 reference denote a different Context from the context currently stored in the default. Explicit `SET_DEFAULT`/`CLEAR_DEFAULT` remain the only default changes. `aram` is a ZL-only clear occurrence and cannot be copied to IT/RF absent an exact form or a newly licensed effect (the contract forbids new binding/default/close/scope effects).

## Known-side interface problems versus unknown alternative syntax

A fixed-interface problem is not the same as a string mismatch. The following are concrete failures **if an alternate-reader span is claimed to transfer the authored ZL-style Context/role application**. The reference assignments and missing register writes are fixed under the contract. That does not prove that every conceivable whole parse is impossible: a separately written ordinary higher-order function might consume a `ContextRef` or package as opaque first-class data without dereferencing or applying it as a `Context`. Such a route would be a different, explicitly paid construction and would not inherit the ZL application or its no-update consequence. Unknown neighbors cannot repair the direct application by silently gaining a state effect:

1. **IT and RF c1 is never written.** The only fixed `BIND_CONTEXT c1` spelling, `opaees`, occurs once in ZL `.1 G003`. Both IT and RF nevertheless contain fixed `REF c1` at `.1 G020/G022`, `.8 G002/G004`, and `.16 G001`. Those are fixed `ContextRef` values. Under the intended direct `Context` argument/dereference, there is no c1 register to resolve: no other assigned token writes c1, future unknowns are barred from taking binding effects, and no implicit/nearest noun/image binder exists. A free Context constant could fill a direct Context slot but does not populate c1. A different syntax could inspect/pass the reference token itself as `ContextRef` data, but would not realize those slots as the bound Contexts in the ZL derivation.
2. **IT c0 is also absent before its early c0 references.** Its only fixed c0 binder is `.24 G005`; `olkaiin` `.1 G016`, `aloees` `.1 G018`, `olkey` `.7 G002`, and `qotchdy` `.9 G005` occur before it. These dereference evaluations cannot be repaired retroactively. In RF the only fixed `otody` is likewise `.24 G005`, so its same early c0 references are unresolved. Later fresh binders do not change earlier expression values under the contract. An alternative first-class `ContextRef` analysis could be proposed, but it would not realize the written Context arguments or preserve the claimed ZL template at those sites.
3. **IT has an immediate known type mismatch at `.1 G006–G007`.** `otchdy` is fixed `SET_DEFAULT : Context -> Control`, but its next literal `otedy` is fixed `ExplicitPackage[Context, InputKind -> ResponseAssessment]`, not a Context. It cannot be applied as SET_DEFAULT’s Context argument or coerced under P03. A completely different ordinary function that consumes these two fixed packages as values remains a possible new syntax, not a success of the fixed SET_DEFAULT application. RF `.1 G007` is unknown `oto@152;y`, so that position is an open assignment rather than the same known-side conflict.
4. **IT and RF have a second immediate mismatch at `.1 G031–G032`.** Both have fixed `otchdy` `SET_DEFAULT(Context)` followed by fixed `dar` `ImplicitPackage[() -> ThermalAssessment]`; neither the package nor its eventual assessment is a Context. ZL has the different exact sequence `oteedy dar`, which is the declared thermal-value extraction. The known IT/RF sequence cannot be made the same typed local template by aliasing or changing `dar`’s type; a new higher-order ordinary composition could still consume these packages without applying the SET_DEFAULT frame.
5. **IT's physician-role reference is unbound.** `qopchas` is the only fixed role-d writer and occurs in ZL/RF `.1 G014`, but not IT; IT `.1 G014` is the different unknown `qopchchs`. All readers have fixed `REF d` `fcheey` at `.7 G005`, before any other role binder can write d. The unknown IT form cannot be retrospectively assigned a binder effect under this contract. Thus there is no d register available under the frozen state policy; this is a debt for any direct role-dereference construction, not a proof that an opaque `RoleRef`-taking ordinary function could not be written.

These are known-side conflicts for the **fixed ZL-style Context/role applications** in alternate-reader material under the frozen interface. The c0/c1/d register debt is real, but not a theorem of global UNSAT over every parse because first-class references or packages could in principle enter separately typed ordinary functions. That would require its own content and complete argument accounting; it cannot quietly stand in for bound Context values or for the current shared-operation consequence. These findings do not turn unrecognized neighboring forms into known contradictions. Separate unknown syntax remains at forms such as IT/RF `.1 G001/G003`, RF `.7 G003/G004`, IT `.11 G004`, and the various different end/annular strings. Such groups have not been assigned types by this prep note; they remain unknown and may be ordinary terms/functions but cannot gain a protected state effect. Nor does a known unbound reference authorize inventing a hidden binder.

## Whole-pass audit focus (for later, after freeze)

- For every occurrence of every family form, verify the same frozen kernel and O transformation; at each actual call check the full argument list and result type, including terms nested as an assessment or comparison argument. Recheck all41 exact occurrences, including alternate-reader gaps and the bare `.24`/outside uses.
- Track `x`, `c0`, `c1`, `d`, default, last closed REQUIRE_LIST and stored basis by native order. Do not confuse a register write with default update. A later `ar` or `otody` must allocate fresh identity; prior constructed values remain old; `aram` clears only where that literal occurs.
- Separate any fixed-type contradiction from a location with merely unassigned morphology. Known `REF c1`/`REF c0`/`REF d` failures above are prior obligations; an unknown surrounding form is not a proof of a new contradiction and cannot rescue a protected reference.
- Keep the `.1` thermal no-update model consequence conditional on its declared single-valued exclusive HOT/COLD meanings. The contract does not source-assign that direction or map c0/c1 to an age/health category. Do not promote that counterfactual to an observed manuscript consequence.
- Recheck O4 specifically: age/thermal comparison plan and context-indexed conduct plans are separately written; require whatever explicit relation the frozen contract and whole syntax actually provide. The possibility that they refer to related generic contexts is not identity unless represented.
- O2 and O3 must acquire actual written time variation and different-recipient/health ownership, not just the existence of Context fields or a family law. Preserve the temporal source rival. No reader or annular ambiguity should be normalized away.

This note is audit planning only. It makes no semantic assignment, does not weaken the 583 whole obligations, and does not authorize contract repair. Whole-draft review should be frozen before sharing, and any omitted or failed fixed consequence should remain recorded separately from unresolved syntax.
