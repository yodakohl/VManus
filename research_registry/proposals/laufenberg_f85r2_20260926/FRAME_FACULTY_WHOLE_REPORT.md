# RAW564 whole-E attempt: fixed nominalization countercase

This bounded authoring attempt finds a concrete failure of the **strict RAW564 reduction inventory in IT2a and RF1b**. Each has two consecutive standalone `ar` groups in .24. If the first applies successfully, its result is `FacultySpec`; the second requires `ProcessFrame`. No conversion back to a Frame is among the stipulated rules. The two readers concern one manuscript span and are not independent confirmations.

**ZL3b does not contain that consecutive pair. Its whole E remains incomplete, not proved impossible.** This packet preserves the six-word E.10 necessity clause and all 24 fixed S values, accounts for every E group and all 16 bare `ar` occurrences, and adds no new word meaning or grammar repair. It is neither a complete translation nor evidence that any assigned meaning is correct. Independent confirmed meanings remain zero.

## Scope and decision

The decision was written and hashed before the full census: `FRAME_FACULTY_WHOLE_DECISION.md`, SHA256 `fa4e7e8977b381393a00786fbb64e892e043ec319bf5c90dd374a7e1d9c69f8a`. The task began 22:44:43 UTC on 2026-09-26, with a 35-minute ceiling. Inputs were the existing safe 473-group projection, exact RAW564 and RAW553 cards, frozen550 draft and typed grammar, GDT1045's report, the prior composition review, and the current source review. No new target data, images, reserve, aliases, decoder, registry/state or Git write was used.

The attached JSON records all 81 E groups, the 16 bare `ar` records, complete relevant line contexts with their original separators, every exact occurrence of the 30 parent bindings, input hashes and two small inference traces. The full S grammar remains in its frozen parent files; this packet does not rewrite it. A short attempt at E is retained below. After the all-reader strict extension failed, the parent explicitly directed that the remaining time not be spent manufacturing another unrestricted paragraph dictionary.

## The exact consequence

RAW564 licenses two reductions: a Frame followed by a RecipientRef evaluates that Frame at the recipient; a Frame followed by `ar=NOM` produces its FacultySpec. The latter also applies across a real word boundary. NOM preserves the original process and host role, but its output is not itself a Frame.

| Reader | First `ar` | Second `ar` | Between them | After second |
|---|---|---|---|---|
| IT2a | `IT2a\|f85r2.24\|G013` | `IT2a\|f85r2.24\|G014` | `DEFINITE_SPACE` | `DEFINITE_SPACE` before `am` |
| RF1b | `RF1b\|f85r2.24\|G014` | `RF1b\|f85r2.24\|G015` | `DEFINITE_SPACE` | `UNCERTAIN_SMALL_SPACE` before `am` |

Both first operators follow the unassigned whole form `otees`. Grant the strongest possible left context: suppose a complete written expression ending there already denotes `P:ProcessFrame`. This is a conditional grant, not an assignment of a Frame meaning to `otees`.

```text
P:ProcessFrame  ar₁:(ProcessFrame → FacultySpec)
    ⇒ NOM(P):FacultySpec

NOM(P):FacultySpec  ar₂:(ProcessFrame → FacultySpec)
    ⇒ domain mismatch: FacultySpec ≠ ProcessFrame
```

If no suitable P exists, the first application is already unlicensed. If it does exist, the second fails under the fixed reductions. The second operator cannot retrieve an arbitrary earlier Frame by skipping the first NOM result. A multiword Frame expression is permitted only if a written construction actually builds it; it is not permission to choose an arbitrary backward span.

This is deliberately a **fixed-contract** conclusion. A new higher-order constructor that consumes a FacultySpec and produces a new Frame could change the expression available to the second operator. Such a constructor, its lexical binding and its application production are absent from RAW564 and the fixed S grammar. Adding them would be a new grammar, as would idempotent NOM, a Spec-to-Frame cast or a different meaning for free `ar`. No theorem against all possible nominalization languages is claimed. No such escape is installed here.

The complete .24 alternatives, without normalization, are:

```text
ZL3b: okees ochar oted[o:a]r ochedy otody olchedy oteedo ar or airol otees ar aram
IT2a: okees ochar otedar ochedy otody olchedy otchdo ar or air ol otees ar ar am
RF1b: okees ochar otedas oche@152;y otody @221;l che@152;y oteedo ar or air ol otees ar ar am
```

ZL's final `aram` is one literal group here. It is not split into `ar am`. The uncertain RF boundary is **after** its second `ar`, so it does not remove the recorded definite boundary between the two operators. No native-pixel decision is made by this packet.

## Every bare `ar`

The following table is the full census, not a selection of helpful prefix examples. `D` means `DEFINITE_SPACE`, `U` means `UNCERTAIN_SMALL_SPACE`. Complete source IDs and line contexts are retained in the JSON.

| Reader | Locus/group | Immediately previous group | Left/right boundary | Obligation |
|---|---|---|---|---|
| ZL3b | .1 G004 | `opaees` | D / D | Unassigned predecessor; no Frame derivation |
| ZL3b | .22 G002 | `los` | U / D | Same, with uncertain left boundary |
| ZL3b | .24 G008 | `oteedo` | D / D | Unassigned predecessor; no Frame derivation |
| ZL3b | .24 G012 | `otees` | D / D | Unassigned predecessor; no Frame derivation |
| IT2a | .1 G004 | `opoees` | D / D | Unassigned predecessor |
| IT2a | .20 G001 | line start | LINE_START / D | Cross-line scope unresolved |
| IT2a | .22 G002 | `los` | D / D | Unassigned predecessor |
| IT2a | .24 G008 | `otchdo` | D / D | Unassigned predecessor |
| IT2a | .24 G013 | `otees` | D / D | First NOM of countercase |
| IT2a | .24 G014 | `ar` | D / D | Second NOM of countercase |
| RF1b | .1 G004 | `opoees` | D / D | Unassigned predecessor |
| RF1b | .20 G001 | line start | LINE_START / D | Cross-line scope unresolved |
| RF1b | .22 G002 | `los` | D / D | Unassigned predecessor |
| RF1b | .24 G009 | `oteedo` | D / D | Unassigned predecessor |
| RF1b | .24 G014 | `otees` | D / D | First NOM of countercase |
| RF1b | .24 G015 | `ar` | D / U | Second NOM of countercase |

The previous physical line before both .20 initial operators ends with `chedy`, whose fixed S meaning is a SourceRelation. That last group alone is not a Frame. This is an additional unresolved context, not another proved countercase: a complete multiword expression could in principle have a type different from its last group, if an explicit production built it. No such W production or cross-line Frame scope has been supplied. Unknown ZL predecessors likewise do not become contradictory merely because their types have not been assigned.

## Whole-E attempt and exact remaining debt

Each reader has 27 E groups and 27 literal types. Joining the two parent dictionaries supplies 8 ZL types and 7 each in IT/RF; the remaining counts are **19, 20 and 20**, respectively. These are coverage counts, not fit scores. The apparent old debt of 21 ZL entries was RAW553 alone; S already contributes `oteey` and `aiin`.

| ZL line, complete literal sequence | Contribution under inherited values |
|---|---|
| .7 `pchedeey olkey qokedy sheos fcheey` | All five values unknown. No written organ introduction is recovered. |
| .8 `otchedy chotey qocthey oteey ol oloqorain` | `oteey` retains the attractive faculty instance; five values unknown. No instance/specification/bearer association or realization clause is supplied. |
| .9 `daiin qotaiin tchedy otedy qotchdy chckhey` | All six values unknown. `qotchdy` is not the assigned `qotchd`. |
| .10 `ytchedy qodar qotedar qokar qotchd qotom` | The complete inherited necessity proposition below. |
| .11 `soiis aiin shedaiin chok{co}m` | `aiin` retains RecipientRef; three values unknown. An E antecedent and closing clause remain unwritten. |

The .10 derivation is:

```text
ytchedy : ProcessKind = NOURISHMENT
qodar   : FacultySpec = NOM(A)       [licensed qod|ar]
qotedar : FacultySpec = RETENTIVE    [atomic]
qokar   : FacultySpec = NOM(L)       [licensed qok|ar]
qotchd  : FacultySpec = EXPULSIVE    [atomic]
qotom(P,F1,F2,F3,F4) : Proposition

REQUIRES_EACH(NOURISHMENT,
              [NOM(A), RETENTIVE, NOM(L), EXPULSIVE])
```

The resulting retained hypothesis says that nourishment requires each of the attractive, retentive, alterative and expulsive faculties. It supplies neither an event nor an identified faculty instance. IT's `qtchedy` and RF's `qo@152;ar` remain gaps even in this seed line. The JSON lists every other literal alternative, including markup.

This clause names kinds. Its participating-organ interpretation does not identify a particular E organ or the S recipient. S's x/r binders remain confined to S.12–17. E's `aiin` cannot refer backwards to the later S binder, and the repeated `oteey` does not identify a common physical faculty instance. A discriminating whole E would need a written E binder and an actual `Realizes(e,f,s,b)` association with all arguments accounted for. Naming `NOM(A)` or possessing it cannot fill those slots or create e. No implicit realization, owner or successful assimilation is inserted.

The delegated-realization and different-organ rivals consequently remain untested. The opaque-whole-name rival avoids the universal free-NOM commitment but is not thereby proven true. Reprinting `qodar` and `qokar` as the old faculty names alone does not exercise RAW564's promised shared process/host constraint.

## Source coverage and a paragraph-boundary correction

The cached primary supports activity-derived faculty names and distinguishes a faculty, its activity, and an attained presentation/assimilation. It motivates a resident retentive power under the stated premise of purposeful Nature. It does not identify any target form, compound cut, application direction, E/S owner or repeated individual. [Galen, Book III](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Galen/Natural_Faculties/3%2A.html), public-domain 1916 translation, reproduced with a not-proofread notice.

The complete chosen III.1 is larger than the retained S account. It includes proper juice as material adapted to assimilation; attraction from veins into parts; presentation as the goal of attraction; adhesion and eventual assimilation requiring considerable time; continued movement between parts preventing both outcomes in any of them; prolonged retention by a faculty resident in the receiving part; and the conditional purposeful-Nature premise. S supplies a proposed local sequence and departure condition. E.10 supplies a proposed necessity list. They do not express all those qualifications, the named/generic organ extension, proper versus foreign material, or a written realization/owner relation. S's strict cessation-at-boundary commitments remain its own hypotheses; they are not repaired into the source's weaker goal language.

There is also an exact boundary error in the inherited description **“III.9 opening complete paragraph”**. In cached `external_cache/galen3_frame_source.html`, the `<P CLASS="justify" ID="p277">` unit contains the organ/faculty discussion **and** the final analogy involving dogs, human faeces and liver residues appropriate to spleen, gall-bladder or kidneys. The next `<P>` starts chapter R10. The final analogy is not a separate following paragraph in these bytes. The cache is 102400 bytes, SHA256 `1d0f8547ae087a7c97d36f7600cee05dbb1b3321beb973b3065bba2ea8b0ad24`.

Therefore full-paragraph coverage includes that recipient-relative appropriateness analogy. The legacy fixed excerpt omitted it. This observation corrects the whole-unit claim; it does **not** retroactively add content to frozen553/564, or supply any new target binding. The parent has independently confirmed the cached boundary and is recording a correction to the source review. The JSON separately records the additional full-paragraph debt. The NOM countercase does not depend on which shorter source excerpt was intended.

## Cost and disposition

The retained dictionaries contain 24 S whole values and 6 E whole values. RAW564 adds two Frame components and one NOM value used both as component and standalone `ar`; these are three proposed component values, not four independent meanings. Its costs remain three licensed compound cuts, two application cases, one cross-word application license, Frame/Spec/Instance distinctions, an explicit Realizes relation, frame preservation and a restricted resident-host law. This authoring attempt adds **zero** new whole values, productions, casts, compound licenses, aliases or cross-paragraph identity links.

The strict all-reader RAW564 extension fails on its specified local type rules. ZL-only whole E remains unfinished and source-incomplete; neither a coherent full ZL translation nor its impossibility has been demonstrated. Further arbitrary filling would not cure the existing strict countercase. A different nominalization grammar would require a separately frozen contract. Parent meanings, GDT1045 and all earlier frozen packets remain unchanged.

Frozen at 2026-09-26 23:00:19 UTC, within the 35-minute allowance. Validation checked literal coverage, preserved parent bindings, exact separators and the unchanged decision hash; it did not execute semantics.
