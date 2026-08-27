# GDT543 — 81 gelernte Fragmentstämme mit gerichteten Ausbauten

Status: `PASS_81_FRAGMENT_TARGETS_MAPPED__72_ALIGNED_STEMS__13_RECURRENT_CHANNELS`

## Kernbefund

Alle 81 Formen behalten ein vollständiges altes Mehrkomponentenrezept als
benannten Stamm. Unter 104 gleich langen Ankeroptionen wählt die Karte einen
deterministischen Hauptanker. Bei 72/81 Zielen ist sogar eine alte sichtbare
Schreibform dieses Rezeptes exakt und richtungsgleich als Teil der neuen
Oberfläche erhalten. Die 93 linken/rechten Ausbauarme besitzen 87 alte
Grenzpaare; 69/81 Hauptanker werden in alten Satzumgebungen angetroffen, die
den Zielmodus enthalten.

Die sichtbaren Reste ergeben 83 Beobachtungen in 53 Seitenkanälen. Dreizehn
wiederkehrende Kanäle sind in ihrer Rezeptabbildung invariant und erreichen
34 Ziele. Nur der
wiederkehrende rechte Rest `dy` bleibt absichtlich zweideutig: fünfmal `DY`,
einmal `D_ADDR+Y`. Das bestätigt die schon bekannte Regel, `dy` nicht als
automatisches globales Suffix zu lesen.

Acht Zielrezepte stehen als exakte zusammenhängende Teilfolge in 19 längeren
alten Ganzkarten. Bei vier davon kommt zugleich der Ziel-Kontextmodus vor; die
vier anderen bleiben starke Struktur-, aber keine Kontextbrücken.

## Wiederkehrende sichtbare Ausbaukanäle

| Seite und Rest | Belege | Rezeptabbildung | Klasse |
| --- | ---: | --- | --- |
| `LEFT ch` | 2 | `CH:2` | `REPEATED_INVARIANT_VISIBLE_CHANNEL` |
| `LEFT d` | 4 | `D_ADDR:4` | `REPEATED_INVARIANT_VISIBLE_CHANNEL` |
| `LEFT f` | 2 | `LOCAL_CHAR_F:2` | `REPEATED_INVARIANT_VISIBLE_CHANNEL` |
| `LEFT k` | 3 | `K:3` | `REPEATED_INVARIANT_VISIBLE_CHANNEL` |
| `LEFT l` | 3 | `L:3` | `REPEATED_INVARIANT_VISIBLE_CHANNEL` |
| `LEFT p` | 2 | `P:2` | `REPEATED_INVARIANT_VISIBLE_CHANNEL` |
| `LEFT sh` | 3 | `SH:3` | `REPEATED_INVARIANT_VISIBLE_CHANNEL` |
| `LEFT t` | 3 | `T:3` | `REPEATED_INVARIANT_VISIBLE_CHANNEL` |
| `LEFT y` | 3 | `Y:3` | `REPEATED_INVARIANT_VISIBLE_CHANNEL` |
| `RIGHT aiin` | 2 | `AIIN:2` | `REPEATED_INVARIANT_VISIBLE_CHANNEL` |
| `RIGHT chy` | 3 | `CH+Y:3` | `REPEATED_INVARIANT_VISIBLE_CHANNEL` |
| `RIGHT d` | 5 | `D_ADDR:5` | `REPEATED_INVARIANT_VISIBLE_CHANNEL` |
| `RIGHT dy` | 6 | `DY:5|D_ADDR+Y:1` | `REPEATED_AMBIGUOUS_VISIBLE_CHANNEL` |
| `RIGHT y` | 3 | `Y:3` | `REPEATED_INVARIANT_VISIBLE_CHANNEL` |

## Offene sichtbare und atomare Übergänge

Ohne vollständig richtungsgleichen sichtbaren Altstamm: `chckhedy`, `cholpchd`, `dalcheeeky`, `fchdar`, `folchol`, `keody`, `okedam`, `pchof`, `qoteeod`.

Noch nie als direktes Paar in einer alten Ganzkarte sichtbar: `aiicthy:AIIN>CH`, `chady:A_ADDR>DY`, `chap:A_ADDR>P`, `chepakeo:P>A_ADDR`, `ofaram:AR>AM_ADDR`, `rotaiin:R>OT`.
Diese Karten werden nicht verworfen; sie bleiben explizite Einzeldefaults mit
ihrem alten Ganzfragment und ihrer bisherigen Bedeutung.

## Vollständiges 81-Karten-Deck

| Ziel | Rezeptausbau um Altstamm | sichtbarer Ausbau | alter Kontext | stärkste Strukturbrücke | Arbeitsbedeutung |
| --- | --- | --- | --- | --- | --- |
| `aiicthy` | `AIIN [CH+T+Y]` | `aii[cthy]` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_WITH_NEW_INTERFACE` | Den Wert und den Posten nehmen und einstellen. |
| `akar` | `A_ADDR [K+AR]` | `a[kar]` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Hier; geben; vom Ausgang. |
| `alkey` | `AL [K+E+Y]` | `al[key]` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Am Zielort; den Posten geben; auf Grad I. |
| `chady` | `[CH+A_ADDR] DY` | `[cha]dy` | `TARGET_MODE_SET_DISJOINT` | `ALIGNED_VISIBLE_STEM_WITH_NEW_INTERFACE` | Nehmen; hier; abschließen. |
| `chap` | `[CH+A_ADDR] P` | `[cha]p` | `TARGET_MODE_SET_DISJOINT` | `ALIGNED_VISIBLE_STEM_WITH_NEW_INTERFACE` | Nehmen und einsetzen; hier. |
| `chckhedy` | `CH+CH [K+E+DY]` | kein exakter sichtbarer Altstamm | `TARGET_MODE_SET_DISJOINT` | `RECIPE_ANCHOR_ALL_INTERFACES_OLD` | Nehmen, erneut nehmen und geben; auf Grad I; abschließen. |
| `chctho` | `CH [CH+T+O]` | `ch[ctho]` | `TARGET_MODE_SET_EQUAL` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Nehmen, erneut nehmen und einstellen; zur Ausführung. |
| `chefchy` | `[CH+E] LOCAL_CHAR_F+CH+Y` | `[che]fchy` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Den Posten zweimal nehmen; auf Grad I; hier. |
| `chekeody` | `CH+K [E+O] DY` | `chek[eo]dy` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Nehmen und geben; auf Grad I; zur Ausführung; abschließen. |
| `cheod` | `[CH+E+O] D_ADDR` | `[cheo]d` | `TARGET_MODE_SET_INCLUDED` | `EXACT_TARGET_SEQUENCE_INSIDE_OLD_SUPERCARD` | Nehmen; auf Grad I; zur Ausführung; hier. |
| `chepakeo` | `[CH+E+P] A_ADDR+K+E+O` | `[chep]akeo` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_WITH_NEW_INTERFACE` | Nehmen, einsetzen und geben; auf Grad I; hier; erneut auf Grad I; zur Ausführung. |
| `chepos` | `[CH+E+P] O+S` | `[chep]os` | `TARGET_MODE_SET_DISJOINT` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Nehmen, einsetzen und wählen; auf Grad I; zur Ausführung. |
| `cheta` | `[CH+E] T+A_ADDR` | `[che]ta` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Nehmen und einstellen; auf Grad I; hier. |
| `choekeey` | `CH+O+E [K+EE+Y]` | `choe[keey]` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Den Posten nehmen und geben; zur Ausführung; auf Grad I; auf Grad II. |
| `choiin` | `CH [O+IIN]` | `ch[oiin]` | `TARGET_MODE_SET_INCLUDED` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Nehmen; zur Ausführung; auf der bezeichneten Stufe. |
| `cholpchd` | `[OL+P] CHD` | kein exakter sichtbarer Altstamm | `TARGET_MODE_SET_EQUAL` | `EXACT_TARGET_SEQUENCE_INSIDE_OLD_SUPERCARD` | Fortsetzen; einsetzen und bearbeiten. |
| `choraiin` | `[CH+OR] AIIN` | `[chor]aiin` | `TARGET_MODE_SET_EQUAL` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Die Einheit und den Wert nehmen. |
| `chory` | `[CH+OR] Y` | `[chor]y` | `TARGET_MODE_SET_EQUAL` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Die Einheit und den Posten nehmen. |
| `ckhochy` | `[CH+K+O] CH+Y` | `[ckho]chy` | `TARGET_MODE_SET_EQUAL` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Den Posten nehmen, geben und erneut nehmen; zur Ausführung. |
| `cpholdy` | `[CH+P+OL] DY` | `[cphol]dy` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Nehmen und einsetzen; fortsetzen; abschließen. |
| `cthom` | `[CH+T+O] M_LOCAL` | `[ctho]m` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Nehmen und einstellen; zur Ausführung; hier. |
| `dairal` | `[D_ADDR+AIR] AL` | `[dair]al` | `TARGET_MODE_SET_INCLUDED` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Hier; entlang der Bahn; am Zielort. |
| `dalcheeeky` | `AL [CH+K] EEE+Y` | kein exakter sichtbarer Altstamm | `TARGET_MODE_SET_EQUAL` | `RECIPE_ANCHOR_ALL_INTERFACES_OLD` | Am Zielort; den Posten nehmen und geben; auf Grad III. |
| `dalky` | `AL [K+Y]` | `dal[ky]` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Am Zielort; den Posten geben. |
| `dard` | `[D_ADDR+AR] D_ADDR` | `[dar]d` | `TARGET_MODE_SET_INCLUDED` | `EXACT_TARGET_SEQUENCE_INSIDE_OLD_SUPERCARD` | Hier; vom Ausgang; erneut hier. |
| `dcheol` | `D_ADDR [CH+E+O+L]` | `d[cheol]` | `TARGET_MODE_SET_INCLUDED` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Hier; nehmen; auf Grad I; zur Ausführung; über die Verbindung. |
| `dkar` | `D_ADDR [K+AR]` | `d[kar]` | `TARGET_MODE_SET_EQUAL` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Hier; geben; vom Ausgang. |
| `dolarshy` | `[D_ADDR+OL] AR+SH+Y` | `[dol]arshy` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Hier; fortsetzen; vom Ausgang; den Posten halten. |
| `dsholdaiir` | `D_ADDR [SH+OL] DA+IIN+R` | `d[shol]daiir` | `TARGET_MODE_SET_INCLUDED` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Hier; halten und markieren; fortsetzen; auf der zweiten Stufe; auf der bezeichneten Stufe. |
| `dytcheey` | `D_ADDR [Y+T] CH+EE+Y` | `d[yt]cheey` | `TARGET_MODE_SET_EQUAL` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Hier; beide Posten einstellen und nehmen; auf Grad II. |
| `fchdar` | `LOCAL_CHAR_F [CHD+AR]` | kein exakter sichtbarer Altstamm | `TARGET_MODE_SET_INCLUDED` | `RECIPE_ANCHOR_ALL_INTERFACES_OLD` | Hier; bearbeiten; vom Ausgang. |
| `fchedyr` | `LOCAL_CHAR_F [CHD+Y] R` | `f[chedy]r` | `TARGET_MODE_SET_EQUAL` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Hier; den Posten bearbeiten und markieren. |
| `folchol` | `LOCAL_CHAR_F [OL+OL]` | kein exakter sichtbarer Altstamm | `TARGET_MODE_SET_DISJOINT` | `RECIPE_ANCHOR_ALL_INTERFACES_OLD` | Hier; zweimal fortsetzen. |
| `fshodchy` | `LOCAL_CHAR_F [SH+O+D_ADDR] CH+Y` | `f[shod]chy` | `TARGET_MODE_SET_EQUAL` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Hier; den Posten halten und nehmen; zur Ausführung; hier. |
| `kardy` | `[K+AR] DY` | `[kar]dy` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Geben; vom Ausgang; abschließen. |
| `kcheeky` | `K+CH+EE [K+Y]` | `kchee[ky]` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Den Posten geben, nehmen und erneut geben; auf Grad II. |
| `kcheody` | `K [CH+E+O] D_ADDR+Y` | `k[cheo]dy` | `TARGET_MODE_SET_EQUAL` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Den Posten geben und nehmen; auf Grad I; zur Ausführung; hier. |
| `kchody` | `K [CH+O+D_ADDR+Y]` | `k[chody]` | `TARGET_MODE_SET_EQUAL` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Den Posten geben und nehmen; zur Ausführung; hier. |
| `kechody` | `K+E [CH+O+D_ADDR+Y]` | `ke[chody]` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Den Posten geben und nehmen; auf Grad I; zur Ausführung; hier. |
| `keedey` | `K+EE+D_ADDR [E+Y]` | `keed[ey]` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Den Posten geben; auf Grad II; hier; auf Grad I. |
| `keody` | `K+E [O+D_ADDR+Y]` | kein exakter sichtbarer Altstamm | `TARGET_MODE_SET_EQUAL` | `RECIPE_ANCHOR_ALL_INTERFACES_OLD` | Den Posten geben; auf Grad I; zur Ausführung; hier. |
| `kodalchy` | `[K+O+D_ADDR] AL+CH+Y` | `[kod]alchy` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Den Posten geben und nehmen; zur Ausführung; hier; am Zielort. |
| `kody` | `K [O+DY]` | `k[ody]` | `TARGET_MODE_SET_DISJOINT` | `EXACT_TARGET_SEQUENCE_INSIDE_OLD_SUPERCARD` | Geben; zur Ausführung; abschließen. |
| `lkeol` | `L [K+E+OL]` | `l[keol]` | `TARGET_MODE_SET_EQUAL` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Über die Verbindung; geben; auf Grad I; fortsetzen. |
| `lodaiin` | `L [O+D_ADDR+AIIN]` | `l[odaiin]` | `TARGET_MODE_SET_INCLUDED` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Über die Verbindung; zur Ausführung; hier; Wert. |
| `ltsholy` | `L [T+SH+OL] Y` | `l[tshol]y` | `TARGET_MODE_SET_EQUAL` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Über die Verbindung; den Posten einstellen und halten; fortsetzen. |
| `ofaram` | `[O+LOCAL_CHAR_F+AR] AM_ADDR` | `[ofar]am` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_WITH_NEW_INTERFACE` | Zur Ausführung; hier; vom Ausgang; hier. |
| `okedals` | `[OK+AL] S` | `[okedal]s` | `TARGET_MODE_SET_INCLUDED` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Setzen und wählen; am Zielort. |
| `okedam` | `[OK+E+D_ADDR] AM_ADDR` | kein exakter sichtbarer Altstamm | `TARGET_MODE_SET_INCLUDED` | `RECIPE_ANCHOR_ALL_INTERFACES_OLD` | Setzen; auf Grad I; hier; hier. |
| `olsheor` | `OL [SH+E+OR]` | `ol[sheor]` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Fortsetzen; die Einheit halten; auf Grad I. |
| `otalor` | `[OT+AL] OR` | `[otal]or` | `TARGET_MODE_SET_INCLUDED` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Danach; am Zielort; Einheit. |
| `pchof` | `P+CH [O+LOCAL_CHAR_F]` | kein exakter sichtbarer Altstamm | `TARGET_MODE_SET_EQUAL` | `RECIPE_ANCHOR_ALL_INTERFACES_OLD` | Einsetzen und nehmen; zur Ausführung; hier. |
| `pofochey` | `P+O+LOCAL_CHAR_F [O+CH+E+Y]` | `pof[ochey]` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Den Posten einsetzen und nehmen; zur Ausführung; hier; erneut zur Ausführung; auf Grad I. |
| `psheody` | `P [SH+E+O+D_ADDR+Y]` | `p[sheody]` | `TARGET_MODE_SET_EQUAL` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Den Posten einsetzen und halten; auf Grad I; zur Ausführung; hier. |
| `pydaiin` | `P [Y+D_ADDR+AIIN]` | `p[ydaiin]` | `TARGET_MODE_SET_EQUAL` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Den Posten und den Wert einsetzen; hier. |
| `qoekedy` | `CARRIER_Q+O+E [K+E+DY]` | `qoe[kedy]` | `TARGET_MODE_SET_DISJOINT` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Mit Beginnmarker; zur Ausführung; auf Grad I; geben; erneut auf Grad I; abschließen. |
| `qokshd` | `[OK+SH] D_ADDR` | `[qoksh]d` | `TARGET_MODE_SET_DISJOINT` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Setzen und halten; hier. |
| `qopaiin` | `[CARRIER_Q+O+P] AIIN` | `[qop]aiin` | `TARGET_MODE_SET_EQUAL` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Mit Beginnmarker; zur Ausführung; den Wert einsetzen. |
| `qotchoiin` | `OT+CH [O+IIN]` | `qotch[oiin]` | `TARGET_MODE_SET_INCLUDED` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Danach; nehmen; zur Ausführung; auf der bezeichneten Stufe. |
| `qoteeod` | `[OT+EE+O] D_ADDR` | `q[oteeo]d` | `TARGET_MODE_SET_DISJOINT` | `EXACT_TARGET_SEQUENCE_INSIDE_OLD_SUPERCARD` | Danach; auf Grad II; zur Ausführung; hier. |
| `qoteoly` | `[OT+E+OL] Y` | `[qoteol]y` | `TARGET_MODE_SET_INCLUDED` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Danach; auf Grad I; fortsetzen; Posten. |
| `rotaiin` | `R [OT+AIIN]` | `r[otaiin]` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_WITH_NEW_INTERFACE` | Den Wert markieren; danach. |
| `saiis` | `[S+A_ADDR] IIN+S` | `[sa]iis` | `TARGET_MODE_SET_DISJOINT` | `EXACT_TARGET_SEQUENCE_INSIDE_OLD_SUPERCARD` | Zweimal wählen; hier; auf der bezeichneten Stufe. |
| `shckhar` | `SH [CH+K+AR]` | `sh[ckhar]` | `TARGET_MODE_SET_INCLUDED` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Halten, nehmen und geben; vom Ausgang. |
| `shckheody` | `SH+CH+K [E+O] DY` | `shckh[eo]dy` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Halten, nehmen und geben; auf Grad I; zur Ausführung; abschließen. |
| `shekeefy` | `[SH+E+K] EE+LOCAL_CHAR_F+Y` | `[shek]eefy` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Den Posten halten und geben; auf Grad I; auf Grad II; hier. |
| `sheod` | `[SH+E+O] D_ADDR` | `[sheo]d` | `TARGET_MODE_SET_INCLUDED` | `EXACT_TARGET_SEQUENCE_INSIDE_OLD_SUPERCARD` | Halten; auf Grad I; zur Ausführung; hier. |
| `shofol` | `[SH+O] LOCAL_CHAR_F+OL` | `[sho]fol` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Halten; zur Ausführung; hier; fortsetzen. |
| `shokaiir` | `SH [OK+IIN+R]` | `sh[okaiir]` | `TARGET_MODE_SET_DISJOINT` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Halten, setzen und markieren; auf der bezeichneten Stufe. |
| `sholfordaiin` | `[SH+OL] LOCAL_CHAR_F+OR+D_ADDR+AIIN` | `[shol]fordaiin` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Die Einheit und den Wert halten; fortsetzen; hier; hier. |
| `shytchy` | `SH [Y+T] CH+Y` | `sh[yt]chy` | `TARGET_MODE_SET_EQUAL` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Beide Posten halten, einstellen und nehmen. |
| `soaiin` | `S [O+AIIN]` | `s[oaiin]` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Den Wert wählen; zur Ausführung. |
| `tcheo` | `T [CH+E+O]` | `t[cheo]` | `TARGET_MODE_SET_INCLUDED` | `EXACT_TARGET_SEQUENCE_INSIDE_OLD_SUPERCARD` | Einstellen und nehmen; auf Grad I; zur Ausführung. |
| `tosheo` | `T [O+SH+E+O]` | `t[osheo]` | `TARGET_MODE_SET_DISJOINT` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Einstellen und halten; zur Ausführung; auf Grad I; erneut zur Ausführung. |
| `tshokeody` | `T+SH [OK+E+O+D_ADDR+Y]` | `tsh[okeody]` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Den Posten einstellen, halten und setzen; auf Grad I; zur Ausführung; hier. |
| `tydy` | `T [Y+DY]` | `t[ydy]` | `TARGET_MODE_SET_EQUAL` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Den Posten einstellen; abschließen. |
| `yches` | `Y [CH+E+S]` | `y[ches]` | `TARGET_MODE_SET_EQUAL` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Den Posten nehmen und wählen; auf Grad I. |
| `ykeedar` | `Y+K+EE [D_ADDR+AR]` | `ykee[dar]` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Den Posten geben; auf Grad II; hier; vom Ausgang. |
| `ykesho` | `Y+K+E [SH+O]` | `yke[sho]` | `TARGET_MODE_SET_EQUAL` | `ALIGNED_VISIBLE_STEM_ALL_INTERFACES_OLD` | Den Posten geben und halten; auf Grad I; zur Ausführung. |
| `yshedair` | `Y [SH+E+D_ADDR] AIR` | `y[shed]air` | `TARGET_MODE_SET_EQUAL` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Den Posten halten; auf Grad I; hier; entlang der Bahn. |
| `ysheeod` | `Y [SH+EE+O] D_ADDR` | `y[sheeo]d` | `TARGET_MODE_SET_EQUAL` | `REPEATED_INVARIANT_VISIBLE_EXTENSION_CHANNEL` | Den Posten halten; auf Grad II; zur Ausführung; hier. |

Keine Seite, Bedeutung, Zerlegung oder Rezeptkarte wurde verändert. Die
sichtbaren Kanäle sind Arbeitskürzel, keine bestätigten Lexeme.
