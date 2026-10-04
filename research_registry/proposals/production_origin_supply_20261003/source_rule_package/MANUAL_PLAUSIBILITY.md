# Manual plausibility check before a context model

4 October 2026. User explicitly requests manual assessment first. No fitter,
new GDT, target access, Voynich meaning or added writing rule. This is a
purposefully selected source-case diagnostic, not a blind accuracy estimate.
All source gold existed earlier; aggregate per-form expansion counts were
inspected to select contrasts. Case-level judgments will be written before
opening the corresponding case-level expansion, but prior exposure is not
forgotten. No claim of analyst blinding.

The question is whether the already frozen finite rule relation plus complete
written context can distinguish actual historical expansions, and what part
of an apparent success comes from supplied alphabet/language knowledge.
Known predecessors1160 (supplied per-form candidates),1164 (unpaired ranking
failed),1166 (partial channel/vocabulary pipeline failed) retain their scope.
The known sequitur/plurmen/duplicated-re source exceptions stay unsupported.

Smallest adequate work: inspect paired grammar candidates, a lexical spelling
variant, and a known outside-relation case; preserve entire source records and
all legal alternatives at each focus. Do not train a scorer or repair rules.
If contexts do not discriminate or gold needs unavailable information, narrow
or stop the proposed exact-recovery criterion before implementation. If
contexts do discriminate, record precisely what evidence an unpaired model
would need; a human German reader's success is not model capacity.
No replacement45-minute limit; bounded by these manual examples and decision.


## Seven inspected cases and actual comparisons

Each complete recipe record is retained in MANUAL_WRITTEN_CASES.json. A helper
only retrieved the fixed records and enumerated the unchanged declaration's
outputs; no ranker or learned model ran. Focus judgments were saved in
MANUAL_JUDGMENTS.json before invoking the per-case answer display. Aggregate
answer counts had already guided purposeful selection. CaseG and the source
family had earlier exposure. These seven cases yield no blind accuracy or
population estimate. Manual alternatives below are salient rivals, not a
replacement for the complete legal output sets preserved in the packet.

| Case/source locator | Complete-group context, excerpt | Manual judgment before case answer | Edition | Consequence |
| --- | --- | --- | --- | --- |
| A B4 084r/N016, T006058 | `mach sy trukchn mit eıne̅ mell` | Prefer `einem` from the instrumental/material construction; historical variation still a caveat. | `einem` | Context supports one grammatical choice. |
| B B4 086r/N006, T007003 | `leg sy in eıne̅ topph` | Prefer `einen` for placement into a pot; retain the locative rival. | `einen` | Opposite preference for the **same native group** as A. |
| C B4 075v/N014, T001988 | `stozz in In eıne̅ Morser` | No unique choice: grinding in a mortar versus movement into one. Slight preference for `einem` was explicitly not a decision. | `einem` | Wider recipe context does not give me a decisive exclusion of `einen`. |
| D B4 072r/N027, T000557 | `pe gewss die hun̕r ... geprattn` | Prefer `huner`, retain `hunerr`; preference relies on usual spelling/frequency, not a contextual discriminator. | `hunerr` | My preferred exact string is wrong. Correct subject matter cannot replace the exact answer. |
| E B4 090r/N004, T008926 | `wein oder hun̕r prue` | Same preference `huner`, retain `hunerr`. | `huner` | Same written group as D, different recorded expansion; no demonstrated contextual rule separates them. |
| F W1 001r/N008, T000064 | `slach die du̕ıch ein sib` | Prefer `durich`, retain `duerich`; the93:1 source-type prior was already seen. | `durich` | A correct choice here cannot be credited to a new context effect. |
| G Gr1 019v/N016, T003114 | `... pradt In ... ſeqt` plus U+F153 | Known desired `sequitur` is outside the unchanged local outputs. | `sequitur` | A language preference cannot recover a missing legal candidate. |

Excerpts simplify some nonfocus display characters only; they are navigation
labels. The full written packet preserves every character, space group,
unknown span, focus ID and source locator. B4's084r is a leaf of the historical
control witness, not Voynich f84. No Voynich input was used.

A/B/C each have all18 legal declaration outputs, including `eine`, `einem`,
`einen` and strings such as `eineein`. Recognizing that most alternatives are
not plausible words is largely a spelling/lexicon operation. The A/B switch
is a more specific grammatical contribution. This distinction is needed before
crediting a future context model. We did not reduce the legal domain to only
two answers after looking at the edition.

D/E/F each have eight legal outputs. In D the exact original markup is
`hun<ex>er</ex><am><g ref="#combcomma_er"/></am>r`; E has the same written
class with supplied `e`. Thus `hunerr` was not accidentally doubled by the
manual extractor. Whether D reflects intended historical spelling or an
editorial restoration problem is **not adjudicated** without a native source
check. It stays the exact recorded reference and is not normalized to my
preferred answer. The two contexts alone do not prove a universal inability
to distinguish these spellings: an independently supported scribal or lexical
condition could in principle matter. None was demonstrated here.

G has six legal strings (`seqtitur`, `seqttur`, `seqttura`, `seqtuitu`,
`seqtuitur`, `seqtur`), all preserving the prefix `seqt`. The `ui` of
`sequitur` must precede the surviving `t`, beyond the local relation. The whole
record also contains two UNKNOWN spans, retained in the packet. This was a
known failure, included to prevent an attractive-language repair.

## What the manual reader was supplied

I knew the alphabet, abbreviation domains, German recipe language and ordinary
word readings. The surrounding text was the **written** view, not the gold
expanded context, but as a German reader I could mentally resolve neighboring
abbreviations. A future model must not receive those expansions as an oracle.
My general linguistic training is also much broader than five short related
source books. Manual preference therefore establishes conditional plausibility,
not that the proposed reference-only algorithm has enough data or capacity.

The first two comparisons support that the fixed native declaration domains
can carry a real context-dependent contrast. They do not show this to be a new
historical discovery. IDEA864 already documents `einem/einen` in location and
destination contexts from Ste1, and GDT1160 already demonstrates conditional
context gains with supplied form inventories. GDT833's spelling intervention
likewise shows that exact historical output spelling is a substantive separate
constraint; it does not prove our present variants unidentifiable. Those
primary predecessor decisions remain unchanged. No generic repeat of
“context helps abbreviations” is justified by these manual cases.

## Decision before implementation

**LIMITED MANUAL PLAUSIBILITY; NO CAPACITY OR EXACT-RECOVERY CLAIM.** The core
selection mechanism is plausible for some source forms; the seven cases do
not justify expecting unique exact reconstruction of every group, and they do
not establish an unknown-key or Voynich method.

The prospective experiment would be worth designing only around the remaining
new question: can the unchanged shared sign rules generate candidates for
forms whose individual expansion pairs are withheld, and can an unpaired
other-book reference actually select their exact occurrence readings? A fixed
source alphabet is still supplied. The machine must receive no correct
neighbor expansions or per-form gold inventory. Known versus novel forms and
lexical pruning versus real contextual selection need distinct accounting;
plain easy words must not dominate the claimed effect.

Retain exact-spelling errors, unresolved source obligations, outside-relation
answers and explicit ambiguity. Do not relabel the wrong `huner` preference
as success because the recipe subject is plausible. Any secondary lexical or
grammatical scoring needs independently specified labels before fitting;
there is no retrospective spelling equivalence or softened primary score.
Success criteria and the concrete reference/scoring method remain to be fixed.
No six-book fit, neural implementation, altered writer or new corpus was
started. A manual positive licenses consideration of that narrow design only,
not the automatic multi-stage decoder chain proposed earlier.

## Reproduction and source checks

`python research_registry/proposals/production_origin_supply_20261003/source_rule_package/manual_cases.py`
recreates all seven written records and exhaustive finite alternatives.
After the saved manual judgments exist, append `--reveal` to recreate the
source comparison and its judgment-file hash. The helper imports the unchanged
source-package projector and checks all eight original source-byte pins.
All seven focus abbreviations were separately inspected in the original XML;
MANUAL_PRIMARY_FRAGMENTS.json retains these source fragments and IDs are in
MANUAL_ANSWER_COMPARISON.json. No native facsimile collation was performed.

Attribution and original XML URLs/licenses remain in source-package SUMMARY
and REPORT: CoReMA, University of Graz, CC BY4.0. Manual records are drawn from
those originals, with no new source acquisition or reserved material. The
bounded idea producer checked predecessor/design limits only and neither
chose my case answers nor supplied an independent accuracy estimate.

Append `--check` to the same command to compare the saved cases, judgments and
answers with a fresh extraction and write MANUAL_CHECKS.json. This checks data
consistency and hashes, not the correctness of a human linguistic judgment.
