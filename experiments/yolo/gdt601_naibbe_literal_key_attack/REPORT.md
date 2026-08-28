# GDT601 — the published Naibbe table is not a Voynich key

Status: **LITERAL_NAIBBE_KEY_REJECTED_ON_F84_FREE_91_FOLIO_CORPUS**.

## Result

The complete published Naibbe table passes its own hard positive control and
fails the independent Voynich target.

| target model | corpus | strict token coverage | observed bits/char | shuffled mean | order z |
|---|---|---:|---:|---:|---:|
| Latin | shipped Naibbe Pliny control | 100.00% | -3.5151 | -5.2747 | **+147.24** |
| Italian | shipped Naibbe Pliny control | 100.00% | -4.4978 | -5.7164 | **+89.00** |
| Latin | Voynich, 91 f84-free physical folios | 79.86% | -5.1842 | -5.1667 | **-2.33** |
| Italian | Voynich, 91 f84-free physical folios | 79.86% | -5.5295 | -5.5006 | **-2.33** |

The high Voynich coverage is not evidence for the key: the table was designed
from common Voynich-looking strings. Only 41.12% of Voynich token types parse,
and the parsed sequence is less language-like than its own order-shuffled
controls. The strongest isolated outputs include strings such as `rritermi`,
`tedonnae`, and `piano ...`; their failure to aggregate into corpus-wide order
signal shows why local readable fragments are not decipherment evidence.

## Consequence

Naibbe remains a useful demonstration that a verbose homophonic cipher can
imitate several Voynich statistics. Its published 414-entry table is not the
manuscript's Latin or Italian decoding table under the tested normal
orientation and gap model. The broader variable-segmentation/homophonic family
remains open only if an unknown key can first be recovered on a known control
without using the published table, then produces held target signal.

No old German workshop gloss was used. No Voynich lexeme, sound, plaintext,
language, or meaning follows. f84/f84r was forbidden and never materialized.
