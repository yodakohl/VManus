# GDT1164 — unpaired full-context candidate ranking fails

**NO_SUPPORTED_SOURCE_CONTEXT_RANKING.** The fixed relational matcher does not recover a useful unknown lexical inventory from these historical-source contexts. Its marked-form macro top5 score is **2.042%**, below frequency alone (**4.443%**) and a simpler contextual fingerprint (**11.832%**). All four prospective promotion gates fail. No candidate generator is promoted to Voynich, and the original GDT167/190/1159 failures remain unchanged.

Unlike GDT1160, no expansion pairs or per-form candidate inventories were supplied to fitting. Four whole-book folds used independently selected raw written types and expanded candidates from the other books. Exact strings, spelling, paired IDs and gold labels never entered the numeric fitter. The source is an editorial representation of Nuremberg letterbooks, not a proven Voynich writing channel. Prior project and design exposure are disclosed; this is algorithm-input separation, not fresh analyst blindness.

## Complete primary comparison

Each marked type has equal weight within its held book; the four book means have equal weight. Top5 means exact editorial expansion inclusion among the five ranked candidates. F uses occurrence rates; B uses sixteen-quantile contextual distance fingerprints; G uses the full marginal-relaxed Gromov–Wasserstein objective.

|Held book|Marked types|Sites|Reference candidates|F top5|B top5|G top5|
|---|---:|---:|---:|---:|---:|---:|
|Band2|35|6237|225|2.857%|12.651%|2.881%|
|Band3|39|14205|230|0.000%|11.368%|5.286%|
|Band4|38|8454|223|10.369%|5.270%|0.000%|
|Band5|44|18446|221|4.545%|18.038%|0.000%|
|Equal-book mean|156 total|47,342 total|221–230|4.443%|11.832%|2.042%|

G loses **9.790 percentage points** to the stronger aggregate baseline. It beats both competitors in **0/4 books**, versus the required3/4. Its2.042% score is below the required50%; the required gain was+10points. All19 fully refitted context-destruction controls have at least as large a gain as the real contexts: the inclusive conditional rank is **20/20=1.0**, not the required<=.05. This is an operational pipeline comparison, not a population or project-wide significance claim.

The full [156-row candidate table](CANDIDATE_TABLE.md) gives every selected marked form, all exact expansion mixtures, observed scores, oracle ceiling and G's five candidates. All models' full rankings, all three restart rankings and selected numerical couplings are retained for all80 fold/world jobs. No successful-looking form or restart was selected to represent the outcome. B's better result is descriptive; it is not a retrospectively promoted substitute method.

## Coverage and ambiguity

Capacity passed unchanged in every book:128 written nodes,221–230 reference nodes,35–44 eligible selected marked forms. All selected context profiles were nonzero. Blinded marker/site ordinals and line IDs matched. The complete audit retainsall exclusions and every unsupported type; exact exclusion totals are133 partial-group sites and55 multiple-marker sites, as separately classified by the validator. These exclusion categories are not a permission to repair token boundaries.

Across the scored47,342 sites,43,876 exact expansions are in the reference inventories and3,466 are absent. There are no selected empty/multiword gold spans; had there been any, they would have remained errors. A post-lock oracle choosing the best five inventory words per type reaches **87.561%** under the same macro averaging. Thus inventory absence and unavoidable type-global ambiguity alone do not explain the relational model's low score. The oracle is a diagnostic upper bound, never training information or a replacement result.

33,559 scored occurrences lie outside fit-panel records; they remain in the primary scores and have separate secondary results. Held books belong to one related historical source collection, not independent traditions. A type-global ranking does not resolve individual senses; all observed mixtures and collisions are retained in TYPE_RESULTS. Unmarked words can contribute geometry but cannot carry the marked-form primary endpoint.

## Execution and validation

Public registration **ca1d9ec93** preceded source extraction. Observed source capacity was independently reconstructed before fits; all24 observed numeric arrays agreed exactly. All80 observed/null geometries were independently rebuilt with the registered permutations and original record-length slots. Tiny direct four-index and gradient checks preceded real optimization. The independent pre-fit code review found no contract mismatch.

All80 jobs /492 fixed starts completed, with predictions locked at13:00:18UTC. Root verified prediction and code hashes, authorized gold at13:01:07UTC, and the frozen scorer first opened gold at13:01:29UTC. The numerical contract, source choice and thresholds were not repaired after outcomes. An initial interpreter lacked PyTorch and failed before fitting; execution used the existing pinned environment. This was an environment correction, not a model change.

The complete independent validation passes **12,320 checks** (360 geometry,1,488 fit,10,472 scoring; duplicate initial capacity omitted). Independent fit validation passes **1,488 checks**: all164 selected-plan objectives/rankings, bookkeeping and selection for492 restart records, and F reuse. A separately implemented NumPy Adam replays all12 observed selected model starts with identical complete rankings and maximum probability error1.66e-12. This is not an independent replay of all492 optimizer trajectories. Independent score validation passes **10,472 checks**, reconstructing all240 fold/world/model scores, every type mixture and denominator, outside-fit scores, oracle ceiling and all19 null gains. No scientific correction or refit was required.

The prospective validator plan was prepared locally before source access but was not included in the first public registration commit; that timing is disclosed. METHOD/SPEC and source pins were public. Reproduction uses prepare.py for observed capacity then null geometry, fit.py/run.py for the numeric fits and locked score stage, and the independent validate.py. Full commands are in README. Local numeric NPZ packets are regenerable from fixed source bytes and seeds; complete fit predictions and compact source/result audits are published.

## Research decision

Stop this fixed full-context geometry ranker at the registered32,000-group budget. Do not export source words, promote the better-looking baseline, enlarge vocabulary/corpus, tune initialization/entropy or add optimizer restarts as an automatic continuation. IDEA000908's proposed occurrence-level bridge is conditional on this test passing and remains parked.

The positive GDT1160 finding survives: context and its fixed neural model improve selection **when training supplies expansion candidates**. GDT1164 does not supply the missing unsupervised inventory bridge. It does not prove all neural, graph, unpaired, abbreviation or unknown-writing approaches impossible; only this predeclared finite configuration failed. A genuinely different, independently motivated source of constraints and a new prospective falsifier would be needed for a new selection.

No Voynich text/image or reserve was opened. f84/f84r remain sealed. Confirmed Voynich words: **0**.
