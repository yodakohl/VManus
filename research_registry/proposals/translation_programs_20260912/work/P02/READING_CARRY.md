# P02 — vollständige Verlaufsfassung CARRY

Alle deutschen Wörter, Teilnehmer und Zustandsachsen sind Hypothesen. ⟦…⟧ bleibt offen. Die Ereignisordnung ist keine gelesene Zeitdauer. Konflikte werden nicht durch ungeschriebene Änderungen repariert.

## f29v

**f29v.1** `kooiin shor chetchy ol ls shytchy cthy shy cho shy daiin`

⟦kooiin⟧ · ⟦shor⟧ · ⟦chetchy⟧ · ⟦ol⟧ · ⟦ls⟧ · benetze(Zielnennung=f29v.1:7;Vollzug erst dort) · Kraut[B1;neue Instanz;moisture=WET;temperature=UNKNOWN;texture=UNKNOWN] · B1:moisture=WET[CONSISTENT;vorher=WET;Quelle=f29v.1:6] · ⟦cho⟧ · B1:moisture=WET[CONSISTENT;vorher=WET;Quelle=f29v.1:6] · ⟦daiin⟧

**f29v.2** `qotcheaiin s chol chol cthy chey cthold ytchor dary`

⟦qotcheaiin⟧ · ⟦s⟧ · B1:moisture=DRY[CONFLICT;vorher=WET;Quelle=f29v.1:6] · B1:moisture=DRY[CONFLICT;vorher=WET;Quelle=f29v.1:6] · Kraut[B1;wiederaufgenommen;moisture=WET;temperature=UNKNOWN;texture=UNKNOWN] · ⟦chey⟧ · ⟦cthold⟧ · ⟦ytchor⟧ · ⟦dary⟧

**f29v.3** `chol chol kor shey odaiin qotchy taiin s she otey sy`

B1:moisture=DRY[CONFLICT;vorher=WET;Quelle=f29v.1:6] · B1:moisture=DRY[CONFLICT;vorher=WET;Quelle=f29v.1:6] · ⟦kor⟧ · ⟦shey⟧ · ⟦odaiin⟧ · zerkleinere(B1;Quelle=f29v.2:5) · ⟦taiin⟧ · ⟦s⟧ · ⟦she⟧ · ⟦otey⟧ · ⟦sy⟧

**f29v.4** `ysho otshy okaiin cthy oltchy s shot sho okaiin`

⟦ysho⟧ · kühle(Zielnennung=f29v.4:3;Vollzug erst dort) · Ansatz[A1;neue Instanz;moisture=UNKNOWN;temperature=COLD;texture=UNKNOWN] · Kraut[B1;wiederaufgenommen;moisture=WET;temperature=UNKNOWN;texture=GROUND] · B1:temperature=COLD[INITIAL_CONSTRAINT;vorher=UNKNOWN;Quelle=NA],moisture=DRY[CONFLICT;vorher=WET;Quelle=f29v.1:6] · ⟦s⟧ · erwärme(B1;Quelle=f29v.4:4) · ⟦sho⟧ · Ansatz[A1;wiederaufgenommen;moisture=UNKNOWN;temperature=COLD;texture=UNKNOWN]

### Ereignisse und Zustandserhaltung

- f29v.1:6, Vollzug f29v.1:7: benetze B1. moisture=UNKNOWN;temperature=UNKNOWN;texture=UNKNOWN → moisture=WET;temperature=UNKNOWN;texture=UNKNOWN; BOUND_TARGET_MISSING_LIQUID.
- f29v.3:6, Vollzug f29v.3:6: zerkleinere B1. moisture=WET;temperature=UNKNOWN;texture=UNKNOWN → moisture=WET;temperature=UNKNOWN;texture=GROUND; BOUND.
- f29v.4:2, Vollzug f29v.4:3: kühle A1. moisture=UNKNOWN;temperature=UNKNOWN;texture=UNKNOWN → moisture=UNKNOWN;temperature=COLD;texture=UNKNOWN; BOUND.
- f29v.4:7, Vollzug f29v.4:7: erwärme B1. moisture=WET;temperature=COLD;texture=GROUND → moisture=WET;temperature=HOT;texture=GROUND; BOUND.
- f29v.1:8: B1 soll moisture=WET haben; fortgeführter Wert WET aus f29v.1:6; CONSISTENT.
- f29v.1:10: B1 soll moisture=WET haben; fortgeführter Wert WET aus f29v.1:6; CONSISTENT.
- f29v.2:3: B1 soll moisture=DRY haben; fortgeführter Wert WET aus f29v.1:6; CONFLICT.
- f29v.2:4: B1 soll moisture=DRY haben; fortgeführter Wert WET aus f29v.1:6; CONFLICT.
- f29v.3:1: B1 soll moisture=DRY haben; fortgeführter Wert WET aus f29v.1:6; CONFLICT.
- f29v.3:2: B1 soll moisture=DRY haben; fortgeführter Wert WET aus f29v.1:6; CONFLICT.
- f29v.4:5: B1 soll temperature=COLD haben; fortgeführter Wert UNKNOWN aus NA; INITIAL_CONSTRAINT.
- f29v.4:5: B1 soll moisture=DRY haben; fortgeführter Wert WET aus f29v.1:6; CONFLICT.

## f32v

**f32v.7** `ksho cphos she sheaiin otshcho r dain shckhy s odan`

⟦ksho⟧ · zerreibe(ZIEL FEHLT;Quelle=NA) · ⟦she⟧ · ⟦sheaiin⟧ · ⟦otshcho⟧ · ⟦r⟧ · ⟦dain⟧ · ⟦shckhy⟧ · ⟦s⟧ · ⟦odan⟧

**f32v.8** `otchol daiin daiin ctho daiin qotaiin otchy d shan`

⟦otchol⟧ · ⟦daiin⟧ · ⟦daiin⟧ · ⟦ctho⟧ · ⟦daiin⟧ · ⟦qotaiin⟧ · ⟦otchy⟧ · ⟦d⟧ · ⟦shan⟧

**f32v.9** `qotchy cfhy skey chocthy daiin cthaiin daiin`

zerkleinere(ZIEL FEHLT;Quelle=NA) · ⟦cfhy⟧ · ⟦skey⟧ · ⟦chocthy⟧ · ⟦daiin⟧ · ⟦cthaiin⟧ · ⟦daiin⟧

**f32v.10** `sho keol chor chol daiin cpho l cthol da ar`

⟦sho⟧ · ⟦keol⟧ · Blüten[C1;neue Instanz;moisture=UNKNOWN;temperature=UNKNOWN;texture=UNKNOWN] · C1:moisture=DRY[INITIAL_CONSTRAINT;vorher=UNKNOWN;Quelle=NA] · ⟦daiin⟧ · zerstoße(C1;Quelle=f32v.10:3) · ⟦l⟧ · ⟦cthol⟧ · ⟦da⟧ · ⟦ar⟧

**f32v.11** `ol sho chy`

⟦ol⟧ · ⟦sho⟧ · ⟦chy⟧

### Ereignisse und Zustandserhaltung

- f32v.7:2, Vollzug f32v.7:2: zerreibe NA. NA → NA; MISSING_TARGET.
- f32v.9:1, Vollzug f32v.9:1: zerkleinere NA. NA → NA; MISSING_TARGET.
- f32v.10:6, Vollzug f32v.10:6: zerstoße C1. moisture=DRY;temperature=UNKNOWN;texture=UNKNOWN → moisture=DRY;temperature=UNKNOWN;texture=GROUND; BOUND.
- f32v.10:4: C1 soll moisture=DRY haben; fortgeführter Wert UNKNOWN aus NA; INITIAL_CONSTRAINT.

## f17r

**f17r.4** `tcho shol qokol qor olaiin opydg som ypchy ypaim`

⟦tcho⟧ · ZIEL FEHLT:moisture=WET[MISSING_TARGET;vorher=UNKNOWN;Quelle=NA] · ⟦qokol⟧ · ⟦qor⟧ · ⟦olaiin⟧ · ⟦opydg⟧ · ⟦som⟧ · ⟦ypchy⟧ · ⟦ypaim⟧

**f17r.5** `ychekchy cthy chor shor cphor cphaldy dair cthey qody`

⟦ychekchy⟧ · Kraut[B1;neue Instanz;moisture=UNKNOWN;temperature=UNKNOWN;texture=UNKNOWN] · Blüten[C1;neue Instanz;moisture=UNKNOWN;temperature=UNKNOWN;texture=UNKNOWN] · ⟦shor⟧ · ⟦cphor⟧ · ⟦cphaldy⟧ · ⟦dair⟧ · ⟦cthey⟧ · ⟦qody⟧

**f17r.6** `tsho qof cho qokcheor cheteg`

⟦tsho⟧ · ⟦qof⟧ · ⟦cho⟧ · ⟦qokcheor⟧ · ⟦cheteg⟧

### Ereignisse und Zustandserhaltung

- f17r.4:2: NA soll moisture=WET haben; fortgeführter Wert UNKNOWN aus NA; MISSING_TARGET.

## f21r

**f21r.8** `fcho kshy otor sheol ocphal opsheas cthodaiin oty`

⟦fcho⟧ · ⟦kshy⟧ · ⟦otor⟧ · ⟦sheol⟧ · ⟦ocphal⟧ · ⟦opsheas⟧ · ⟦cthodaiin⟧ · ⟦oty⟧

**f21r.9** `okaiin sho tshaiin chkaiin sh cthey cthody cthy s`

Ansatz[A1;neue Instanz;moisture=UNKNOWN;temperature=UNKNOWN;texture=UNKNOWN] · ⟦sho⟧ · ⟦tshaiin⟧ · ⟦chkaiin⟧ · ⟦sh⟧ · ⟦cthey⟧ · ⟦cthody⟧ · Kraut[B1;neue Instanz;moisture=UNKNOWN;temperature=UNKNOWN;texture=UNKNOWN] · ⟦s⟧

**f21r.10** `totchy keor chy ky qotaiin qotchol ty ctheey otaiin`

⟦totchy⟧ · ⟦keor⟧ · ⟦chy⟧ · ⟦ky⟧ · ⟦qotaiin⟧ · ⟦qotchol⟧ · ⟦ty⟧ · ⟦ctheey⟧ · ⟦otaiin⟧

**f21r.11** `shol chol shol tchol chcthy otyky shey yteol shody`

B1:moisture=WET[INITIAL_CONSTRAINT;vorher=UNKNOWN;Quelle=NA] · B1:moisture=DRY[CONFLICT;vorher=WET;Quelle=f21r.11:1] · B1:moisture=WET[CONSISTENT;vorher=WET;Quelle=f21r.11:1] · ⟦tchol⟧ · ⟦chcthy⟧ · ⟦otyky⟧ · ⟦shey⟧ · ⟦yteol⟧ · ⟦shody⟧

**f21r.12** `ykeey chor sheey ysheol chor chol daiin chkaiin`

⟦ykeey⟧ · Blüten[C1;neue Instanz;moisture=UNKNOWN;temperature=UNKNOWN;texture=UNKNOWN] · ⟦sheey⟧ · ⟦ysheol⟧ · Blüten[C1;wiederaufgenommen;moisture=UNKNOWN;temperature=UNKNOWN;texture=UNKNOWN] · C1:moisture=DRY[INITIAL_CONSTRAINT;vorher=UNKNOWN;Quelle=NA] · ⟦daiin⟧ · ⟦chkaiin⟧

### Ereignisse und Zustandserhaltung

- f21r.11:1: B1 soll moisture=WET haben; fortgeführter Wert UNKNOWN aus NA; INITIAL_CONSTRAINT.
- f21r.11:2: B1 soll moisture=DRY haben; fortgeführter Wert WET aus f21r.11:1; CONFLICT.
- f21r.11:3: B1 soll moisture=WET haben; fortgeführter Wert WET aus f21r.11:1; CONSISTENT.
- f21r.12:6: C1 soll moisture=DRY haben; fortgeführter Wert UNKNOWN aus NA; INITIAL_CONSTRAINT.
