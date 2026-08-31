# GDT698 / V71 — exakter Aktionsoberflächen-Rahmenreplay

Status: `PASS_V71_6_SURFACES_10_OCCURRENCES__9_EXISTING_MATCHES_1_UNBOUND_HELD__0_CROSS_REPLAYS__ZERO_WORD_DELTA`

Die sechs Aktionsoberflächen der sieben V70-Mikrorecords kommen im vollständigen 479-Token-Bestand zehnmal vor. Neun Vorkommen sind bereits genau die neun gebundenen Zielaktionen. Das einzige offene Vorkommen bleibt offen.

## Alle zehn Vorkommen

| ID | Stelle | Form | Glosse | exakter Rahmen | Entscheidung |
|---|---|---|---|---|---|
| A001 | `f104v.2#6` | `qokamdy` | ein Maß nehmen und erhitzen | `T009` | `ALREADY_ADMITTED_EXACT_SELF_REPLAY` |
| A002 | `f105v.1#4` | `ykaiin` | erhitze hiervon auf Stufe III | `T001` | `ALREADY_ADMITTED_EXACT_SELF_REPLAY` |
| A003 | `f113v.17#7` | `yteeeor` | hiervon eine Portion bis zur letzten Stufe abkühlen | `T002` | `ALREADY_ADMITTED_EXACT_SELF_REPLAY` |
| A004 | `f75r.3#4` | `qey` | die vorstehende Mittelstufenportion anschließend nehmen | `T003` | `ALREADY_ADMITTED_EXACT_SELF_REPLAY` |
| A005 | `f77r.38#6` | `qol` | Drogenstoff zugeben | `T005` | `ALREADY_ADMITTED_EXACT_SELF_REPLAY` |
| A006 | `f77r.38#9` | `qol` | Drogenstoff zugeben | `NONE` | `UNBOUND_NO_EXACT_PARTICIPANT_FRAME` |
| A007 | `f80v.35#5` | `qol` | Drogenstoff zugeben | `T004` | `ALREADY_ADMITTED_EXACT_SELF_REPLAY` |
| A008 | `f80v.35#6` | `qol` | Drogenstoff zugeben | `T008` | `ALREADY_ADMITTED_EXACT_SELF_REPLAY` |
| A009 | `f86v6.25#4` | `qodar` | Drogenanteil I abmessen | `T007` | `ALREADY_ADMITTED_EXACT_SELF_REPLAY` |
| A010 | `f86v6.25#5` | `ykaiin` | erhitze hiervon auf Stufe III | `T006` | `ALREADY_ADMITTED_EXACT_SELF_REPLAY` |

## Das offene `qol` auf f77r.38#9

Die grobe Form ist verführerisch: Wie bei `qol` #6 geht ein zweigliedriger Nominalblock voraus. Das ist aber nur eine Klauselform, kein Teilnehmerrahmen.

| bekannte qol-Kante | erwartete exakte Folge | tatsächlich vor #9 | Abweichungen | Urteil |
|---|---|---|---:|---|
| C004 | `olkar<br>y<br>qol` | `ltaiin<br>shedy<br>qol` | 2 | Der geschriebene Zielanteil und der Hierzu-Verweis fehlen; ltaiin|shedy ist kein olkar|y-Rahmen. |
| C005 | `chcphey<br>qol` | `shedy<br>qol` | 1 | Unmittelbar vor #9 steht der Feuchtzustand shedy, nicht das zugelassene Zugabeobjekt chcphey. |
| C008 | `olkar<br>y<br>qol<br>qol` | `qol<br>ltaiin<br>shedy<br>qol` | 3 | Die zwei qol sind durch ltaiin|shedy und eine neue Nominalklausel getrennt; der gemeinsame olkar-Zielrahmen fehlt. |

Sichere Arbeitsausgabe:

> Holz, kalt auf Stufe III; mittlere Feuchtstufe erreicht. **[Teilnehmerbindung offen:]** Drogenstoff zugeben.

## Ergebnis

- 6 Aktionsoberflächen, 10 Vorkommen, 9 schon gebundene Zielaktionen.
- 9 exakte Template-Treffer, sämtlich nur am eigenen Quellvorkommen.
- 0 exakte Cross-Occurrence-Replays und 0 neue Mikrorecords oder Kanten.
- `ykaiin` besitzt zwei und `qol` drei verschiedene bereits zugelassene Teilnehmerrahmen: Die Aktionsoberfläche allein bestimmt ihr Objekt oder Ziel nicht.
- 479 Token, 51 Zeilen und 3 gebundene Spannen bleiben unverändert.
