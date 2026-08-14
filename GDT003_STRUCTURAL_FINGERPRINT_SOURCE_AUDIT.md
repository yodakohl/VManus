# GDT003 structural fingerprint source audit

Status: `FROZEN_BEFORE_TRANSFORMATION_SCORING`

## Uniform source policy

Universal Dependencies 2.18 is the source for historical corpora because its
treebanks expose stable native surface `FORM` fields and document/sentence
routing. The comparator deliberately ignores every linguistic annotation.
The modern sensitivity tier uses plaintext extracts from frozen random
main-namespace Wikipedia pages, with exact page revisions and acquisition
response hashes recorded in `gdt003_structural_fingerprint_source_provenance.json`.

Primary source documentation:

- Universal Dependencies language/treebank catalogue:
  https://universaldependencies.org/languages.html
- UD Middle Armenian ArmTDP:
  https://universaldependencies.org/treebanks/axm_armtdp/index.html
- UD Old Georgian GLC:
  https://universaldependencies.org/treebanks/oge_glc/index.html
- UD Old Church Slavonic PROIEL:
  https://universaldependencies.org/treebanks/cu_proiel/index.html
- Wikimedia Action API:
  https://www.mediawiki.org/wiki/API:Main_page

## Exact historical coverage

| requested comparison | frozen historical source | disposition |
| --- | --- | --- |
| Cuman/Kipchak | none at matched capacity | Cuman unsupported; modern Kazakh is sensitivity only |
| Middle Armenian | UD Middle Armenian-ArmTDP | exact variety, but the v2.18 treebank is only about 1,000 tokens and may be unrankable |
| Adyghe/Circassian | none historical at matched capacity | modern Adyghe sensitivity only |
| Abkhaz | none historical at matched capacity | modern Abkhaz sensitivity only |
| Avar/Lezgian | none historical at matched capacity | modern Avar and Lezgian sensitivities only |
| historical Georgian | UD Old Georgian-GLC | exact historical comparator |
| Early Maltese/Siculo-Arabic | none at matched capacity | modern Maltese sensitivity only |
| Old Church Slavonic | UD Old Church Slavonic-PROIEL | exact historical comparator |
| Hungarian | no historical corpus frozen | modern sensitivity |
| Basque | no historical corpus frozen | modern sensitivity |
| Latin/Italian/Greek controls | Latin PROIEL, UD Italian-Old, Ancient Greek PROIEL | historical controls |
| German/Arabic controls | no historical corpus frozen in this pass | matched modern controls |

The absence of a historical corpus is a result of the source audit, not
license to rename a modern corpus. Neither corpus family labels nor known
linguistic typology enters transformation discovery or scoring.

## Biases frozen before scoring

- Wikipedia and UD differ in genre and editorial/tokenization practice; the
  two strata are never pooled as if they were exchangeable.
- Native scripts are preserved. Orthographic character inventory is part of
  the measured fingerprint and a major confound, not a phoneme mapping.
- Wikipedia pages are a random frozen draw, not a balanced linguistic corpus.
- UD `FORM` tokenization is source/editorial tokenization. It is not made
  equivalent to Voynich physical groups by assumption.
- Low-capacity exact historical corpora remain visible but cannot obtain a
  primary distance rank by extrapolation.
- f84r is excluded before Voynich surface retention.
