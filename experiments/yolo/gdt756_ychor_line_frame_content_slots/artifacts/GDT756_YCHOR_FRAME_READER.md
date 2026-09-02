# GDT756 ychor line-frame reader

## Working result

The best current whole-form reading is **`ychor = ferner / ebenso`**, comparable to the medieval recipe marker `Item`. The prior `nimm` reading remains the main rival, and `ferner: nimm` remains a third live possibility. This is a candidate ranking, not a deciphered Latin spelling.

All 13 exact occurrences start a line and none starts a coded paragraph. The bodies contain content+amount+process together in 4/13 lines, against 22/247 locally matched continuation controls. Among 113 initial forms with at least five initial lines, ychor ranks 4 by this body-triad rate.

## Formula candidates

| rank | complete-form candidate | working German | score | decisive fit |
|---:|---|---|---:|---|
| 1 | `Item` | ferner / ebenso | 96 | Best fit to an invariant line starter that never begins a coded paragraph and precedes recipe-like bodies across several sections. |
| 2 | `Recipe / Accipe` | nimm | 80 | Strong GDT755 candidate because every occurrence is initial and several bodies contain content amount and process. |
| 3 | `Item take / Item accipe` | ferner: nimm | 76 | Historically exact two-part formula that reconciles the additive placement with a following recipe command. |
| 4 | `De / Ad / For` | für / gegen | 52 | A short topical heading is plausible in herbal and medical sections. |

## Frame comparison

| body feature | ychor lines | matched continuation controls | rate ratio |
|---|---:|---:|---:|
| CONTENT_PRESENT | 9/13 | 148/247 | 1.155405 |
| AMOUNT_OR_LEVEL_PRESENT | 6/13 | 91/247 | 1.252747 |
| PROCESS_PRESENT | 4/13 | 40/247 | 1.900000 |
| QUALITY_OR_STAGE_PRESENT | 6/13 | 151/247 | 0.754967 |
| CONTENT_AMOUNT_PROCESS_TRIAD | 4/13 | 22/247 | 3.454545 |

The controls match section, Currier language, hand, continuation status, local corpus neighbourhood and line length within one token. Their repeated use is intentional matched weighting; 247 control rows represent 236 distinct lines.

## Direct followers after ychor

| whole | occurrences | candidate | rivals | confidence |
|---|---:|---|---|---|
| `chor` | 2 | Blätter | Wurzel / Samen | `C0_FORCED_CONTEXT` |
| `cthy` | 2 | Wurzel | Blätter / Kraut | `C0_FORCED_CONTEXT` |
| `ar` | 1 | erster Teil | erste Dosis / Pflanzenteil | `C1_FRAME_CONSTRAINED` |
| `chol` | 1 | trockenes Kraut | Pulver / getrocknete Wurzel | `C1_FRAME_CONSTRAINED` |
| `chshoty` | 1 | weiche ein | trockne / kühle ab | `C0_FORCED_CONTEXT` |
| `odol` | 1 | miss den Arzneistoff ab | eine Dosis Arzneistoff / mische den Arzneistoff | `C1_FRAME_CONSTRAINED` |
| `oky` | 1 | heiß am Anfang | erwärme zuerst / heiße Zubereitung | `C1_FRAME_CONSTRAINED` |
| `ols` | 1 | Heilmittel | Arzneistoff / Öl | `C0_FORCED_CONTEXT` |
| `qokchol` | 1 | heiß getrocknetes Kraut | Pulver / getrocknete Wurzel | `C1_FRAME_CONSTRAINED` |
| `s` | 1 | Samen | Salz / Blätter | `C0_FORCED_CONTEXT` |
| `sheol` | 1 | eingeweichtes Kraut | Wasser / Wein | `C0_FORCED_CONTEXT` |

## All thirteen fully candidate-filled lines

Every written token has a default here. Semicolons deliberately expose a compact register/list reading rather than pretending that German prose order is known.

### f6v.8

EVA: `ychor chor okchey qokom`

Primary (`Item`): ferner: Blätter; heiße trockene Zubereitung; erhitze eine Handvoll

Command rival (`Recipe`): nimm: Blätter; heiße trockene Zubereitung; erhitze eine Handvoll

### f9v.11

EVA: `ychor chshoty oky kaiin`

Primary (`Item`): ferner: weiche ein; heiß am Anfang; heiß im dritten Grad

Command rival (`Recipe`): nimm: weiche ein; heiß am Anfang; heiß im dritten Grad

### f17v.15

EVA: `ychor cthy cheeky cheo otor oteol`

Primary (`Item`): ferner: Wurzel; trockne vollständig, dann erwärme; trockene Zubereitung; eine kalte Portion; kühle bis zur Mittelstufe

Command rival (`Recipe`): nimm: Wurzel; trockne vollständig, dann erwärme; trockene Zubereitung; eine kalte Portion; kühle bis zur Mittelstufe

### f19v.9

EVA: `ychor oky chor ytol chol oky ddor`

Primary (`Item`): ferner: heiß am Anfang; Blätter; kühle den Arzneistoff ab; trockenes Kraut; heiß am Anfang; miss eine Portion ab

Command rival (`Recipe`): nimm: heiß am Anfang; Blätter; kühle den Arzneistoff ab; trockenes Kraut; heiß am Anfang; miss eine Portion ab

### f22v.7

EVA: `ychor chor qokchol chory`

Primary (`Item`): ferner: Blätter; heiß getrocknetes Kraut; frische Blätter

Command rival (`Recipe`): nimm: Blätter; heiß getrocknetes Kraut; frische Blätter

### f23r.5

EVA: `ychor qokchol ytym chol dair chol ar ol ol dol dain`

Primary (`Item`): ferner: heiß getrocknetes Kraut; eine Handvoll gekühltes Kraut; trockenes Kraut; zweiter Teil; trockenes Kraut; erster Teil; Arzneistoff; Arzneistoff; eine Dosis; zweiter Grad

Command rival (`Recipe`): nimm: heiß getrocknetes Kraut; eine Handvoll gekühltes Kraut; trockenes Kraut; zweiter Teil; trockenes Kraut; erster Teil; Arzneistoff; Arzneistoff; eine Dosis; zweiter Grad

### f24r.8

EVA: `ychor s om qoear daiin qokeol`

Primary (`Item`): ferner: Samen; eine Handvoll; nimm den ersten Teil; dritter Grad; heiß im zweiten Grad

Command rival (`Recipe`): nimm: Samen; eine Handvoll; nimm den ersten Teil; dritter Grad; heiß im zweiten Grad

### f45v.9

EVA: `ychor cthy chol qokom sy sa ykchom`

Primary (`Item`): ferner: Wurzel; trockenes Kraut; erhitze eine Handvoll; Samen; gib Samen zu; erhitze und trockne eine Handvoll

Command rival (`Recipe`): nimm: Wurzel; trockenes Kraut; erhitze eine Handvoll; Samen; gib Samen zu; erhitze und trockne eine Handvoll

### f86v5.20

EVA: `ychor ar aiin ytaly otaiin ykaiin otal ytar aiin ytaiiil`

Primary (`Item`): ferner: erster Teil; drei Einheiten; kalte Zubereitung; kalt im dritten Grad; erhitze auf den dritten Grad; kalter Rohstoff, erster Grad; nimm den ersten gekühlten Teil; drei Einheiten; drei Einheiten

Command rival (`Recipe`): nimm: erster Teil; drei Einheiten; kalte Zubereitung; kalt im dritten Grad; erhitze auf den dritten Grad; kalter Rohstoff, erster Grad; nimm den ersten gekühlten Teil; drei Einheiten; drei Einheiten

### f93r.28

EVA: `ychor odol chodaiin s`

Primary (`Item`): ferner: miss den Arzneistoff ab; drei Dosen Trockenansatz; Samen

Command rival (`Recipe`): nimm: miss den Arzneistoff ab; drei Dosen Trockenansatz; Samen

### f99r.52

EVA: `ychor ols or agairom`

Primary (`Item`): ferner: Heilmittel; eine Portion; eine Handvoll, dritter Anteil

Command rival (`Recipe`): nimm: Heilmittel; eine Portion; eine Handvoll, dritter Anteil

### f102v2.35

EVA: `ychor sheol por sheeor shekeey qoky cheo teody qokeol daiin`

Primary (`Item`): ferner: eingeweichtes Kraut; eine Portion Pulver; Wein; weiche ein; heiß am Anfang; trockene Zubereitung; kühle ab und beende; heiß im zweiten Grad; dritter Grad

Command rival (`Recipe`): nimm: eingeweichtes Kraut; eine Portion Pulver; Wein; weiche ein; heiß am Anfang; trockene Zubereitung; kühle ab und beende; heiß im zweiten Grad; dritter Grad

### f106r.9

EVA: `ychor chol qokain chocphol lchedy qocheo qokar`

Primary (`Item`): ferner: trockenes Kraut; heiß im zweiten Grad; getrocknete Wurzel; getrocknetes Holz; mische die trockene Zubereitung; erster heißer Teil

Command rival (`Recipe`): nimm: trockenes Kraut; heiß im zweiten Grad; getrocknete Wurzel; getrocknetes Holz; mische die trockene Zubereitung; erster heißer Teil

## Interpretation boundary

The body deck covers all 71 post-ychor token positions with 53 complete-form defaults. Six weak or formerly unread forms receive explicit C0 context candidates instead of question marks. Concrete words such as Blätter, Wurzel, Samen, Wein, Holz and Pulver are hypotheses chosen for a slot and accompanied by rivals; they are not inferred from EVA initials or substrings.

The practical gain is a testable recipe/list frame: continuation marker, content or operation, then optional quality, quantity and process material. The result identifies no plaintext sentence, language, sound or confirmed lexeme.
