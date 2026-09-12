# P28 Q2 — ausdrücklich nach Exposition ergänzte Bereichsprobe

N0/N1/N2/C1 sind ausgewertet. Der deklarierte Recordanfang liefert nur otedy
auf f77r.25 und keinen weiteren Beschriftungsverweis in seinem Record. Auf
f82r.12 stehen dagegen otedy und okal in derselben physischen Zeile. Beide
Vorkommen und ihre Labelquellen sind seit GDT790 bekannt. Kein Blindtest.

Vor Ausführung dieser Zusatzregel festgelegt: Nicht nur ein Recordanfang,
sondern JEDER physische Zeilenanfang, dessen erstes ganzes Wort eine eindeutige
ganze Beschriftung im Zweiblattregister ist, aktiviert deren Panel bis zum
Recordende oder einem späteren solchen Zeilenanfang. Recordeintritt setzt
zunächst den seitenweiten Bereich zurück. Der Einleiter selbst benennt sein
Label; alle folgenden Namen müssen im aktivierten Bereich liegen. Keine
Umschaltung an einem zeileninternen Namen, keine Ausnahmen nur für okal.

Das ist eine bewusst großzügige Version der Namens-als-Bereichseinleiter-Idee,
keine Behauptung, Zeilen seien Sätze. Sie ändert keine Quelle oder Wortbedeutung.
Alle72Zeilen werden geprüft. Fragestellung: Behebt diese globale Revision den
fehlenden Bereichseinleiter auf f82r, ohne einen Folgebezug zu verlieren?
Ein Verlust bleibt ein Widerspruch dieser strikten Bereichsregel; weder eine
freie Ausnahme noch ein zusätzliches ungeschriebenes Rückschaltwort wird ergänzt.
