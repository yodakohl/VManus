# GDT597 exploratory release protocol

Dieses Dokument beschreibt den ausführbaren Zielvertrag der finalen
Werkstattrunde. Es ist kein Blindtest und friert keine austauschbare deutsche
Bedeutung ein.

## Ziel

Alle laufenden T/CHD/S-Aktionen auf `f75r`, `f77r`, `f81r`, `f81v`, `f82r`
und `f83r` erhalten ein sichtbares Objekt. Geschriebene Packetobjekte bleiben
unverändert; trägerlose Aktionen verwenden getypte Quellen oder eines von
sieben konkreten Aktionsdefaults.

## Zugelassene Entwicklung

- Teilnehmer- und Parameterkanal trennen.
- OT/DY als Cuts und OL als Fortsetzung verwenden.
- Linke kompatible, rechte gleichereignige und lokale/defaultmäßige Bezüge
  getrennt rendern.
- Offensichtlich verbrauchte oder nur aktionsintern erzeugte Kandidaten durch
  sichtbare Scopekarten blockieren.
- Jede schwierige manuelle Entscheidung mit ihrem Rivalen ausgeben.

Nicht zugelassen sind neue Seiten, neue Roots, Neuparsing, Substringsegmente
oder ein stilles Umdeuten geschriebener Träger.

## Vollständigkeitsvertrag

Der Release ist fertig, wenn genau 396 eindeutige Zielhosts in 219 Aussagen
vorliegen, alle 396 Klauseln nichtleer sind, alle 177 trägerlosen Klauseln ihr
gerendertes Nomen sichtbar enthalten, die fünf Typ- und drei Bezugskarten die
Population vollständig partitionieren und Runner plus Validator die
öffentlichen Artefakte bytegenau wiederaufbauen.

Das Ergebnis bleibt eine explorative deutsche Arbeitsedition. Es bestätigt
keinen Voynich-Klartext und jede Defaultbedeutung bleibt durch eine bessere
konkrete Lesung ersetzbar.
