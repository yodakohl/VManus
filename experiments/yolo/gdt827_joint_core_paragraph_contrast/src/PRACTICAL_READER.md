# Practical reader: manual treatment, not material transformation

## Scope, exposure, and status

Read `VOYNICH_CURRENT_ROUTE.md` first and obtained compact GDT826/GDT809 index pointers. The route exposed the inherited water/air/fire/becomes/source, earth/dry, and wood/charcoal guesses. **This is not a blinded reading.** I did not inspect other agents' notes or those experiments' full readers. I read the complete assigned blocks in GDT822 `BLOCKS.tsv` and `CONTEXTS.tsv`, and every corresponding source-native group in `SOURCE_GROUPS.tsv`: 50 loci, 150 edition-lines, 1,157 groups. ZL3b/IT2a/RF1b are alternate readings, not three manuscripts. No new page, image, sealed data, or external historical source was opened.

This is a concrete C0 rival, not a translation or a claim that these are treatment instructions. Its attraction is a coherent inventory of physical operations and contact surfaces across paragraphs. Its weakness is that this inventory was chosen after seeing the patterns, and large portions remain unread. It does not establish eight words, POS, syntax, or a manuscript genre.

Native paragraph flags were separately checked after the coordinator relayed a boundary-audit warning: ZL marks f81r.16–31 as one paragraph; IT ends one at .23 and starts another at .24; RF has no start/end flags throughout this selection. ZL and IT agree on the endpoints of the other three assigned blocks. Thus “complete blocks” describes the supplied selection, not three-edition agreement on paragraph segmentation. The f81r sketch must pay an additional continuity debt across the IT boundary. This metadata audit is not independent semantic evidence, and the relayed correction is an additional exposure; no competing glosses were relayed.

## One joint hypothesis, eight fixed exact-whole glosses

| Exact source group | Trial gloss | Fixed physical meaning |
|---|---|---|
| `qokeedy` | rub | Move the contacting hand back and forth against a surface. |
| `qokedy` | press | Exert sustained contact force against a surface. |
| `shedy` | stroke | Move the contacting hand along a surface in a single sweep. |
| `qokain` | hand | The anatomical hand. |
| `qokaiin` | foot | The anatomical foot. |
| `qokeey` | skin | The bodily covering. |
| `chedy` | on | Physical surface contact/location, not becomes or contains. |
| `qol` | it | A singular anaphoric referent; antecedent must still be recovered. |

The operational glosses are deliberately different physical movements, not interchangeable “do/process/treat” placeholders. Imperative force is part of the hypothesis, not an independently identified grammatical fact. Anatomical hand is not freely swapped to arm, operator, instrument, or measure; foot is not lower part, base, or unit. Skin is not heat or a preparation. `it` cannot silently become from-it, therefore, or there.

No component inheritance: `okeedy`, `qokeey`, and `qokeedy` are separate; `qolchedy`, `olchedy`, `lchedy`, `solchedy`, and `chedaiin` stay unknown. Bracket alternatives and extended entities stay opaque. In particular, RF `qokee@152;y` is not assigned rub merely because other editions read `qokeedy`.

## Content sketch, explicitly not literal translation

The single proposed subject is bodily surface manipulation: recurring rub/press/stroke operations, sometimes naming the hand or foot, with contact phrases and anaphoric reference to a previously mentioned surface or object. On this account repetition can prescribe repeated physical movements instead of reporting repeated material transformations.

- **f75r.32–46:** A hand-focused sequence introduces stroking and the skin, develops a central cluster of rubbing/pressing, and returns to hand/stroke references. This is the clearest operation-sequence candidate. Lines .34 and .45 remain wholly unknown under the eight-word map; the repeated `dar` and the final destination of .46 remain unexplained.
- **f76r.51–56:** A shorter sequence includes press–rub–press, then contact phrases, and ends with foot … stroke skin. This could be a compact instruction paragraph. The initial `raiin … dar on qopchedy`, intervening near-whole repetitions, and all of .55 remain serious debts, not secretly understood equipment or dosage.
- **f77r.25–37:** The paragraph alternates hand and foot references, with rubbing and contact on a hand. This could discuss manipulation of those parts. It does not literally say “alternate,” “both,” “each,” or “massage.” The foot–foot repetition at .34 is not solved by the fact people have two feet; a distributive construction would still need evidence. Lines .30–33 and the final qualification at .37 are largely unread.
- **f81r.16–31:** Operations and contact/anaphoric phrases occur without either exact hand or foot. This could continue surface treatment without renaming the limb, but continuity has not been shown: its opening is entirely unknown. There is also no exact rub in this block. The three `ol` groups at .22, the shift at .24, and the closure at .31 remain unexplained.

The sketches do not license extra literal words. In particular there is no inferred oil, patient, healer, heating, benefit, or named ailment. The paragraphs might have quite different subjects despite the recurrent operation-like tokens.

## Literal token ledger for all four complete blocks

The complete 50-line exact-whole ZL substitution ledger is stored once in [the shared reader](../artifacts/READER.md), under `MANUAL`, using the eight fixed senses above (`reibe?`, `drücke?`, `streiche?`, `Hand?`, `Fuß?`, `Haut?`, `auf?`, `es?`). Its machine-readable map is in [MODELS.json](MODELS.json); all 150 source-native alternate-reading lines are retained in [SOURCE_LINES.tsv](../artifacts/SOURCE_LINES.tsv). These are token substitutions, not grammatical translations; unknown groups and source boundaries remain debts. This shared representation supersedes only the duplicate ledger here, not the substantive reading or source audit below.

## Alternate readings and boundary checks that matter

- f75r.33 ZL's small-space `l,shedy` and `qo,l` yield separate groups, while IT has opaque `lshedy` and exact `qol`: `skin [lshedy] it on hand ...`. RF has `ched@222;`, which remains unknown, not on. The prettier IT string is not a consensus translation.
- f75r.35 ends with ZL `qoka[in:r]`, IT `qokar`, RF exact `qokain`; only RF licenses a third hand. RF `{ch'}edy` does not license stroke. The exact `dar dar` doublet remains in all three readings.
- f75r.36 ZL `dardardy` is one unknown; IT/RF have three groups `dar dar dy` (RF small spaces). These do not justify breaking ZL's whole.
- f75r.37 IT replaces the ZL `qokeedy` at group 5 with `qokchdy`; RF has extended entities. f75r.38 has exact ZL/IT rub–rub–press–press–rub. RF retains the AABBA repetition pattern with opaque A=`qokee@152;y`, B=`qokedy`; it does not provide three extra exact rubs.
- f75r.39 IT's second putative rub is `qokchdy`; ZL/RF have exact rub–rub. f75r.42 IT has `c`, not the ZL/RF second operation `qokeedy`. At .44 the ZL/RF drawing interruption separates `ch` and `dar`; IT has `chdar`. At .46 RF's `che@152;y` remains unknown.
- f76r.51 RF `shed@222;` and `qopched@222;` stay opaque. f76r.53 RF `{ch'}edy` is not stroke; at .56 RF `she@152;y` is not stroke, although foot and skin remain exact. The duplicated `olchedy` at .54 is never split to supply on.
- f77r.29 rub–rub is exact all three. At .30 ZL `sa,iin`, IT `saiin`, RF `s,aiin` are different groupings, all unknown. At .31 RF's first `qote@152;y` is not equated to the next exact `qotedy`.
- f77r.34 ZL has opaque `qolchedy`; IT has separate `qol chedy`, producing `foot stroke on it on foot foot [checkhy] [raiin]`. RF has opaque `qolche@152;y` and `@206;aiin`. All three retain the exact foot–foot doublet. IT's extra on is a genuine cost for this rival, not removable redundancy.
- f77r.35 RF reads `qotaiin` rather than `qokaiin`, so the proposed foot is absent there; `che@152;aiin` stays one unknown group. No hidden copula or conditional is supplied in any edition.
- f81r.19 RF has `shee@152;y` as one unknown and final `ol am` separated by a small space, not a presumed English clause. f81r.24 ZL `qotaldar`, IT `qotal dar`, RF `qotal @152;ar` remain their own wholes. f81r.27 RF `che@152;y qoke@152;y` licenses neither on nor press. f81r.29 RF `ysheedy` cannot be split; .30 RF's stroke-like group is opaque, and .31 RF's second stroke-like group is `she@152;@222;`.

These are material rendering differences, not an exhaustive retranscription of every unknown variant. All 150 source lines were inspected, including unknown-only lines and their separators; the literal ledger is expressly ZL-only.

## Discriminating successes, counterexamples, and referent debts

The sharpest local gain is f75r.38: a sequence of distinct physical instructions can preserve all five repeated wholes without turning repetitions into omitted words, intensifiers, or multiple states of the same material. Supporting but weaker sequences are f76r.52 press–rub–press and f77r.29 rub–rub. These are *in-sample motivations*, not confirmations. A repeated property list, recitation, or other notation could also make AABBA meaningful.

The larger departure is grammatical: f77r.35 `chedy qokain` becomes **on hand**, not **becomes water**; f81r.20 `qol chedy qokeey` becomes **it on skin**, not **from it becomes fire**. The latter is only a phrase. The unknown `qopchedy` cannot be called an applicator or a placement verb to complete it. Similarly, `dar chedy qopchedy` at f76r.51 becomes `[dar] on [qopchedy]`: this avoids the inherited mandatory-result problem but does not solve either noun or demonstrate surface contact.

There are substantial adverse cases:

1. f81r.27 `[sol] on press ...` is poor ordinary instruction syntax. A clause boundary, unusual order, or complement construction might explain it, but none is demonstrated. It is a direct joint pressure point on on/press, not permission to change press into pressure.
2. f77r.34 retains foot–foot and, in IT, on–it–on. A pair of anatomical feet does not supply the missing distributive grammar. This is not a solved repetition.
3. f76r.53 `it stroke` contrasts with f81r.25 `stroke it`. A fixed English command order is therefore not available. An unknown language could permit different orders, but that is an unpaid syntactic debt.
4. f75r.40 `stroke hand stroke` permits two movements or an object sandwiched between instructions, but the source identifies neither construction. The hand might be manipulated or might manipulate; these are different roles and cannot be silently interchanged.
5. f77r.33 `[daiin] on it ...` is not rescued by importing the inherited “much.” No scalar meaning was assumed in this eight-word rival. Independently established quantity-plus-predicate syntax could damage the spatial proposal.
6. The anaphor `it` is never assigned a demonstrated antecedent. In f81r especially, the paragraph opening is unknown, so an apparently cohesive chain is only a promise, not recovered referential continuity.

Exact ZL hits of the eight proposed wholes total 34/122 groups in f75r, 12/58 in f76r, 26/92 in f77r, and 22/116 in f81r: 94/388 groups, about 24%. Repetitions inflate that figure; it is substitution coverage, not translated information. `qokeey` occurs once per assigned block because these blocks were selected through the GDT822 target packet; this cannot independently support skin as their common topic. Cross-register anatomical transfer has not been tested here.

## Most useful distinguishing observation

**Inspect the role of the exact `chedy qokedy` adjacency at f81r.27 alongside `qokedy sheedy chedy qoteedy` at .19, with source boundaries fixed.** The rival needs on to mark a contact relation and press to retain its physical operation sense in both places. The inherited account instead treats chedy as a finite material predicate. An independently established clause boundary or grammatical role at .27 would be more diagnostic than another plausible picture or another completion of f77r.35. If .27 is a single ordinary on-plus-nominal construction and qokedy must be its noun, this strict imperative-press rival loses; changing it to pressure would be a new dictionary. If chedy is independently required to be finite there, the fixed on gloss loses directly. Neither condition is established by this packet.

Bottom line: manual surface treatment is a genuinely different, concrete joint content hypothesis, with an attractive operation sequence but no whole-paragraph translation. It earns comparison, not adoption; the current evidence does not choose it over material transformation.
