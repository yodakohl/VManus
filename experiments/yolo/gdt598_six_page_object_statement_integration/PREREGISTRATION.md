# GDT598 exploratory release protocol

Dieses Protokoll beschreibt den ausführbaren Integrationsvertrag; es ist kein
Blindtest und friert keine deutsche Defaultbedeutung ein.

## Ziel

Die vollständigen GDT596- und GDT597-Objektklauseln werden nach ihrem exakten
Action-Slot in die GDT584-Hostfolge auf `f75r`, `f77r`, `f81r`, `f81v`, `f82r`
und `f83r` eingesetzt. Kein anderer Host darf geändert werden. Anschließend
wird jede noch nicht objektfertige Aktion als eigene nächste Arbeitszeile
ausgegeben.

## Vollständigkeitsvertrag

- genau 254 GDT596- und 396 GDT597-Aktionen, null Überlappungen;
- genau 2.272 Hosts in 313 Aussagen;
- identische Hostreihenfolge und Absatzgrenzen;
- alle nicht ersetzten Hosts bytegleich zu GDT584;
- vollständige Partition aller Aktionshosts in objektfertig oder Rest;
- guarded Auswahl ausschließlich der sechs Seiten und kein f84-Material.

Das Resultat ist eine kombinierte Arbeitsedition. Es öffnet keine Seite,
Wurzel, Segmentierung oder neue Bedeutung.
