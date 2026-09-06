# GDT851 — exact two-group tandem blocks exist

**Two complete ABAB spans survive unchanged in all three readings:**

- f30r.11, groups2–5: `cheor chey cheor chey`.
- f8r.19, groups5–8: `shol kaiin shol kaiin`.

All three internal boundaries are definite in each reading. A and B differ,
so these are primitive period2 blocks, not one group repeated four times.
They are two physical source loci on two folios, not six independent examples.
This establishes precise written passage anchors; it does not prove a phrase,
a copying procedure, a meaning or statistical surprise.

## Complete fixed-period census

| Reading | p | Candidate windows | Eligible definite windows | Primitive tandems | Nonprimitive tandems | Physical folios with primitive hits |
|---|---:|---:|---:|---:|---:|---:|
| ZL3b | 1 | 28226 | 25309 | 248 | 0 | 71 |
| ZL3b | 2 | 20724 | 15396 | 4 | 0 | 4 |
| ZL3b | 3 | 13746 | 8472 | 0 | 0 | 0 |
| IT2a | 1 | 27744 | 27070 | 264 | 0 | 75 |
| IT2a | 2 | 20243 | 18805 | 5 | 0 | 4 |
| IT2a | 3 | 13293 | 11887 | 0 | 0 | 0 |
| RF1b | 1 | 27809 | 26627 | 200 | 0 | 66 |
| RF1b | 2 | 20319 | 17932 | 3 | 0 | 3 |
| RF1b | 3 | 13387 | 10962 | 0 | 0 | 0 |

All overlapping candidate spans are retained in WINDOWS_<reading>.json.
Candidates have2p stored groups available in one source line; eligibility
additionally requires consecutive source indices and every internal boundary
definite on both adjoining groups. Adjacent repeats and larger windows therefore
have different denominators. No maximal-run merging or across-line search.

The724reading-specific primitive hits include712period1 and12period2 hits.
Those12period2 observations cover6distinct source loci on5physical folios.
No period3 tandem occurs in the fixed eligible inventory. This absence
neither rejects longer repetitions nor licenses an enlarged search here.

## Every higher-period hit

| Reading | Locus | Start group | Primitive block repeated twice |
|---|---|---:|---|
| ZL3b | f30r.11 | 2 | `cheor / chey` |
| ZL3b | f35v.12 | 2 | `d / aiin` |
| ZL3b | f75v.44 | 6 | `chedy / qol` |
| ZL3b | f8r.19 | 5 | `shol / kaiin` |
| IT2a | f15v.7 | 4 | `s / chy` |
| IT2a | f30r.11 | 2 | `cheor / chey` |
| IT2a | f75v.41 | 6 | `ol / shey` |
| IT2a | f75v.44 | 6 | `chedy / qol` |
| IT2a | f8r.19 | 5 | `shol / kaiin` |
| RF1b | f30r.11 | 2 | `cheor / chey` |
| RF1b | f75v.41 | 6 | `ol / she@222;` |
| RF1b | f8r.19 | 5 | `shol / kaiin` |

f75v.44 is the same line just inventoried in GDT850; its recurrence here is
not a new physical discovery. It adds a particular chedy/qol phase of its
literal repetition to this complete census. The single-letter groups at
f35v.12 and f15v.7 illustrate why raw group patterns must not automatically
be called multiword phrases. RF1b ol/she@222; is preserved literally rather
than normalized into IT2a ol/shey. Reader-only hits remain disclosed.

## Every complete higher-period source line

The following strings display complete raw groups separated for readability.
Outside each scored span, displayed spaces do not assert definite native
boundaries; exact separator flags, source IDs, indices and line metadata
remain in HIGHER_PERIOD_LINES.json and SOURCE_<reading>.json.

| Reading | Locus | Complete source groups |
|---|---|---|
| ZL3b | f30r.11 | `qotchor cheor chey cheor chey so[eeb:een] ydey sor daiin` |
| ZL3b | f35v.12 | `dchaiin d aiin d aiin dal s` |
| ZL3b | f75v.44 | `olshees ol sheckhy qokain ol chedy qol chedy qol keey qolchedy chealy` |
| ZL3b | f8r.19 | `sair cheain cphol dar shol kaiin shol kaiin dai kam` |
| IT2a | f15v.7 | `coy choiin sho s chy s chy tor ols` |
| IT2a | f30r.11 | `qotchor cheor chey cheor chey soiin ydey sor daiin` |
| IT2a | f75v.41 | `sal shedy qokain shey qoin ol shey ol shey qoky qol cheey chl or sheolo` |
| IT2a | f75v.44 | `olshees ol sheckhy qokain ol chedy qol chedy qol keey qolchedy chealy` |
| IT2a | f8r.19 | `sair cheain cphol dar shol kaiin shol kaiin daikam` |
| RF1b | f30r.11 | `qotchor cheor chey cheor chey soeeb ydey sor daiin` |
| RF1b | f75v.41 | `s@221;l she@152;y qokain she@222; qoin ol she@222; ol she@222; qoky qol chee@222; chl @221;r sheolo` |
| RF1b | f8r.19 | `sair cheain cphol dar shol kaiin shol kaiin daikam` |

## Decision, provenance and limits

Retain the two all-reading exact period2 anchors and all alternate-reading
cases; the fixed census is complete. No copying model, codebook, phrase
meaning, null model or next-period extension follows automatically. A later
mechanism study would need a distinct predeclared discriminator.

Public registration86cee535 preceded the guarded extraction. The guard
selected96184raw rows from179selectors, rejected2122sealed rows and17164
nonallowed rows. f84/f84r were rejected before payload materialization.
No image, new selector, OCR, normalization or inherited semantic tag was used.

The independent validator reconstructed every window from the complete saved
source lines, checked native boundaries, tested all smaller finite-word
periods directly, and reproduced counts, folios, hits and higher-period
lines. Byte-identical cached replay passed. Source/artifact binding passed.
Validation concerns source inventory and arithmetic, not manuscript meaning.
Acquisition, independent validation and replay took approximately3.5seconds;
report preparation stayed within the five-minute execution allowance.
