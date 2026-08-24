# Pass 701 — Kontrastbaum und frischer Werkstatt-Encoder

Diese schnelle Werkstattrunde fragt erstmals vorwärts: Kann ein Lehrling aus
einer neuen kurzen deutschen Arbeitsanweisung eine bereits vorhandene Karte
finden, ohne eine neue Voynich-Form zu erfinden?

## Ergebnis

Die 36 komponierbaren Tascheneinträge lassen sich genau einmal auf 18
Lehrkontraste verteilen. Das sind keine behaupteten sprachlichen Antonyme,
sondern praktische Entscheidungen: Quelle oder Ziel, Portion oder Maß, kurz
oder lang, halten oder absetzen, aktueller Posten oder Schluss.

Von 24 frisch formulierten Arbeitsanweisungen treffen 16 eine bereits
vorhandene Komponentenfolge. Beispiele:

- `OK+AIN`: eine Portion ansetzen;
- `OK+AIR`: den Lauf in Gang setzen;
- `CHK+E+Y`: diesen Posten kurz wärmen;
- `L+CHD+DY`: weiterleiten, umsetzen, Schritt schließen.

Acht ebenso einfache Wünsche fehlen im Kartenbuch, obwohl jeder nur einen
Baustein von einer vorhandenen Familie entfernt liegt. Dazu gehören „diesen
Posten waschen“, „eine Portion teilen“ und „den Ansatz kurz halten“. Der
Encoder bildet dafür ausdrücklich **keine** neue Oberfläche. Er zeigt die
nächsten belegten Familien und verlangt eine Meisterentscheidung.

## Neue Arbeitstheorie

Die Komponenten sind semantisch produktiv: Ein Schreiber kann eine Handlung
als kurze Folge diktieren und eine passende Familie suchen. Das exakte
Karteninventar ist aber lizenziert und begrenzt. Nicht jede denkbare
Kombination besitzt automatisch ein eigenes geschriebenes Wort. Das passt
besser zu einem Fachkürzel- und Nomenklatorsystem als zu frei flektierender
Prosa.

Die nächste Runde untersucht deshalb alle 170 komponierten Karten als
Kompatibilitätsnetz. Gesucht werden kleine Regeln wie „Grad folgt nur einer
Prozessbasis“ oder „Schluss steht nur nach bestimmten Arbeitsketten“, damit die
acht Leerstellen als echte verbotene oder bloß unbelegte Kombinationen
unterschieden werden können.

Dies bleibt die kreative Zehnseiten-Werkstattlesung; es ist keine historische
Entzifferungsbehauptung. Keine neue Seite und keine neue Voynich-Oberfläche
wurde ergänzt.
