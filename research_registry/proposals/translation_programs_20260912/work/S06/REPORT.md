# S06 — zwei vollständige Fassungen, eine nicht tragfähige Zusatzbrücke

Die feste P05-V03-Lesung ergibt auf f32v.7–11 eine lokale Entnahme–Sieben–Zurückhalten-Kette und eine zweite lokale Zerstoßen–Verarbeiten-Kette. Eine durchgehende Herstellung vom vorher genannten Pflanzenpulver bis zum Endprodukt ergibt sich daraus nicht. Die nominale Listenfassung bleibt ebenfalls möglich. Keine Wortbedeutung wurde bestätigt.

Die 39 Quellgruppen sind in beiden Fassungen vollständig ausgerichtet: 35 mit hypothetischem P05-Wert, vier offen (ksho, d, l, da). Das ist Entwurfsabdeckung, keine Trefferquote. P05 wurde schon an diesem Text entwickelt; sämtliche Inhalte und Vorgängermodelle waren vor der Synthese bekannt. Keine neue oder zurückgehaltene Seite wurde geöffnet; f84/f84r bleiben geschlossen. Diese fünf Zeilen sind nicht das ganze physische Blatt. Keine unabhängige Bedeutungsprüfung, Suche-Gegenkontrolle oder Signifikanzbehauptung.

## Konkrete Fassungen

[Herstellung M](READING_M.md) und [Liste K](READING_K.md) geben jede Zeile mit Quelle und vollständiger Prosa wieder. [ALIGNMENT_M.tsv](ALIGNMENT_M.tsv) und [ALIGNMENT_K.tsv](ALIGNMENT_K.tsv) binden jedes Wort. Winkelklammern markieren ergänzte Beziehungen; offene Gruppen bleiben sichtbar. [FIXED_LEXICON.tsv](FIXED_LEXICON.tsv) hält dieselben Nomen und feste Tätigkeitswerte, in K ausschließlich nominalisiert. K ist eine bereits aus P05 bekannte Rivalenfamilie, keine neue Entdeckung.

| Abschnitt | M: feste Herstellungsfassung | K: feste Listenfassung | Konsequenz / offene Bindung |
|---|---|---|---|
| .7 | Zerreiben, Stehenlassen, Vermischen mit Rest | Tätigkeits-, Zeit-, Orts- und Mengenfelder | Anfangsmaterial fehlt; kleine Dosis ohne eindeutiges Ziel |
| .8 | Getrocknetes Gut / Pflanzenpulver mit Dosen; aus abgeteilter Portion Feinanteil entnehmen | Stoffe, Dosisfelder, Portion, Entnahme, Feinanteil | Herkunft der abgeteilten Portion nicht geschrieben gebunden |
| .9 | Feinanteil sieben; Pflanzenmark und Pflanzenportion zu je Q zurückhalten | Sieben, Filter, Zurückhalten, zwei dosierte Stoffeinträge | Zwei gleichzeitige getrennte Ausgaben sind zusätzliche Annahme |
| .10 | Flüssigkeit, Öl, trockene Blüten Q; trockenes Pflanzengut zerstoßen | Stoff-/Qualitäts-/Mengen- und Tätigkeitsfelder | Keine gelesene Mischhandlung verbindet Öl/Blüten mit dem Zerstoßen |
| .11 | Letztes zerstoßenes Material mit Flüssigkeit verarbeiten | Verarbeitung mit Flüssigkeit als Eintrag | Lokale Fortführung angenommen; keine Verbindung zum Siebgut |

[FRAMES_M.tsv](FRAMES_M.tsv) enthält alle acht Tätigkeitsstellen, ihre Eingaben, Ausgaben und Ergänzungen. [ASSUMPTIONS.tsv](ASSUMPTIONS.tsv) nennt die zusätzlichen Bedingungen. Es sind zwei lokale Ketten und ein unvollständiger Anfangsablauf, kein ausführbares Gesamtrezept. K ersetzt diese Genealogie durch nominale Eintragsstruktur; auch deren Syntax ist nicht unabhängig gebunden.

## Bisher widersprüchlich belegte Werte

[PRIOR_WORD_VALUES.tsv](PRIOR_WORD_VALUES.tsv) vergleicht sämtliche vorkommenden Wortformen mit P05, P04, P11, P25 und S05. Nicht zugewiesen bedeutet nur im betreffenden Modell offen.

| Form | Gegensätzliche bisherige Hypothesen | Hier festgehalten |
|---|---|---|
| qotchy / cfhy | Sieben/Filter; Zweck/Bindung feuchter Masse; Zerkleinern | P05 siebe / Filter |
| sho / chy | Flüssigkeit/verarbeite; Tätigkeit/Wasser | P05 Flüssigkeit/verarbeite an jeder Stelle |
| chocthy / cthaiin | Pflanzenmark/Pflanzenportion; Fein-/Grobpulver; feine/grobe Fraktion | P05 Pflanzenmark/Pflanzenportion; keine Größenordnung übernommen |
| daiin | unbekannte feste Dosis; Maß Γ; III | feste Dosis Q, keine entschlüsselte Zahl |

Die Öl-Blüten-Mischung aus S05 wird nicht übernommen: Sie setzte sho als Verb voraus und nahm bei derselben Listenregel auch cthol mit. Ebenso wäre „feine und grobe Siebfraktion zu je drei Teilen“ eine unbegründete Mischung mehrerer Programme. Wiederholte Übernahme derselben freien Wortwerte liefert keine unabhängige Bestätigung.

## Alle Mengen und die geprüfte Zusatzbrücke

[QUANTITIES.tsv](QUANTITIES.tsv) enthält alle sieben Mengenstellen: sechs daiin=Q und ein dain=kleine Dosis D. Nach unveränderter P05-Doppelregel verteilt .8:2–3 die Dosen auf odan (.7:10) und otchol (.8:1). Weitere Q stehen für ctho, chocthy, cthaiin und chor. D bleibt ungebunden. Weder Q noch D erhält eine Zahl. Die Wahl von P05s Doppelregel ist eine Hypothese, keine Entscheidung gegen die anders gebundene P14-Mengenfassung.

Vorab festgelegte Zusatzfrage M+: Kann die abgeteilte Portion qotaiin unmittelbar aus der einen ctho-Dosis Q stammen? Wenn Q bei allen drei betroffenen Stoffen dieselbe positive tatsächlich gehandhabte Masse bezeichnet, die Entnahme keine Masse hinzufügt und die beiden zurückbehaltenen Ausgaben getrennt und gleichzeitig je Q wiegen, gilt:

`2Q = beide Ausgaben zusammen ≤ Feinanteil F ≤ abgeteilte Portion P ≤ Ausgangsdosis Q`.

Damit müsste `Q ≤ 0` gelten, im Widerspruch zu `Q > 0`. Diese Konjunktion ist tatsächlich unvereinbar. [MASS_AUDIT.json](MASS_AUDIT.json) enthält die Prämissen, Ableitung und einen konsistenten Zeugen ohne Herkunftsbrücke: bei bloßer Skalennormierung Q=1, P=F=2 und beiden Ausgaben=1. Die Eins ist keine gelesene Zahl. Ohne die Brücke muss die unbekannte Ausgangsportion unter denselben Massenannahmen mindestens 2Q liefern.

Das ist eine Konsequenz zusätzlich angenommener Stoffidentitäten und Mengen, keine Beobachtung zweier gewogener Manuskriptstoffe. Dosis kann je Substanz eine andere Masse bedeuten; die zwei Nennungen könnten Eingaben, Alternativen oder dieselbe Portion sein. Diese Möglichkeiten wurden nicht nachträglich als gerettete M+-Fassungen gewertet. Der Test entscheidet nicht zwischen ihnen und identifiziert insbesondere nicht das falsche Wort. K macht keine Ausführungsbilanz und hat deshalb für diesen Vergleich keine Bestätigungskapazität.

## Entscheidung und nächster sinnvoller Schritt

M+ wird als geschlossene Herkunftskette unter den festgelegten gemeinsamen Massenannahmen verworfen. M bleibt ein offen dokumentierter Herstellungsentwurf mit zwei lokalen Ketten; K bleibt nominaler Rivale. Keine der Fassungen ist eine fast vollständige plausible Entzifferung: hohe Zuordnungsabdeckung durch frei gesetzte Karten ersetzt weder Syntax noch Stoffidentität. Zurückgehaltene Seiten bleiben deshalb unbenutzt.

Der nächste gezielte Inhaltsschritt wäre, die Eingabe-/Ausgabe- versus Alternativfunktion der beiden dosierten Nomen auf .9 im Zusammenhang aller schon exponierten Doppel-Dosis-Kontexte fest auszuschreiben. Das verändert die tatsächliche Stoffgeschichte und könnte die rivalisierenden Lesungen weiter trennen. Kein automatisches Wiederholen der hier algebraisch widerlegten Konjunktion, keine weiteren freien Synonyme zur Glättung.

Reproduktion: `python research_registry/proposals/translation_programs_20260912/work/S06/build.py`, danach `python research_registry/proposals/translation_programs_20260912/work/S06/validate.py`. Die separate Prüfung besteht für Quellenbytes, vollständige Ausrichtung, stabile Wortwerte, sämtliche Mengenstellen und die bedingte Algebra. Sie bestätigt die Umsetzung, nicht die Bedeutung. [DECISION.md](DECISION.md) fixierte diese exponierte Synthese vor der Ausführung; [SOURCE.json](SOURCE.json) bindet ihre Quellen.

Repository-Prüfung: S06-Validator und Registry-Prüfung PASS; die Prüfung des exakt bereitgestellten Veröffentlichungsbaums auf private Inhalte und Diff-Fehler PASS. Die globale Altbestandsprüfung bleibt bei acht schon bestehenden Fehlern: sieben ungebundene Reproduktionsdateien in GDT600 und ein veralteter Experimentindex. Diese liegen außerhalb S06 und wurden nicht verändert.
