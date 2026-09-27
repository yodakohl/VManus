# Source-concept frequency: bounded feasibility result

2026-09-27. Status: **PARKED_MISSING_COMPARABLE_COMPLETE_SOURCE_INPUTS**.

The registered intake did not establish three independent, complete, currently
readable cached works suitable for the eight fixed semantic counts. No source
concept frequencies, Voynich scores, classifier, meaning preference or translation
were produced. This is an input/design decision, not a negative manuscript test.

The task began at approximately 15:11 UTC and closed at 15:18 UTC, within its inclusive
25-minute ceiling. The registration was read before source inspection. Its SHA-256
is `4e53628e050bf87239107ca755d467e15918d2bb17c785fa8abdd5d8e32b97b9`.

## What was actually checked

The current route and controls topic were read. The GDT380 behavior freeze points
back to GDT378's source receipts, observation layer, oracle contract and builder.
Those receipts and the relevant source-builder functions were inspected. The two
additional owned corpus descriptions were GDT893's `COREMA_INTAKE.json` and the
GDT159 diplomatic source audit/manifest. No third corpus description was added.
The six CoReMA XML headers, provenance, body metadata and editorial notes were
checked directly; full running texts were not semantically annotated.

Exact expected raw filenames were searched in the repository including ignored
caches and in conventional temporary/cache locations. `GDT378_SOURCE_CACHE` was
unset. A broader home-directory filename enumeration was stopped after about
90 seconds without a matching filename. Thus the four missing raw caches below
were **not located by this bounded search**; permanent deletion or their absence
from every possible location is not established. No download was attempted.

## GDT380/GDT378 source inventory

| Recorded source | Provenance and permitted publication recorded previously | Current availability and whole-work boundary | Intake decision |
|---|---|---|---|
| CoReMA, six XML collections | Institutional TEI; local headers license text CC BY4.0, separately from facsimiles. Original PID links and exact byte hashes are below. | All six raw XMLs survive and match GDT893 hashes. They represent recipe collections/portions with related witnesses and incompleteness; see the next table. | Useful readable material, but not six independent complete works. No automatic three-work roster. |
| PCEEC2 | GitHub `beatrice57/pceec2`, commit `bf79d1c46e8ef983a7347b0664d0d80243f32831`; prior receipt permits derived-feature publication only. | The84 parsed files were not located. The published builder uses only the first12 eligible records of each file and can split long records. Its derived layer is not a complete correspondence-work transcript. | Missing raw input and unsuitable substitute boundary. |
| Curious Cures, CUL MS Add.9308 | Cambridge institutional manifest;183 HTR-assisted diplomatic transcript pages, Middle English with Latin. Prior receipt says derived features only; it is not a fresh general license determination. | Raw183-page HTML bundle not located. Page manifest and opaque derived rows survive. Transcript-bearing pages alone do not prove completeness of every historical work in the codex. | Missing readable source; no concepts inferred from opaque rows. |
| Austin's Harleian cookery edition |1888 public-domain edition of MSS279 and4016; Internet Archive OCR, originally sensitivity-only. | Raw OCR not located. Existing builder slices two book regions and retains only paragraphs containing a form of “Take”; other authorial paragraphs are omitted. Two witnesses in one edition are not automatically two independent works. | Missing readable source; existing filtered layer is not whole-work content. |
| Furnivall's *Book of Quinte Essence* | Revised1889 public-domain edition, Project Gutenberg17179; Middle English, manuscript c.1460–1470. | Raw edited text not located. Builder isolates the book body and removes editorial lines; its opaque derived layer does not preserve readable concept identity. BooksI/II are parts of one work. | One potentially useful work if its exact cache is recovered; not currently count-ready. |

The historical source receipts also explicitly exclude Regiomontanus' Dartmouth
edition for its permission requirement and MEMT for unavailable commercial access.
Neither was used or replaced. Historical downloads and previous detector execution
are preserved facts; this intake does not revise them into unexecuted experiments.

## Surviving CoReMA witnesses

The following are exact surviving cached sources. Counts in the table are the
previous GDT893 intake counts, not new semantic frequencies. The current pass
recomputed each raw XML hash and inspected the relevant headers/notes.

| Witness and institutional PID | Source scope and metadata | Why it cannot silently become an independent complete work |
|---|---|---|
| [w1](https://gams.uni-graz.at/o:corema.w1.recipes), Wien Cod.2897 | Cookery portion;253 top-level recipe units,251 without explicit incompleteness flags. | Header says the cookery text breaks off. GDT893 records close wording/sequence correspondences with b4. |
| [bs1](https://gams.uni-graz.at/o:corema.bs1.recipes), Basel AN V12 | Meister Hans, *Von allerley kochen*,17r–108v;263 top-level recipe units,262 without explicit flags. | Strong named whole-collection candidate, but one uncertain recipe and no established independence from all proposed comparator collections. The header also distinguishes the preceding register from the text portion. |
| [b6](https://gams.uni-graz.at/o:corema.b6.recipes), Königsberger Kochbuch |34 top-level recipe units,27 without explicit flags. | Header explicitly describes a fragment with missing beginning/end leaves; literal lacunae occur despite absent XML gap tags. |
| [gr1](https://gams.uni-graz.at/o:corema.gr1.recipes), Graz Ms.1609 | Cookery portion of Mondseer housebook;250 top-level recipe units,242 without explicit flags. | The larger codex contains many other kinds of work; this XML omits the food lists on87r–93v. The cached recipe derivative is not the complete housebook. |
| [b4](https://gams.uni-graz.at/o:corema.b4.recipes), Berlin Ms.germ.qu.1187 | Cookery portion71r–112v;257 top-level recipe units,256 without explicit flags. | One editorially noted broken recipe; close w1 correspondences. Other codex works described in the header are not present merely because the header lists them. |
| [br1](https://gams.uni-graz.at/o:corema.br1.recipes), Brixen Cod.I5 | Cookery portion230r–236v;43 top-level recipe units,43 without explicit incompleteness flags. | A bounded apparently complete collection in this edition, not the whole codex. The headers and exact-duplicate checks do not establish a historical stemma or independence from all other cookery collections. |

Minor uncertainty does not make all readable recipes unusable. A future design
could represent it explicitly. The present failure is that the requested
**three independent whole-work comparison was not established**, not a demand
for perfectly certain medieval text. Replacing whole works with selected clean
recipes, related witnesses or manuscript fragments would change this design.

## The second corpus description does not fill the gap

GDT159 describes graphematic samples for a different surface-algebra question:
21 medical PAGE/ALTO units,76 fifteenth-century mixed-genre units,15 scholastic
units,29 charter units and seven apothecary pages. It preserves abbreviations and
does not use translation or lemma labels. These are not a documented roster of
three complete medical works with semantic annotation for the eight concepts.
The Latin medical panel is earlier than the target period; the precise-period
panel mixes genres. No source file from these panels was opened or newly acquired.

## Viability of the fixed eight concepts

| Fixed concept | What a defensible source count would have to distinguish | Available ready count? |
|---|---|---|
| WINTER | Literal named season versus coldness, seasonal ingredients and metalinguistic mention; inflected spellings retained as auditable occurrences. | No. |
| SUMMER | Literal named season versus warmth, ingredients and metaphor; same scope rule as WINTER. | No. |
| WATER | Water as a substance versus a named distillate, watery quality and anaphoric reference. Ingredient annotations can assist but do not exhaust all uses. | No complete semantic count. |
| BODY/PERSON | Human body, whole person and animal body must be separated before any declared union; implicit patients and pronouns must not be counted as written nouns. | No. |
| AND | Actual conjunction including spelling/abbreviation variants, distinguishing lexical mention and other ambiguous forms. | GDT378's English lexical oracle is partial, not a complete multilingual semantic count. |
| NOT | Negation function and its written exponent versus negative noun phrases, exclusion and negative concord. | The old POLARITY_EXCLUSION label deliberately combines several functions; it is not this exact endpoint. |
| COPULA | Predicative linking uses versus auxiliary, existential and change-of-state constructions. | No copula endpoint in the existing frozen contract. |
| UNIVERSAL QUANTIFICATION | All/each/every as quantified-domain operators versus totality adjectives, headings, distributive actions and implicit generality. | No universal-quantifier endpoint in the existing frozen contract. |

The existing CoReMA roles annotate ingredients, instructions, alternatives,
references and other recipe elements. They do not supply a complete, uniform
annotation of these eight endpoints. The GDT378 oracle likewise lacks the
required complete semantic inventory. It must not be relabelled as one.

The counts are concept-expression counts, potentially spanning several source
words. Voynich profiles count exact written groups. A future bridge would have
to pay explicitly for polysemy, omitted arguments, inflection, abbreviation,
allomorph splitting and phrase compression. Without that bridge, contrasting
source concepts cannot yield a calibrated probability for an exact Voynich
word. The meaning classes are not logically indistinguishable by definition,
but this intake supplied neither their empirical separation nor the bridge.

## Decision and reopening conditions

Park IDEA000607's present source-comparison branch before implementation. Do not
run a classifier, silently relax the three-work rule, rebuild a corpus or score
the exposed target from these receipts. GDT380's failure, GDT749's calibration
failure and GDT611's meaning-permutation limit remain unchanged.

Reopening requires an exact already available or separately authorized roster
of three independently identified complete works, inspectable readable bytes and
provenance, complete unit boundaries with uncertainty preserved, and a fixed
auditable eight-concept annotation rule. Related editions count once. The roster
must plausibly cover the proposed document functions; cookbook-only transfer is
not automatically a medical/cosmological-book prior. Only then could a separately
registered minimal source comparison be considered. No new blanket acquisition
is proposed here.

## Reproducibility pointers and hashes

All paths are repository-relative. Source-cache files are cited for reproduction,
not added to publication. No raw source contents or private machine paths are
copied into this report.

| Supporting artifact | SHA-256 |
|---|---|
| `experiments/yolo/gdt380_identity_free_functional_transfer/artifacts/gdt380_comparator_behavior_freeze.json` | `829d910696cdba12489b9435bfd1cc16cc6f6113606c30af6e798b0756ef16da` |
| `experiments/yolo/gdt378_cross_corpus_construction_transfer/SOURCE_AUDIT.md` | `87e2b9949e66bf8d7950583cde0dc91870e58155fc7cb73e47642a6bca83aa60` |
| `experiments/yolo/gdt378_cross_corpus_construction_transfer/artifacts/gdt378_source_freeze.json` | `52e2aa40dbb62b29f285a2e54b81b459c17711b74fedc886aa765ecf4585e569` |
| `experiments/yolo/gdt378_cross_corpus_construction_transfer/artifacts/gdt378_comparator_source_manifest.tsv` | `d9e9cff85ad06ff12c566ff372a6005e897f66b1b84a7f16af5b962a870b16ec` |
| `experiments/yolo/gdt378_cross_corpus_construction_transfer/artifacts/gdt378_oracle_contract.json` | `6294285e5ce31231debb34ae0974d1378e759443b3dcab4f4548d3cdeb84dabd` |
| `experiments/yolo/gdt378_cross_corpus_construction_transfer/src/freeze_comparator_layers.py` | `ab6b0df798440a97dcd41799013e62c4c954698dc5e3778d99d75d0255d0abdc` |
| `experiments/yolo/gdt893_global_source_montage_word_code/artifacts/COREMA_INTAKE.json` | `4d63a53942499d8562f854199e1db079055d5c148c153c3b83c9d5c47bff2ecd` |
| `GDT159_DIPLOMATIC_SOURCE_AUDIT.md` | `ec83fc5a8441f5e4dc8a14d2d2ec21c043721aafed7dbcaf5f7688dc1c7d86a9` |
| `gdt159_diplomatic_corpus_manifest.tsv` | `f86b3a001233413a45fc262f10dcaf01c2e5510e48955d3c3bf879e21d9ae5c5` |
| `.gdt176/corema/w1.recipes.xml` | `a56639c7e8795a2afe76aa7cd950a8a68ade7231e1e68170034bc30002ab48e6` |
| `.gdt176/corema/bs1.recipes.xml` | `d4fc0b986404cb423b99137678a879d3df94b15602740dbfb1fd56b25bc74eb6` |
| `.gdt176/corema/b6.recipes.xml` | `d475072e62701bea6b058729b5f4b988e0eb93fe00878d2831f62e431573e3dd` |
| `.gdt176/corema/gr1.recipes.xml` | `41c603f445a15bcb914eb0d090c80754ad1747821b7556dd77e31c1273a12ff5` |
| `.gdt176/corema/b4.recipes.xml` | `59bf0cf97fc21623a7683cc8059a150644bff313488939222fd200969b7b0afd` |
| `.gdt176/corema/br1.recipes.xml` | `8f142085e1a67c1e854992b1f35a3e8afa9476407789e8029b95bfe639b639ba` |

The GDT378 receipts retain the unavailable raw-content identities:
PCEEC2 parsed bundle `c90c1eabdb58bd1a41e9231c52612bc14cfa1c560d8cf357e1480384e873c714`;
Curious Cures bundle `b3f94e6ea5a2f02efd65a98ad8d4614f039841ca979a1a1c48fab1b16412d08c`;
Harleian OCR `6ffbad0b4b0b09e6c41d35c3edb019df42ecc649e0ef24e31bbd9b01d7d4bb6b`;
Quinte Essence text `62c45f771258c60ecd58a11189ad341b0878ec3fe4513b884ea1070634c60a21`.
These four receipt values were read from the prior freeze, not revalidated
against missing raw bytes during this intake.
