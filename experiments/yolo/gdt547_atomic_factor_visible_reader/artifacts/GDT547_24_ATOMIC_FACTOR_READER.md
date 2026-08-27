# GDT547 — 24 atomare und faktorielle Restkarten

Status: `PASS_24_ATOM_FACTOR_CARDS_VISIBLE__21_OLD_DECK_COVERS__3_SPECIAL_ROUTES`

Alle24 Oberflächen besitzen jetzt eine vollständige sichtbare Route und eine
vollständige deutsche Arbeitslesung.21 werden vom alten GDT519-Renderer-Deck
buchstabengetreu abgedeckt:16 rein kanonisch, fünf mit mindestens einem alten
gelernten Kurzrenderer. Die drei übrigen benutzen je einen bereits begrenzten
Mechanismus (`aiir`, präfixbedingtes `aiis`, lokales q-null).

### `OLD26_ALL_CANONICAL_VISIBLE_ATOMS` (16)

| Oberfläche | sichtbare Route | Arbeitslesung | Ausführung |
| --- | --- | --- | --- |
| `axor` | `a→A_ADDR | x→LOCAL_X | or→OR` | Hier; mit lokalem X-Zeichen-/Namenskern; Einheit. | `READ_CURRENT_LOCAL_X_OVERLAY` |
| `cheda` | `ched→CHD | a→A_ADDR` | Bearbeiten; hier. | `READ_FACTOR_GREEN` |
| `cheeo` | `ch→CH | ee→EE | o→O` | Nehmen; auf Grad II; zur Ausführung. | `READ_FACTOR_GREEN` |
| `chpady` | `ch→CH | p→P | a→A_ADDR | dy→DY` | Nehmen und einsetzen; hier; abschließen. | `READ_FACTOR_GREEN` |
| `chxar` | `ch→CH | x→LOCAL_X | ar→AR` | Nehmen; mit lokalem X-Zeichen-/Namenskern; vom Ausgang. | `READ_CURRENT_LOCAL_X_OVERLAY` |
| `da` | `da→DA` | Auf der zweiten Stufe. | `READ_FACTOR_GREEN` |
| `dcheey` | `d→D_ADDR | ch→CH | ee→EE | y→Y` | Hier; den Posten nehmen; auf Grad II. | `READ_FACTOR_GREEN` |
| `keeol` | `k→K | ee→EE | ol→OL` | Geben; auf Grad II; fortsetzen. | `READ_FACTOR_GREEN` |
| `ld` | `l→L | d→D_ADDR` | Über die Verbindung; hier. | `READ_FACTOR_GREEN` |
| `lpchees` | `l→L | p→P | ch→CH | ee→EE | s→S` | Über die Verbindung; einsetzen, nehmen und wählen; auf Grad II. | `READ_FACTOR_GREEN` |
| `shain` | `sh→SH | ain→AIN` | Den Anteil halten. | `READ_FACTOR_GREEN` |
| `shd` | `sh→SH | d→D_ADDR` | Halten; hier. | `READ_FACTOR_GREEN` |
| `shddy` | `sh→SH | d→D_ADDR | dy→DY` | Halten; hier; abschließen. | `READ_FACTOR_GREEN` |
| `shso` | `sh→SH | s→S | o→O` | Halten und wählen; zur Ausführung. | `READ_EXPLICIT_OBSERVED_PAIR_DEFAULT` |
| `shtchy` | `sh→SH | t→T | ch→CH | y→Y` | Den Posten halten, einstellen und nehmen. | `READ_FACTOR_AMBER_LOCAL_APPENDIX` |
| `todeeey` | `t→T | o→O | d→D_ADDR | eee→EEE | y→Y` | Den Posten einstellen; zur Ausführung; hier; auf Grad III. | `READ_FACTOR_GREEN` |
### `OLD26_MIXED_CANONICAL_AND_LEARNED_RENDERERS` (5)

| Oberfläche | sichtbare Route | Arbeitslesung | Ausführung |
| --- | --- | --- | --- |
| `chcpheor` | `chcph→CH+CH+P | e→E | or→OR` | Die Einheit nehmen, erneut nehmen und einsetzen; auf Grad I. | `READ_FACTOR_GREEN` |
| `cphaiin` | `cph→CH+P | aiin→AIIN` | Den Wert nehmen und einsetzen. | `READ_FACTOR_GREEN` |
| `pdaiin` | `p→P | daiin→AIIN` | Den Wert einsetzen. | `READ_FACTOR_GREEN` |
| `qotedal` | `qot→OT | e→E | dal→AL` | Danach; auf Grad I; am Zielort. | `READ_FACTOR_GREEN` |
| `tocpheey` | `t→T | o→O | cph→CH+P | ee→EE | y→Y` | Den Posten einstellen, nehmen und einsetzen; zur Ausführung; auf Grad II. | `READ_FACTOR_GREEN` |
### `CURRENT30_DOMINANT_SHORT_RENDERER` (1)

| Oberfläche | sichtbare Route | Arbeitslesung | Ausführung |
| --- | --- | --- | --- |
| `chedaiir` | `ched→CHD | aiir→IIN+R` | Bearbeiten und markieren; auf der bezeichneten Stufe. | `READ_FACTOR_GREEN` |
### `PREFIX_CONDITIONED_CURRENT_AIIS_CHANNEL` (1)

| Oberfläche | sichtbare Route | Arbeitslesung | Ausführung |
| --- | --- | --- | --- |
| `faiis` | `f→LOCAL_CHAR_F | aiis→IIN+S` | Hier; auf der bezeichneten Stufe; wählen. | `READ_FACTOR_GREEN` |
### `GDT535_LOCAL_Q_NULL_PLUS_CANONICAL_ATOMS` (1)

| Oberfläche | sichtbare Route | Arbeitslesung | Ausführung |
| --- | --- | --- | --- |
| `qef` | `q→NULL_Q | e→E | f→LOCAL_CHAR_F` | Auf Grad I; hier. | `READ_FACTOR_GREEN` |

## Offene Nähte

Von52 direkten Atompaaren kommen40 schon innerhalb alter vollständiger Karten
vor. Zwölf Nähte auf neun Karten sind neu: `axor`, `cheda`, `chedaiir`, `chpady`, `chxar`, `faiis`, `shain`, `shso`, `tocpheey`. Das nimmt den
Karten nicht ihre Defaultbedeutung. Es sagt nur, an welcher Stelle der heutige
Reader auf Faktor-/Kontextlogik oder eine beobachtete Einzelkarte statt auf
eine alte direkte Naht angewiesen ist.

Der ältere GDT446-Faktorleser gibt im beobachteten Kontext20 grüne, eine
gelbe und drei Stopentscheidungen. Zwei Stopps (`axor`, `chxar`) entstehen nur,
weil sein eingefrorenes Deck dem späteren f66r-`LOCAL_X`-Overlay vorausgeht.
Der verbleibende Stopp `shso` ist der ehrliche Einzeldefault für das neue
Direktpaar `SH>S`. `shtchy` bleibt wegen des lokalen `SH>T`-Paares gelb.

Keine Oberfläche bleibt bedeutungslos, aber diese Unterschiede bleiben in
jeder Karte sichtbar.
