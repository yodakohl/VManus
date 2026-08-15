# GDT095 — exhaustive plant-description channel

## Question

On the already archived strict pharmaceutical plant-label panel, does an HPR2
layer predict the full frequency-eligible human visual-description vocabulary
on unseen physical folios? This is exploratory localization, not confirmation.

## Frozen panel and representation family

Use every unhedged kind-L `PLANT` locus in section P from the aligned GDT012 /
GDT059 inventories: 83 loci on f88, f89, f99, f100 and f102. f84r is absent.
Use the local description clause, strip source identifiers and fixed editorial
stop words, apply only a simple plural normalization, and retain every token
present at 4..N-4 loci. Export the entire token manifest.

Compare ten representations: raw character trigrams, PAGE_HOST character
trigrams, compiler signature, WRAPPER/RIGHT/B3 marginals, and exact
PAGE_HOST×WRAPPER, PAGE_HOST×RIGHT, PAGE_HOST×B3, and
PAGE_HOST×WRAPPER×RIGHT conjunctions. K=5 and shrinkage 4 are inherited from
GDT068/GDT089. Every prediction excludes the target physical folio. Candidate
neighbors must share at least one representation feature; a zero-overlap exact
feature set backs off to held-folio prevalence instead of using an arbitrary
lexicographic tie.

The primary statistic is total binary codelength gain over held-folio token
prevalence. A 5,000-world null permutes each locus's complete descriptor-token
vector within folio and reports a maximum across all ten representations.

After the full token manifest was exposed, a post-hoc interpretive ablation
separates obvious position vocabulary (`base`, `edge`, `ground`, `level`) from
the remaining appearance vocabulary. This split is logged and may explain a
lead, but it is not a second confirmatory endpoint.

## Ceiling

Human description words are external outcome tags, not translations of a
Voynich form. No PAGE_HOST or construction receives a semantic role or gloss.
