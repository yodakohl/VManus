# GDT669 historical codebook memo

## Lens

1. You are a multilingual fifteenth-century medical-scribe specialist familiar with recipe breviaries, weights, grades, and learned drug names.
2. You compare the Voynich working morphology with real Latin, Italian, German, Arabic-Latin, and apothecary abbreviation habits circa 1380–1460.
3. You seek a plausible mixture of technical stems and memorized wholes that predicts composition rather than superficial letter matches.
4. You allow exploratory analogies, but an analogy must improve the concrete card and may not overwrite the manuscript-internal spelling system.
5. You distinguish noun, command, measure, state, and closing formula and reject modern generic process language.

## Historical format comparison

The comparison supports a *format*, not a glyph decipherment. A fifteenth-century recipe collection can mix Latin and vernacular, short commands, ingredient or drug names, preparations and dosage statements. Wellcome MS.5262 is a fifteenth-century collection of 129 recipes in Latin and English; Wellcome MS.418 contains mid-fifteenth-century recipes for medicinal waters and other remedies in Latin and Langue d'Oc; Wellcome MS.683 is a mid-fifteenth-century north-east Italian Latin recipe collection organized in the tradition of Rhazes' *Liber nonus ad Almansorem*. These are good analogues for a hybrid technical register, not donors for Voynich letter values. [Wellcome MS.5262](https://wellcomecollection.org/works/hkxxeu85), [Biblissima/Wellcome MS.418](https://portail.biblissima.fr/en/ark:/43093/mdatac6f1f20edb381b8ec397ef638d5578d86af71443), [Biblissima/Wellcome MS.683](https://portail.biblissima.fr/fr/ark:/43093/mdata72ef62bcc641a30a9bbff144384d5ac965fa76f8)

The British Library catalogue for Harley MS 2381 separately lists a mid-fifteenth-century medical-recipe compendium and preserves a short vernacular recipe opening with “Take”. That supports the coexistence of compact imperatives and nominal recipe entries, again without identifying `q` with *recipe* or any other Latin word. [British Library, Harley MS 2381](https://searcharchives.bl.uk/catalog/040-002048212)

## Internal decisions

1. Free `sh` is the strongest new practical card: the inherited productive head already means moistening, and its fourteen free occurrences allow the short imperative **weiche ein**. No new role is needed.
2. `shear` (22 positions) fixes the productive ladder `SH_MOIST+E_MIDDLE+AR_FRACTION_I`: **erste bis zur Mittelstufe eingeweichte Fraktion**. The nominal default avoids adding an unattested command head.
3. `shek` (10) is an ordered operation: **bis zur Mittelstufe einweichen und dann erhitzen**. It is not the generic phrase “mäßig behandeln”.
4. `shedaiin` (10) matches `shedain` but retains the third dose: **drei Dosen bis zur Mittelstufe eingeweichter Droge**.
5. `ro` (7) is the compact material/preparation noun **Wurzelansatz**. Free `r` remains context-sensitive; the bound `R_ROOT+O_PREP` composition is unproblematic.
6. `cthal` (7) is **Krautdroge, Rohstoff I**, not a named species. This parallels concise materia-medica headings without importing a Latin plant name.
7. `dals` (8) and `dalar` (5) separate a terminal species/charge from a first fraction: `D+AL+S` versus `D+AL+AR`. The shared default is measurement of raw drug I, not a universal reading of `dal`.
8. `oeees` (6) and `loeees` (2) preserve the long/final stage before terminal charge `s`. Final `s` is never exported backward as initial seed.
9. `sary` uses initial seed plus first fraction plus closure. It is not split as terminal species because the `s` is visibly initial.
10. `chordy` keeps the learned longest head `chor=Pflanzenteil`; it must not collapse into `CH_DRY+OR_PORTION+DY`.
11. `lkeol`, `shokol` and `olkair` exploit the established bound `OL_MATERIAL`. “Auszug” is retained only as a rival where a preceding substance head makes a result plausible; no carrier liquid is named.
12. `dcheey`, `pched`, `alchdy` and `psheedy` distinguish dose, powder, raw drug and completion. They are executable or concrete without the filler “weiter bearbeiten”.
13. `eeckhy` places an end-stage marker before the learned composite head. Because the surface is exactly spellable but the ordering is marked, the German is economical: **Arzneikompositum vollständig bereiten und abschließen**.
14. `okytaiin` and `oytor` remain the only learned wholes. Both contain an internal `y` whose productive V45 scope forbids an unlicensed split; memorizing the full card is safer than inventing an internal reader boundary.
15. `kchokchy` preserves all five visible operations: heat, dry, prepare, reheat, lightly redry. A historical scribe could abbreviate repetitive workshop stages, but the modern rendering may not erase them.

## Candidate blocks

No new productive block is required. The strongest *candidate family observations* are:

- `SH+E+AR / SH+E+D+AIN / SH+E+D+AIIN`: one moisture-stage head followed by fraction or dose tails;
- `D+AL+S / D+AL+AR`: measured raw-drug head followed by charge or fraction;
- `O+EEE+S / L+O+EEE+S`: final-stage preparation charge, optionally with a wood head.

These are compositions of existing roles, not new stems. The only exact-whole proposals are `LEARNED_OKYTAIIN_WHOLE` and `LEARNED_OYTOR_WHOLE`, both necessitated by the current internal-`y` scope.

## Claim boundary

The historical manuscripts show that multilingual recipe collections, compact commands and learned drug/preparation names coexist around the relevant period. They do not prove that the Voynich surfaces are Latin, Italian, German, Arabic-Latin, or abbreviations of any cited word. All thirty-seven German values remain concrete, replaceable workshop defaults governed first by V45 spelling and context.
