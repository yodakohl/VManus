# GDT485 — Methode

## Question

Lassen sich alle 135 festen GDT484-Arbeitslesungen in kurzes, natürliches
Deutsch überführen, ohne technische Lesung, Komponentensequenz, Eventgrenze,
Namen, OT/OL-Reihenfolge oder Herkunftsstufe zu verlieren?

## Inputs

- GDT479: feste 135-Record-/183-Event-Reihenfolge und OT/OL-Spuren;
- GDT482: normalisierte Komponentensequenz jedes Events;
- GDT484: aktuelle technische Lesung und stärkste Herkunftsstufe jedes Records
  und Events;
- `src/fluent_readings.tsv`: explizite, recordweise redigierte Werkstattfassung
  samt benanntem Redaktionsgriff.

## Method

1. Die 135 GDT484-Lesungen werden bytegleich als technischer Kanal übernommen.
2. Jedes der 183 GDT479-Events erhält einen Rückprojektionssatz mit Oberfläche,
   Rezept, aktivem Modell, wörtlicher und normalisierter Komponentenspur,
   Eventlesung, OT/OL-Zustand und GDT484-Herkunft.
3. Die Werkstattfassung wird recordweise redigiert. Zulässig sind nur
   Pronomen/Mehrzahl, natürlichere Wortstellung, verdichtete Listen,
   ausgeschriebene Adresspfade, geglättete Fortsetzung und das Auslagern von
   Reihenfolge-Metakommentaren in ihr eigenes Spurfeld.
4. Alle verschieden geschriebenen Werte in deutschen Anführungszeichen müssen
   in technischer und flüssiger Fassung identisch bleiben. Exakte
   Wiederholungszahlen bleiben entweder sichtbar oder in der technischen und
   wörtlichen Spur erhalten.
5. Neun klar mechanische Marker werden vor/nach der Redaktion gezählt:
   eingebettete Reihenfolge-Sätze, nummerierte Events, Pfeile, invertierte
   Weiter-Imperative, doppeltes Weiter, Arbeitsgang-/Adressspur-Metapräfixe,
   Schrägstrichlabels und das Komma vor einem Schrittabschluss.

„Rückführbar“ bedeutet hier ausdrücklich Zweikanal-Rückführung: Die geglättete
Paraphrase muss nicht durch eine inverse Stilregel rekonstruiert werden, weil
ihre vollständige technische Quelle und ihre Eventzerlegung in derselben Zeile
erhalten bleiben.

## Decision rule and claim ceiling

Die Runde ist vollständig, wenn 135/135 Records eine nichtleere Werkstattfassung
und 183/183 Events eine exakte Rückprojektionszeile besitzen, alle technischen
Lesungen bytegleich sind, die 69 OT/OL-Stellen stimmen, alle verschieden
benannten Werte erhalten bleiben und kein Zielmarker in der Werkstattfassung
zurückbleibt.

Die Ausgabe ist eine redaktionelle Schicht über den festen Arbeitsbedeutungen.
Sie fügt keine Wurzel, Komponentenbedeutung, Namensidentität, Syntax,
Klartextsprache, Modellwahl, Grenze, Oberfläche, Rezept, Event oder Seite hinzu.
