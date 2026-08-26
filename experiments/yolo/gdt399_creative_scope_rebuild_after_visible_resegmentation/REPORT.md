# GDT399 — Sichtbar korrigierter Scope-Neubau

Status: kreative Arbeitsrekonstruktion, keine bestätigte Übersetzung.

## Ergebnis

Die Pass-1026-Kartenfolge lässt sich vollständig neu kompilieren: **3.888
Ereignisse, 627 Aussagen und 4,374 Fokusanschlüsse**. Gegenüber
dem überholten Pass-1025-Inventar entstehen netto **+32**
Anschlüsse, weil die 203 sichtbar neu zerlegten Oberflächen zuvor verborgene
WERT-/ANTEIL-/POSTEN-/GRAD-/RELATIONSzeichen wieder zeigen.

Kein Anschluss bleibt offen. Kein Fokus springt über eine Besitzergrenze; der
weiteste Vorgriff bleibt genau eine Karte. Die neun bekannten groben
Scope-Familien reichen weiterhin aus. 0
Familien sind auf nur einer Seite und 0
auf nur einem Register beschränkt.

## Was sich wirklich geändert hat

- 239 Kartenereignisse in 96 Aussagen tragen ein neues sichtbares Rezept.
- Die komplette Fokuszahl steigt von 4.342 auf 4,374.
- Alle 96 betroffenen Aussagen erhalten wieder eine vollständige Lesung aus
  denselben 19 Kernwerten; kein neuer deutscher Kern wurde ergänzt.
- Jede Oberfläche hat weiterhin genau ein Rezept.
- Die vier Register werden erneut vollständig zurückgespielt: `{'PASS_FIXED_SCOPE': 4}`.

## Werkstattregel

Ein sichtbarer Zeichenwechsel wird zuerst neu zerlegt. Nur benannte Q-,
CHD/CHED-, CHK/CHEK-, OS/OES-, D- oder offene-Y-Verpackungen dürfen dasselbe
Rezept behalten. Danach gelten unverändert: nächster Kopf mit Linksgleichstand,
AL/AR links→aktiv→gleiche Karte rechts→Besitzer, L/AIR rechts→links, höchstens
eine Karte begrenzter Vorgriff, R positional und echter Besitzer-/Aussageschluss
als Reset.

## Bedeutung für die nächsten Seiten

Das war kein kosmetischer Patch: Die Satzmaschine wurde aus den korrigierten
Karten neu erzeugt. Sie überlebt, ohne die 239 Änderungen zurückzudrehen. Der
nächste sinnvolle Schritt ist ein gezielter Holdout dieser neuen
4,374-Anschlussbasis und erst danach die nächste Vierseitenfreigabe.

## Artefakte

- `artifacts/gdt399_4374_scope_attachments.tsv`
- `artifacts/gdt399_627_statement_scope_edition.tsv`
- `artifacts/gdt399_3888_event_replay.tsv`
- `artifacts/gdt399_22_page_replay.tsv`
- `artifacts/gdt399_four_register_replay.tsv`
- `artifacts/gdt399_rule_support.tsv`
- `artifacts/gdt399_96_statement_change_audit.tsv`
- `artifacts/gdt399_result.json`
