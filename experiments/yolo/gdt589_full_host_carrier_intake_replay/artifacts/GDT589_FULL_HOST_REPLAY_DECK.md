# GDT589 — vollständiger Host-Replay und schriftpositionssichere Leserschicht

Explorative Arbeitslesung; kein rekonstruierter Klartext.

## Vollreplay

- 953 komplette bekannte Handlungshosts / 1243 Trägerslots.
- 910 automatische Hosts / 1186 Slots reproduzieren Regel, Nomen, Formen, Packet und Reihenfolge exakt.
- 41 bekannte manuelle Hosts bleiben als eigener sichtbarer Weg erhalten.
- 2 alte ID-Regeln fallen sichtbar und ohne Lesedrift auf den portablen Elternweg zurück.

## Manuelle Fälle mit sichtbarer Trägeränderung im nackten Zukunftspfad

| Host | manuelle Regel | Elternregel | alte Träger | Zukunftsträger | Packetwechsel |
|---|---|---|---|---|---|
| `ACTION:G407-E0582@1:SH` | `SH_HP_SETTLE_BEFORE_STRAIN` | `SH_REST_HOLD` | Pflanzenansatz | Pflanzeneinheit | NO |
| `ACTION:G407-E3903@1:S` | `S_HP_STRAIN_AFTER_WET_STEP` | `S_HP_SIEVE` | Arzneiansatz | Arzneiansatz | YES |
| `ACTION:G407-E4069@4:S` | `S_HP_STRAIN_AFTER_WET_STEP` | `S_HP_SIEVE` | Zutatenportion | Zutatenportion | YES |
| `ACTION:G407-E4089@2:SH` | `SH_HP_SETTLE_BEFORE_STRAIN` | `SH_REST_HOLD` | Drogenmaterial|Arzneiansatz | Drogenmaterial|Materialeinheit | NO |
| `ACTION:G407-E4166@3:CHD` | `CHD_HP_WET_EXTRACT_PROCESS` | `CHD_REST_PROCESS` | Drogenmaterial|Drogenmaterial|Arzneiauszug|Drogenmaterial|Drogenmaterial | Drogenmaterial|Drogenmaterial|Dosis- oder Mengenmaß|Drogenmaterial|Drogenmaterial | NO |
| `ACTION:G407-E4226@1:S` | `S_HP_SIEVE_DIRECT_PORTION` | `S_HP_STRAIN` | Zutatenportion|Arzneiauszug | Zutatenportion|Arzneiauszug | YES |
| `ACTION:G407-E4407@2:S` | `S_HP_STRAIN_AFTER_WET_STEP` | `S_HP_SIEVE` | Pflanzenportion | Pflanzenportion | YES |
| `ACTION:G407-E4410@2:CHD` | `CHD_HP_MATERIAL_COMMINUTE` | `CHD_HP_DRY_GRIND` | Pflanzenmaterial|Pflanzenansatz | Pflanzenmaterial|Pflanzen- oder Arbeitseinheit | NO |

Direkter Elternregel-Sinn und konservativer Runtime-Fallback sind getrennt: Zwei der vier Nomenabweichungen entstehen erst durch einen breiten, bisher unbelegten Eltern-Zellfallback. Alle 53 historischen manuellen Slots bleiben im expliziten alten Regelweg exakt.

## Alte ID-Brücken

- `ACTION:G407-E0298@4:SH`: `SH_CH_BRIDGE_HOLD` → `SH_REST_HOLD`; OR+Y+OR → Pflanzeneinheit|Pflanzenmaterial|Pflanzeneinheit; sichtbarer Fallthrough exakt.
- `ACTION:G407-E0494@4:SH`: `SH_CH_BRIDGE_HOLD` → `SH_REST_HOLD`; Y → Pflanzenmaterial; sichtbarer Fallthrough exakt.

## Geschriebene Wiederholungen: zwei Kanäle statt Objektzählung

Es gibt 117 Repeat-Hosts mit 295 Trägerslots und 132 zusätzlichen Schriftpositionen. GDT588 hatte nur die 13 Wiederholungen in Sonderpackets sichtbar gemacht; 104 gewöhnliche Kompositionen blieben im flüssigen Satz dedupliziert.

GDT589 hält deshalb die flüssige Bedeutungshypothese und die geordnete Schreibspur getrennt. `Y–T–Y` kann Rahmung oder Koreferenz sein; `×2` beweist nicht zwei reale Gegenstände.

- `ACTION:G407-E0046@6:SH`: `Y+Y` → Y=Arbeitsmaterial | Y=Arbeitsmaterial
- `ACTION:G407-E0055@2:SH`: `Y+Y` → Y=Arbeitsmaterial | Y=Arbeitsmaterial
- `ACTION:G407-E0059@4:T`: `Y+Y+AIN` → Y=Arbeitsgut | Y=Arbeitsgut | AIN=Teilmenge
- `ACTION:G407-E0094@1:SH`: `AIN+AIN+AIIN` → AIN=Teilmenge | AIN=Teilmenge | AIIN=Arbeitsflüssigkeit
- `ACTION:G407-E0134@2:T`: `Y+Y` → Y=Arbeitsgut | Y=Arbeitsgut
- `ACTION:G407-E0190@2:SH`: `Y+Y` → Y=Arbeitsmaterial | Y=Arbeitsmaterial
- `ACTION:G407-E0237@4:T`: `Y+Y+OR` → Y=Pflanzenmaterial | Y=Pflanzenmaterial | OR=Pflanzenansatz
- `ACTION:G407-E0241@2:T`: `Y+Y+Y+Y` → Y=Pflanzenmaterial | Y=Pflanzenmaterial | Y=Pflanzenmaterial | Y=Pflanzenmaterial

## Packetanzeige: drei Ebenen bleiben getrennt

Die geordneten Slotnomen, ein kompositionell eingeführter Packetkopf und der fertige Satz sind nicht dasselbe. Der Vollreplay markiert deshalb:

- 2 Source-Part-Hosts: Slotlemma `Arbeitsgut`, Packetlesung `Arbeitsmaterial`;
- 3 Seih-Hosts ohne geschriebenes AIIN: `Auszug` kommt aus dem Handlungspacket;
- 1 Celestial-Host: der geschriebene `Sektoranteil` fehlt in der Kurzkarte, bleibt aber in Spur und Satz;
- 4 saubere Bad-Hosts: `Körper` wird als neue explorative Erstlesung geführt, `Stationsansatz` bleibt sichtbare Alternative.

## Vier saubere Bad-Gabeln

- `ACTION:G407-E2404@1:SH` (f77r): bisher Stationsansatz; Arbeitsgabel `Körper im Bad` / `Stationsansatz im Bad`, Körper zuerst.
- `ACTION:G407-E2637@1:SH` (f77r): bisher Stationsansatz; Arbeitsgabel `Körper im Bad` / `Stationsansatz im Bad`, Körper zuerst.
- `ACTION:G407-E2652@1:SH` (f77r): bisher Stationsansatz; Arbeitsgabel `Körper im Bad` / `Stationsansatz im Bad`, Körper zuerst.
- `ACTION:G407-E3182@1:SH` (f82r): bisher Stationsansatz; Arbeitsgabel `Körper im Bad` / `Stationsansatz im Bad`, Körper zuerst.

## Übergaberegel

Auf einem neuen bereits segmentierten Host läuft zuerst das Gate: automatisch, explizit manuell oder alte ID verwerfen. Danach bleiben geordnete Slots primär; Multiset und flüssiger Satz sind getrennte Anzeigen. Breite Fallbacks zeigen zusätzlich alle beobachteten Register×Root-Alternativen.
