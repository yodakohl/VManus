"""Deterministic reporting of every already tested equal-length pair."""
from collections import Counter
import csv
import json
from pathlib import Path

E = Path(__file__).resolve().parents[1]
A = E / 'artifacts'
result = json.loads((A / 'RESULT.json').read_text())
panels = json.loads((A / 'PARAGRAPHS.json').read_text())
pairs = json.loads((A / 'PAIR_CONSEQUENCES.json').read_text())
rows = []
for edition, candidates in pairs.items():
    by_id = {p['id']: p for p in panels[edition]}
    for pair in candidates:
        a, b = by_id[pair['a']], by_id[pair['b']]
        ca, cb = Counter(a['projection']), Counter(b['projection'])
        differing = {letter: [ca[letter], cb[letter]] for letter in sorted(ca.keys() | cb.keys()) if ca[letter] != cb[letter]}
        rows.append([edition, pair['a'], pair['b'], len(a['projection']), json.dumps(differing, separators=(',', ':')), pair['decision'], json.dumps(pair['offsets'], separators=(',', ':'))])
with (A / 'EQUAL_LENGTH_COUNTEREXAMPLES.tsv').open('w') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n')
    w.writerow(['edition', 'paragraph_a', 'paragraph_b', 'projected_length', 'different_letter_counts_a_b', 'decision', 'rotation_offsets'])
    w.writerows(rows)

lines = ['# GDT970 — kein vollständiges Absatzpaar für den festen Pes-Code', '',
         'Kein Paar der vollständig literal lesbaren Absätze erfüllt die notwendige Zeichenkonsequenz der beiden Begleitstimmen. Bei allen Paaren widersprechen schon Länge oder Zeichenhäufigkeiten dem registrierten Modell. Die Reihenfolgeprüfung, ein vollständiger Ereigniscode und die musikalische Hauptstimme wurden an keinem überlebenden Kandidaten erreicht. **Keine Übersetzung gewonnen.**', '',
         '| Lesung | Vollständige Absätze | Literal prüfbar | Physische Blätter der prüfbaren Absätze | Alle Paare | Verbleibende Paare |', '|---|---:|---:|---:|---:|---:|']
for ed, s in result['panels'].items():
    lines.append(f"| {ed} | {s['complete_paragraphs']} | {s['literal_paragraphs']} | {s['literal_physical_leaves']} | {s['all_literal_pairs']} | {s['pair_decisions']['NECESSARY_CONSEQUENCE_ONLY']} |")
lines += ['', 'RF1b liefert hier keine Absatzgrenzen; seine Nullzahlen sind fehlende Prüfbarkeit. ZL3b und IT2a sind alternative Lesungen desselben Manuskripts. Die 627 beziehungsweise 161 vollständigen, aber nicht durchgehend literal prüfbaren Absätze bleiben unbekannt; sie wurden weder bereinigt noch negativ gewertet. Weitere sechs ZL- und sieben IT-Blöcke scheiterten bereits an der unveränderten Vollständigkeitsregel.', '',
          '## Konkrete Vorhersage und alle Beobachtungen', '',
          'Die historische Quelle schreibt die vollständigen Pes-Stimmen als AB und BA. Unter einem globalen, aneinandergesetzten Ereigniscode müssen ihre ganzen Zeichenfolgen nach Projektion auf Buchstaben zyklisch übereinstimmen. Unterschiedliche Codelängen und Ereignisgrenzen innerhalb eines Wortes sind erlaubt. Der hypothetische vollständige Code müsste sämtliche inneren Leerzeichen erklären; diese notwendige Teilprüfung erklärt sie noch nicht.', '',
          'Alle vier dokumentarischen Dauerzweige sagen dieselbe notwendige Beziehung voraus. Sie können durch diesen Test nicht voneinander unterschieden werden: Drei ergeben A=B=12 bedingte Breven, der erhaltene Prosa-Gegenfall A=11/B=12. Exakte Dauer, Tonhöhe, musikalische Absicht und Schlüsselwerte sind keine Beobachtungen dieses Absatztests.', '',
          '| Lesung | Unterschiedliche Zeichenlänge | Gleiche Länge, verschiedene Häufigkeiten | Erst bei zyklischer Ordnung widersprochen | Überlebt |', '|---|---:|---:|---:|---:|']
for ed, s in result['panels'].items():
    c = s['pair_decisions']
    lines.append(f"| {ed} | {c['UNEQUAL_LENGTH']} | {c['UNEQUAL_INVENTORY']} | {c['UNEQUAL_CYCLIC_ORDER']} | {c['NECESSARY_CONSEQUENCE_ONLY']} |")
lines += ['', 'Kein literal prüfbarer Absatz lag unter dem registrierten Minimum von neun Buchstaben. Einwortzeilen wurden ausdrücklich zugelassen: Das betrifft einen ZL- und sechs IT-Absätze, die eine ungeprüfte Übernahme von GDT928s Anker-Mindestlänge ausgeschlossen hätte. Auch identische Projektionen und Verschiebung null wären erhalten geblieben; tatsächliche solche Paare gab es nicht.', '',
          '[CANDIDATE_PREDICTIONS.tsv](artifacts/CANDIDATE_PREDICTIONS.tsv) enthält **jeden der 1.349 vollständigen Absätze**, seine feste Vorhersageklasse, Defekte, beobachtete Partner und Entscheidung. [EQUAL_LENGTH_COUNTEREXAMPLES.tsv](artifacts/EQUAL_LENGTH_COUNTEREXAMPLES.tsv) zeigt für **alle 438 gleich langen Paare** die tatsächlich unterschiedlichen Buchstabenhäufigkeiten, jeweils als [Anzahl A, Anzahl B]. Die übrigen Paare sind durch die vollständige [Längenpartition](artifacts/LENGTH_PARTITION.tsv) und sämtliche Paarzählungen exhaustiv abgedeckt. [PARAGRAPHS.json](artifacts/PARAGRAPHS.json) bewahrt die ganzen Gruppen, Zeilen, Grenzen und Quell-IDs. Keine Einzelstelle wurde zur Entscheidung ausgewählt.', '',
          '## Entscheidung und verbleibende Mehrdeutigkeit', '',
          'Der feste Code für vollständige musikalische Teile hat in der literal prüfbaren ZL-/IT-Abdeckung keinen Kandidaten. Damit existiert dort auch kein vollständiger Drei-Absatz-Zeuge für Hauptstimme und beide Pes unter diesem Vertrag. RF und die nicht literal lesbaren Absätze bleiben unentschieden. Kein allgemeiner Ausschluss von Musik, kontextabhängiger Schrift, anders abgegrenzten Teilen oder nichtwörtlicher Inhaltsdarstellung folgt. Solche Änderungen werden nicht als nachträgliche Rettung eingebaut.', '',
          'Ein positives zyklisches Paar allein hätte weiterhin keinen vollständigen, präfixfreien Code, keine Erklärung der Leerzeichen und keinen musikalischen Sinn identifiziert. Die Vorabkontrolle zeigt sogar einen zulässigen vollständigen Code mit verschiedenen Schreibungen, die auf dieselbe Buchstabenfolge projizieren. Ebenso gibt es zyklische Paare, die die wiederholten Quellereignisse nicht codieren können. Hier entstand kein positiver Kandidat, dessen Restmehrdeutigkeit durch eine Schlüsselwahl reduziert worden wäre.', '',
          '## Abgrenzung und Prüfung', '',
          'Die Registrierung wurde als 3cc6748f5 veröffentlicht; der Push war um13:13:52UTC bestätigt. Der unveränderte Lauf begann am2026-09-15 um13:14:10.733154UTC und dauerte rund0,517Sekunden. Er verwendete ausschließlich die sechs gebundenen, bereits bewacht gewonnenen GDT915-Caches und deren179freigegebene Selektoren. Alle waren zuvor im Projekt exponiert, einschließlich der historisch EVALUATION genannten Daten. Keine unabhängige Bestätigungskapazität; keine echte Reserve, f84/f84r oder f116v geöffnet.', '',
          'Die unabhängige Validierung rekonstruiert die vollständige Aufnahme und alle140.152literal möglichen Absatzpaare ohne Import des Hauptprogramms. Direkte Suchen in verdoppelten Zeichenfolgen prüfen seine kanonischen Rotationsklassen. Alle Vorhersagezeilen, Längenklassen, gleich langen Paarbelege und Quellbindungen werden abgeglichen. Die echte Auswertung beansprucht nur die Pfade für Längen- und Häufigkeitswidersprüche; positive und reine Reihenfolgefälle sind ausschließlich durch synthetische Beispiele geprüft. Das endgültige maschinelle Prüfergebnis steht in [VALIDATION.json](artifacts/VALIDATION.json).', '',
          'Keine geeignete Gegenkontrolle der gesamten Suche, daher keine Signifikanz- oder Wahrscheinlichkeitsbehauptung. Keine unabhängige Bedeutungsprüfung, daher keine bestätigten Noten-, Wort- oder Pflanzennamen. Bestehende globale Repository-Schulden bleiben sieben ungebundene GDT600-Dateien und die frühere GDT953-Größenbegründung; der exakte Veröffentlichungsumfang wird gesondert geprüft.', '',
          'Arbeitsbudget einschließlich Vorbereitung, Implementierung, Prüfung und Veröffentlichung:13:03–13:35UTC. Die Abschlussveröffentlichung ist beim Schreiben dieses Berichts noch ausstehend; ihr Git-Zeitstempel dokumentiert den tatsächlichen Abschluss. Keine Verlängerung für einen Decoder oder eine Code-Reparatur.', '']
(E / 'REPORT.md').write_text('\n'.join(lines))
print(json.dumps({'complete_prediction_rows': sum(len(ps) for ps in panels.values()), 'equal_length_counterexample_rows': len(rows), 'all_literal_pairs': sum(s['all_literal_pairs'] for s in result['panels'].values())}))
