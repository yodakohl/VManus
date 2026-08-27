# GDT555 — elf scheinbar unvollständige Karten sind echte Zustandsstarter

Status: `PASS_64_UNIQUE_GAPS_CLASSIFIED__EXACT_SOURCE_POINTERS_ONLY`

## Ergebnis

Die 16 aktionslosen und 57 argumentlosen Ereignisse aus GDT554 sind keine 73
verschiedenen Probleme: neun gehören zu beiden Mengen. Das vollständige
Arbeitsdeck umfasst daher 64 eindeutige Ereignisse auf 50 Oberflächen.

Elf dieser 64 Ereignisse initialisieren nachweislich einen Zustand:

- acht sichtbare Handlungskarten ohne Argument setzen die aktive Handlung;
- drei sichtbare Argumentkarten ohne Handlung setzen das aktive Argument;
- jede der elf wird unmittelbar von der nächsten Karte ausdrücklich als
  Zustandsquelle genannt;
- insgesamt entstehen 22 exakte Quelllinks: elf zur unmittelbaren Folgekarte
  und elf weitere Fortführungen;
- der längste Zustand bleibt fünf Karten lang aktiv.

Die acht Handlungsstarter kommen auf allen vier Seiten und in beiden Registern
vor. Die drei Argumentstarter liegen im vorhandenen Material auf f66r. Jeder
Link verwendet die bereits eingetragene GDT539-Quell-ID; es wurde keine
Nachbarschaft nur wegen einer plausiblen Lesung als Verbindung gezählt.

## Konkrete Beispiele

Zweimal steht die gleiche exakte Mikrokonstruktion:

```text
s       Wähle.
aiin    Im laufenden Satz wähle den Arbeitswert.
```

Auf f66r initialisiert `qotey` den laufenden Eintrag, den `kol` sofort
übernimmt. `daly` setzt `Y`, das anschließend von `saiir`, `cheol` und `kal`
verwendet wird. Umgekehrt setzt `sair` die Handlung `S`; fünf spätere Karten
reichen bis zur Entfernung fünf auf genau diese Quellkarte zurück.

`tshol` zeigt, warum eine objektlose Karte nicht unvollständig sein muss. Ihre
letzte sichtbare Handlung `SH` wird unmittelbar von `folchol` und danach von
`otor` übernommen. Die Lesung ist als Zustandsfolge vollständig, obwohl die
erste Karte selbst kein Argument nennt.

## Die übrigen Arbeitsrollen

Die 64 eindeutigen Ereignisse teilen sich in neun sichtbare Rollen:

| Rolle | Ereignisse |
|---|---:|
| objektlose Handlung mit Abschluss- oder Satzgrenze | 19 |
| objektlose Handlung vor einer neuen sichtbaren Handlung | 17 |
| Handlungsinitialisierer | 8 |
| Relations-/Adressprolog | 7 |
| geerbte objektlose Handlung durch eine Steuerkarte | 4 |
| Argumentinitialisierer | 3 |
| verbfreier Abschluss | 3 |
| nominaler/steuernder Prolog | 2 |
| Fortsetzungsprolog | 1 |

Nur die Oberfläche `ol=OL` besitzt zwei beobachtete Lückenrollen: einmal steht
sie am Anfang als Fortsetzungsprolog, zweimal trägt sie eine bereits aktive
Handlung. Das ist genau der erwartete Unterschied zwischen leerem und gefülltem
Aktionssteckplatz, keine zweite Bedeutung für `OL`.

Alle 30 Prüfungen bestehen. Sämtliche Rezepte, Makros und deutschen Klauseln
bleiben exakt aus GDT554 erhalten. Die zusammengezogenen Paarlesungen setzen
nur zwei bereits vorhandene Klauseln nebeneinander.

## Nächster Griff

Der größte verbleibende Block besteht aus Abschluss- und Grenzkarten. Als
nächstes sollte `DY=ABSCHLIESSEN` nicht nur innerhalb der 64 Lücken, sondern an
allen bereits vorhandenen Ereignis- und Aussagegrenzen geprüft werden. Das
kann entscheiden, ob `DY` einen ganzen Satz, einen lokalen Schritt oder beide
Ebenen schließt, ohne eine neue Seite zu öffnen.
