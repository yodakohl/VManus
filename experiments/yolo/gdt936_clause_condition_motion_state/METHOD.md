# GDT936 — Ausführung

Quelle und Entdeckungsabgrenzung: [PREREGISTRATION.md](PREREGISTRATION.md).
Nach der vollständigen Konkordanz ausgewählte Kandidaten: src/MODEL.json,
gebunden in MODEL_LOCK.json. Die bisherigen M/R/T-Werte bleiben bytegleich.

src/explore.py erfasst vier Ziel- und acht Vergleichsformen. src/run.py schreibt
alle1408 Gruppen in beiden Modellen sowie die expliziten lokalen .37-Rollen.
src/validate.py rekonstruiert Erfassung, Ganzwerte, Quelltreue, Leserunterschiede
und die sechs Bedingungs-/Folgezuordnungen; deterministischer Replay ohne
Laufzeitstempel. Tatsächliche Wärme oder Folgeereignisse werden nicht abgeleitet.
Die manuelle Inhaltsentscheidung steht in [REPORT.md](REPORT.md).
