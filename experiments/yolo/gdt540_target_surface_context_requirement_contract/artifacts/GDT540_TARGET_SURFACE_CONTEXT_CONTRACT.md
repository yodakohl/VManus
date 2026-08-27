# GDT540 — Kontextvertrag der 145 neuen Prosaoberflächen

Status: `PASS_149_OCCURRENCES_CLASSIFIED__145_SURFACE_CONTRACTS__ONE_CONTEXT_SWITCH`

## Der kurze Vertrag

1. Eine sichtbare Handlung wird gelesen und wird zum laufenden Satzkopf.
2. Fehlt die Handlung, wird die letzte sichtbare Handlung desselben Satzes eingesetzt; fehlt auch sie, bleibt nur eine nichtverbale Fragmentlesung.
3. Ein sichtbares Argument wird gelesen und wird zum laufenden Satzargument.
4. Fehlt das Argument, wird das laufende Satzargument übernommen, falls eines vorhanden ist; sonst bleibt die Handlung objektlos.
5. An einer Aussagegrenze werden beide Zustände geleert.

Damit erhalten 149/149 Vorkommen und 145/145 Oberflächen eine konkrete Intake-Regel, ohne ein Rezept oder einen Stammwert zu ändern.

## Beobachtete Anforderungsverteilung

| Bekannte Vorkommensklasse | Vorkommen |
| --- | ---: |
| selbständig | 92 |
| braucht aktive Handlung | 5 |
| braucht aktives Argument | 41 |
| braucht beides | 11 |

Auf Oberflächenebene sind 88 nur selbständig, 40 nur mit aktivem Argument, fünf nur mit aktiver Handlung und elf nur mit beiden Zuständen beobachtet. Eine Form schaltet um.

## Die drei Wiederholungen

- `keody` erscheint dreimal und bleibt dreimal selbständig.
- `shain` erscheint zweimal und bleibt zweimal selbständig.
- `qokees` erscheint einmal ohne Satzargument und einmal mit geerbtem `Y`. Rezept und sichtbare Handlungen `OK+EE+S` bleiben identisch. Das ist der direkte Beleg für die Regel „Argument übernehmen, falls vorhanden; sonst objektlos“.

Alle geerbten Handlungen liegen höchstens 3 Karten zurück, alle geerbten Argumente höchstens 3 Karten. Ein Zwei-Slot-Satzspeicher reicht deshalb weiterhin aus; die Distanz ist nur eine Beobachtung dieser vier Seiten, keine harte Zukunftsgrenze.

## Vollständiger Oberflächenvertrag

| Oberfläche | Rezept | beobachtete Modi | Zukunfts-Intake |
| --- | --- | --- | --- |
| `aiicthy` | `AIIN+CH+T+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `akar` | `A_ADDR+K+AR` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `alkey` | `AL+K+E+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `axor` | `A_ADDR+LOCAL_X+OR` | `REQUIRES_ACTIVE_ACTION` | Laufende Satzhandlung einsetzen; sichtbares Argument lesen; ohne laufende Handlung nur als Fragment ausgeben. |
| `chady` | `CH+A_ADDR+DY` | `SELF_CONTAINED` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `chap` | `CH+A_ADDR+P` | `SELF_CONTAINED` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `chckhedy` | `CH+CH+K+E+DY` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `chcpheor` | `CH+CH+P+E+OR` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `chctho` | `CH+CH+T+O` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `cheda` | `CHD+A_ADDR` | `SELF_CONTAINED` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `chedaiir` | `CHD+IIN+R` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `cheeo` | `CH+EE+O` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `chefchy` | `CH+E+LOCAL_CHAR_F+CH+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `chekchy` | `CH+K+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `chekeey` | `CH+K+EE+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `chekeody` | `CH+K+E+O+DY` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `cheod` | `CH+E+O+D_ADDR` | `SELF_CONTAINED` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `chepakeo` | `CH+E+P+A_ADDR+K+E+O` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `chepos` | `CH+E+P+O+S` | `SELF_CONTAINED` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `cheta` | `CH+E+T+A_ADDR` | `SELF_CONTAINED` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `choekeey` | `CH+O+E+K+EE+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `choiin` | `CH+O+IIN` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `cholpchd` | `OL+P+CHD` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `choraiin` | `CH+OR+AIIN` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `choraly` | `CH+OR+AL+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `chory` | `CH+OR+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `chpady` | `CH+P+A_ADDR+DY` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `chxar` | `CH+LOCAL_X+AR` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `ckhochy` | `CH+K+O+CH+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `cphaiin` | `CH+P+AIIN` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `cpholdy` | `CH+P+OL+DY` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `cthdy` | `CH+T+D_ADDR+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `cthom` | `CH+T+O+M_LOCAL` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `da` | `DA` | `REQUIRES_ACTIVE_ACTION_AND_ARGUMENT` | Laufende Satzhandlung einsetzen und ein laufendes Satzargument übernehmen, falls eines vorhanden ist; ohne Handlung nur als Fragment. |
| `dairal` | `D_ADDR+AIR+AL` | `REQUIRES_ACTIVE_ACTION_AND_ARGUMENT` | Laufende Satzhandlung einsetzen und ein laufendes Satzargument übernehmen, falls eines vorhanden ist; ohne Handlung nur als Fragment. |
| `dairody` | `D_ADDR+AIR+O+DY` | `REQUIRES_ACTIVE_ACTION_AND_ARGUMENT` | Laufende Satzhandlung einsetzen und ein laufendes Satzargument übernehmen, falls eines vorhanden ist; ohne Handlung nur als Fragment. |
| `dairykodas` | `D_ADDR+AIR+Y+K+O+DA+S` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `dalalshedy` | `AL+AL+SH+E+DY` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `dalcheeeky` | `AL+CH+K+EEE+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `dalky` | `AL+K+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `dalol` | `AL+OL` | `REQUIRES_ACTIVE_ACTION_AND_ARGUMENT` | Laufende Satzhandlung einsetzen und ein laufendes Satzargument übernehmen, falls eines vorhanden ist; ohne Handlung nur als Fragment. |
| `dard` | `D_ADDR+AR+D_ADDR` | `REQUIRES_ACTIVE_ACTION_AND_ARGUMENT` | Laufende Satzhandlung einsetzen und ein laufendes Satzargument übernehmen, falls eines vorhanden ist; ohne Handlung nur als Fragment. |
| `dcheey` | `D_ADDR+CH+EE+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `dcheol` | `D_ADDR+CH+E+O+L` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `dkar` | `D_ADDR+K+AR` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `doiiin` | `D_ADDR+O+IIN` | `REQUIRES_ACTIVE_ACTION_AND_ARGUMENT` | Laufende Satzhandlung einsetzen und ein laufendes Satzargument übernehmen, falls eines vorhanden ist; ohne Handlung nur als Fragment. |
| `dolarshy` | `D_ADDR+OL+AR+SH+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `dsholdaiir` | `D_ADDR+SH+OL+DA+IIN+R` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `dyky` | `D_ADDR+Y+K+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `dytcheey` | `D_ADDR+Y+T+CH+EE+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `faiis` | `LOCAL_CHAR_F+IIN+S` | `SELF_CONTAINED` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `fchdar` | `LOCAL_CHAR_F+CHD+AR` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `fchedyr` | `LOCAL_CHAR_F+CHD+Y+R` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `folchol` | `LOCAL_CHAR_F+OL+OL` | `REQUIRES_ACTIVE_ACTION` | Laufende Satzhandlung einsetzen und ein laufendes Satzargument übernehmen, falls eines vorhanden ist; ohne Handlung nur als Fragment. |
| `fshodchy` | `LOCAL_CHAR_F+SH+O+D_ADDR+CH+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `kardy` | `K+AR+DY` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `kcheeky` | `K+CH+EE+K+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `kcheody` | `K+CH+E+O+D_ADDR+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `kchody` | `K+CH+O+D_ADDR+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `kechody` | `K+E+CH+O+D_ADDR+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `keedey` | `K+EE+D_ADDR+E+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `keeol` | `K+EE+OL` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `keody` | `K+E+O+D_ADDR+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `kodalchy` | `K+O+D_ADDR+AL+CH+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `kodary` | `K+O+D_ADDR+AR+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `kody` | `K+O+DY` | `SELF_CONTAINED` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `ld` | `L+D_ADDR` | `REQUIRES_ACTIVE_ACTION_AND_ARGUMENT` | Laufende Satzhandlung einsetzen und ein laufendes Satzargument übernehmen, falls eines vorhanden ist; ohne Handlung nur als Fragment. |
| `lkeol` | `L+K+E+OL` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `lodaiin` | `L+O+D_ADDR+AIIN` | `REQUIRES_ACTIVE_ACTION` | Laufende Satzhandlung einsetzen; sichtbares Argument lesen; ohne laufende Handlung nur als Fragment ausgeben. |
| `lpchees` | `L+P+CH+EE+S` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `lsheody` | `L+SH+E+O+D_ADDR+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `ltsholy` | `L+T+SH+OL+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `ofaram` | `O+LOCAL_CHAR_F+AR+AM_ADDR` | `REQUIRES_ACTIVE_ACTION_AND_ARGUMENT` | Laufende Satzhandlung einsetzen und ein laufendes Satzargument übernehmen, falls eines vorhanden ist; ohne Handlung nur als Fragment. |
| `okalchedy` | `OK+AL+CHD+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `okedals` | `OK+AL+S` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `okedam` | `OK+E+D_ADDR+AM_ADDR` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `okoy` | `OK+O+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `olsheor` | `OL+SH+E+OR` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `otalor` | `OT+AL+OR` | `REQUIRES_ACTIVE_ACTION` | Laufende Satzhandlung einsetzen; sichtbares Argument lesen; ohne laufende Handlung nur als Fragment ausgeben. |
| `oteochey` | `OT+E+O+CH+E+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `pchof` | `P+CH+O+LOCAL_CHAR_F` | `SELF_CONTAINED` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `pdaiin` | `P+AIIN` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `pofochey` | `P+O+LOCAL_CHAR_F+O+CH+E+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `psheody` | `P+SH+E+O+D_ADDR+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `pydaiin` | `P+Y+D_ADDR+AIIN` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `qef` | `E+LOCAL_CHAR_F` | `REQUIRES_ACTIVE_ACTION_AND_ARGUMENT` | Laufende Satzhandlung einsetzen und ein laufendes Satzargument übernehmen, falls eines vorhanden ist; ohne Handlung nur als Fragment. |
| `qocthedy` | `CARRIER_Q+O+CH+T+E+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `qoekedy` | `CARRIER_Q+O+E+K+E+DY` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `qokaiir` | `OK+IIN+R` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `qokchey` | `OK+CH+E+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `qokee` | `OK+EE` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `qokeedar` | `OK+EE+D_ADDR+AR` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `qokees` | `OK+EE+S` | `SELF_CONTAINED|REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `qokshd` | `OK+SH+D_ADDR` | `SELF_CONTAINED` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `qopaiin` | `CARRIER_Q+O+P+AIIN` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `qotchoiin` | `OT+CH+O+IIN` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `qotedal` | `OT+E+AL` | `REQUIRES_ACTIVE_ACTION_AND_ARGUMENT` | Laufende Satzhandlung einsetzen und ein laufendes Satzargument übernehmen, falls eines vorhanden ist; ohne Handlung nur als Fragment. |
| `qoteeod` | `OT+EE+O+D_ADDR` | `REQUIRES_ACTIVE_ACTION_AND_ARGUMENT` | Laufende Satzhandlung einsetzen und ein laufendes Satzargument übernehmen, falls eines vorhanden ist; ohne Handlung nur als Fragment. |
| `qoteoly` | `OT+E+OL+Y` | `REQUIRES_ACTIVE_ACTION` | Laufende Satzhandlung einsetzen; sichtbares Argument lesen; ohne laufende Handlung nur als Fragment ausgeben. |
| `rotaiin` | `R+OT+AIIN` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `saiis` | `S+A_ADDR+IIN+S` | `SELF_CONTAINED` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `shain` | `SH+AIN` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `shckhar` | `SH+CH+K+AR` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `shckheody` | `SH+CH+K+E+O+DY` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `shd` | `SH+D_ADDR` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `shddy` | `SH+D_ADDR+DY` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `shedshey` | `SH+E+D_ADDR+SH+E+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `shee` | `SH+EE` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `sheeody` | `SH+EE+O+D_ADDR+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `shekair` | `SH+E+K+AIR` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `shekaly` | `SH+E+K+AL+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `shekeefy` | `SH+E+K+EE+LOCAL_CHAR_F+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `shekeey` | `SH+E+K+EE+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `shekey` | `SH+E+K+E+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `shekol` | `SH+E+K+OL` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `sheocthy` | `SH+E+O+CH+T+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `sheod` | `SH+E+O+D_ADDR` | `SELF_CONTAINED` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `sheodaiin` | `SH+E+O+D_ADDR+AIIN` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `sheoy` | `SH+E+O+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `shofol` | `SH+O+LOCAL_CHAR_F+OL` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `shokaiir` | `SH+OK+IIN+R` | `SELF_CONTAINED` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `sholfordaiin` | `SH+OL+LOCAL_CHAR_F+OR+D_ADDR+AIIN` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `shso` | `SH+S+O` | `SELF_CONTAINED` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `shtchy` | `SH+T+CH+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `shyshol` | `SH+Y+SH+OL` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `shytchy` | `SH+Y+T+CH+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `soaiin` | `S+O+AIIN` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `tcheo` | `T+CH+E+O` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `tocpheey` | `T+O+CH+P+EE+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `todeeey` | `T+O+D_ADDR+EEE+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `tolchedy` | `T+OL+CHD+DY` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `tolshy` | `T+OL+SH+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `tosheo` | `T+O+SH+E+O` | `REQUIRES_ACTIVE_ARGUMENT` | Sichtbare Handlung lesen; laufendes Satzargument übernehmen, falls eines vorhanden ist, sonst objektlos lesen. |
| `tshokeody` | `T+SH+OK+E+O+D_ADDR+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `tydy` | `T+Y+DY` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `yches` | `Y+CH+E+S` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `ykeedar` | `Y+K+EE+D_ADDR+AR` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `ykesho` | `Y+K+E+SH+O` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `ykoiin` | `Y+K+O+IIN` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `ykshedy` | `Y+K+SH+E+DY` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `ypches` | `Y+P+CH+E+S` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `yshedair` | `Y+SH+E+D_ADDR+AIR` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `ysheeod` | `Y+SH+EE+O+D_ADDR` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `ytarody` | `Y+T+AR+O+DY` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |
| `ytoy` | `Y+T+O+Y` | `SELF_CONTAINED` | Sichtbare Handlung und sichtbares Argument lesen. |

## Grenze der Lesung

Die vier Klassen beschreiben, welche Zustände die bekannte kontextuelle Werkstattlesung tatsächlich benutzt. Bei einmal belegten Oberflächen ist das noch keine ewige Worteigenschaft. Der Zukunftsvertrag wird deshalb aus den sichtbaren Handlungs- und Argumentslots abgeleitet; `qokees` zeigt ausdrücklich, dass derselbe Oberflächenkörper je nach Satzvorgeschichte mit oder ohne Objekt funktionieren kann.

Keine neue Seite, kein neues Rezept und keine neue Stammbedeutung wurde eingeführt.
