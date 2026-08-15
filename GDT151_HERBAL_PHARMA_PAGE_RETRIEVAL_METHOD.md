# GDT151 — complete Herbal-to-pharmaceutical page retrieval

## Question

Does the GDT148 PAGE_HOST retrieval lead generalize from six selected
Herbal-to-Herbal relations to the complete set of cached human catalogue
statements linking an Herbal drawing to a pharmaceutical plant fragment?

This is an exploratory, post-exposure stress test. It does not use label
ownership and does not infer that prose names the depicted fragment. The
target is the complete pharmaceutical **page bag**, so any fragment-specific
signal is diluted by the other material on that page.

## Frozen mechanical inventory

Take every f84-free page in `gdt137_herbal_visual_feature_inventory.tsv`.
From its cached human `illustrations` description, extract every exact folio
reference whose current page has section `P` in the f84-filtered GDT062
inventory. Preserve one additional reference to f101v as
`UNSCORED_NO_FORMAL_PAGE_BAG`, rather than silently dropping it.

This yields 32 references, 31 scored relations, 30 scored Herbal source pages,
and 15 possible pharmaceutical target pages. No relation is selected by its
Voynich text.

## Models and controls

For every source page, rank all 15 pharmaceutical pages using weighted
Jaccard similarity of complete page bags:

1. exact PAGE_HOST frequency;
2. PAGE_HOST character trigrams;
3. raw-token character trigrams;
4. compiler signature;
5. absolute page-group-count proximity;
6. a leave-source-out human target-degree prior.

The degree prior is an adversarial nontextual control: often-mentioned
pharmaceutical pages should not make a formal representation look predictive.

Use 100,000 shuffles of the externally supplied target labels, preserving the
complete target-degree multiset and forbidding duplicate targets for the only
two-edge source page. Recompute the degree prior inside every world. Report
MRR, top-three count, inclusive local tails, and maximum-over-six tails. The
alternative readings remain observations of one manuscript; GDT062 supplies
one derived display view and no replication is claimed.

## Decision and ceiling

PAGE_HOST transfer is called interesting only if its MRR or top-three count is
positive after the six-model maximum and beats both nuisance controls. Failure
limits the GDT148 selected-relation lead; it cannot prove that PAGE_HOST is
content-free.

No plant or component identity, semantic role, gloss, word, morpheme, POS,
sound, language, plaintext, meaning, or translation may be inferred. f84r is
not retained, joined, scored, or targeted.
