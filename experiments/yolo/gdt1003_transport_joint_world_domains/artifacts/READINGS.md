# Every projected shared code and complete representative reading

All values below are hypothetical fixed terminal meanings, not word translations. Every paragraph is shown completely. W/G/C denote anonymous cargo labels here; their conventional source names have no independent support. M is the assumed transporting agent, B the assumed boat. Each tuple has one full representative; its other possible full dictionaries/parses were not exhausted.

## P0-3 — 8 complete shared tuples


### P0-3-T01: okaiin=W

Coherent variants for this representative: ZL-P00-V00, ZL-P00-V02, ZL-P00-V04, ZL-P00-V06. New whole-word aliases: 62; distinct new THEN aliases: 2.

ZL3b|f112v|f112v.45-f112v.47

Source flag: False; cargo: W; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| ycheey chokeey okasal tchdy oteol | INITIAL: INIT CARGOS COLOC M HOME |
| chcthy alaiin | FERRY: FERRY W |
| char | THEN: THEN |
| al kamdam ykeey lor chaiin cheky | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| chokain | THEN: THEN |
| char | THEN: THEN |
| am chey kain chdal okaiin | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE W |
| daldy [?:e] otar aig | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| oaral alor aiiin olkaiin oty ary | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, M=L, W=L] → load W [B=R, M=R, W=R].

IT2a|f24v|f24v.1-f24v.5

Source flag: True; cargo: G,W; voyages: [3]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| tchodar chocfhhg opom shod chcphy | INITIAL: INIT CARGOS COLOC M HOME |
| opshody ocphoraiin okokom ydals ckhor | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE W |
| shy cho dchar otol | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| otaiir otchos | FERRY: FERRY G |
| okchom okcho octhol odchees oesearees okam | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| chcth ydal | EXCLUDE: RETURN_EXCLUDING W |
| sh okol okaiin | CONVEY: CONVEY_OUT NEXT W |
| odaiin dlos oeor oraiin tchar oro | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, G=L, M=L, W=L] → load G [B=R, G=R, M=R, W=L] → load None [B=L, G=R, M=L, W=L] → load W [B=R, G=R, M=R, W=R].

Other variants: none fail this representative. Every full failed path remains in ROWS.json.

### P0-3-T02: okaiin=HARM

Coherent variants for this representative: ZL-P00-V00, ZL-P00-V02, ZL-P00-V04, ZL-P00-V06. New whole-word aliases: 62; distinct new THEN aliases: 4.

ZL3b|f112v|f112v.45-f112v.47

Source flag: False; cargo: W; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| ycheey chokeey okasal tchdy oteol | INITIAL: INIT CARGOS COLOC M HOME |
| chcthy alaiin char al kamdam | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE W |
| ykeey lor chaiin cheky chokain char | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| am | THEN: THEN |
| chey kain chdal okaiin | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| daldy [?:e] otar aig | WITH_OUT: WITH_TRIP B TAKE_OUT FIRST_CARGO |
| oaral alor aiiin olkaiin oty ary | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, M=L, W=L] → load W [B=R, M=R, W=R].

IT2a|f24v|f24v.1-f24v.5

Source flag: True; cargo: W; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| tchodar chocfhhg opom shod chcphy | INITIAL: INIT CARGOS COLOC M HOME |
| opshody ocphoraiin okokom ydals ckhor | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE W |
| shy cho dchar otol | WITH_OUT: WITH_TRIP B TAKE_OUT W |
| otaiir | THEN: THEN |
| otchos | THEN: THEN |
| okchom okcho octhol odchees oesearees okam | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| chcth | THEN: THEN |
| ydal sh okol okaiin | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| odaiin dlos oeor oraiin tchar oro | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, M=L, W=L] → load W [B=R, M=R, W=R].

Other variants: none fail this representative. Every full failed path remains in ROWS.json.

### P0-3-T03: okaiin=THEN

Coherent variants for this representative: ZL-P00-V04, ZL-P00-V06. New whole-word aliases: 62; distinct new THEN aliases: 4.

ZL3b|f112v|f112v.45-f112v.47

Source flag: False; cargo: W; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| ycheey chokeey okasal tchdy oteol | INITIAL: INIT CARGOS COLOC M HOME |
| chcthy alaiin char al kamdam | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE W |
| ykeey lor chaiin cheky chokain char | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| am chey kain chdal | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| okaiin | THEN: THEN |
| daldy [?:e] otar aig | WITH_OUT: WITH_TRIP B TAKE_OUT OTHER_CARGO |
| oaral alor aiiin olkaiin oty ary | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, M=L, W=L] → load W [B=R, M=R, W=R].

IT2a|f24v|f24v.1-f24v.5

Source flag: True; cargo: W; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| tchodar chocfhhg opom shod chcphy | INITIAL: INIT CARGOS COLOC M HOME |
| opshody ocphoraiin okokom ydals | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| ckhor shy cho dchar otol | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE W |
| otaiir | THEN: THEN |
| otchos | THEN: THEN |
| okchom | THEN: THEN |
| okcho octhol odchees oesearees okam chcth | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| ydal sh okol | CONVEY: CONVEY_OUT NEXT OTHER_CARGO |
| okaiin | THEN: THEN |
| odaiin dlos oeor oraiin tchar oro | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, M=L, W=L] → load W [B=R, M=R, W=R].

Other variants: ZL-P00-V00: ZL3b|f112v|f112v.45-f112v.47 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER, IT2a|f24v|f24v.1-f24v.5 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER; ZL-P00-V02: ZL3b|f112v|f112v.45-f112v.47 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER, IT2a|f24v|f24v.1-f24v.5 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER Every full failed path remains in ROWS.json.

### P0-3-T04: okaiin=OTHER_CARGO

Coherent variants for this representative: ZL-P00-V04, ZL-P00-V06. New whole-word aliases: 62; distinct new THEN aliases: 5.

ZL3b|f112v|f112v.45-f112v.47

Source flag: False; cargo: W; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| ycheey chokeey okasal tchdy oteol | INITIAL: INIT CARGOS COLOC M HOME |
| chcthy alaiin char al kamdam | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE W |
| ykeey lor chaiin cheky chokain char | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| am | THEN: THEN |
| chey kain chdal okaiin | WITH_OUT: WITH_TRIP B TAKE_OUT OTHER_CARGO |
| daldy [?:e] otar aig | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| oaral alor aiiin olkaiin oty ary | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, M=L, W=L] → load W [B=R, M=R, W=R].

IT2a|f24v|f24v.1-f24v.5

Source flag: True; cargo: W; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| tchodar chocfhhg opom shod chcphy | INITIAL: INIT CARGOS COLOC M HOME |
| opshody ocphoraiin okokom ydals | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| ckhor shy cho dchar otol | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE W |
| otaiir | THEN: THEN |
| otchos | THEN: THEN |
| okchom | THEN: THEN |
| okcho | THEN: THEN |
| octhol odchees oesearees okam chcth ydal | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| sh okol okaiin | CONVEY: CONVEY_OUT NEXT OTHER_CARGO |
| odaiin dlos oeor oraiin tchar oro | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, M=L, W=L] → load W [B=R, M=R, W=R].

Other variants: ZL-P00-V00: ZL3b|f112v|f112v.45-f112v.47 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER, IT2a|f24v|f24v.1-f24v.5 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER; ZL-P00-V02: ZL3b|f112v|f112v.45-f112v.47 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER, IT2a|f24v|f24v.1-f24v.5 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER Every full failed path remains in ROWS.json.

### P0-3-T05: okaiin=FIRST_CARGO

Coherent variants for this representative: ZL-P00-V00, ZL-P00-V02, ZL-P00-V04, ZL-P00-V06. New whole-word aliases: 62; distinct new THEN aliases: 5.

ZL3b|f112v|f112v.45-f112v.47

Source flag: False; cargo: W; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| ycheey chokeey okasal tchdy oteol | INITIAL: INIT CARGOS COLOC M HOME |
| chcthy alaiin char al kamdam | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE W |
| ykeey lor chaiin cheky chokain char | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| am | THEN: THEN |
| chey kain chdal okaiin | WITH_OUT: WITH_TRIP B TAKE_OUT FIRST_CARGO |
| daldy [?:e] otar aig | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| oaral alor aiiin olkaiin oty ary | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, M=L, W=L] → load W [B=R, M=R, W=R].

IT2a|f24v|f24v.1-f24v.5

Source flag: True; cargo: W; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| tchodar chocfhhg opom shod chcphy | INITIAL: INIT CARGOS COLOC M HOME |
| opshody ocphoraiin okokom ydals | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| ckhor shy cho dchar otol | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE W |
| otaiir | THEN: THEN |
| otchos | THEN: THEN |
| okchom | THEN: THEN |
| okcho | THEN: THEN |
| octhol odchees oesearees okam chcth ydal | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| sh okol okaiin | CONVEY: CONVEY_OUT NEXT FIRST_CARGO |
| odaiin dlos oeor oraiin tchar oro | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, M=L, W=L] → load W [B=R, M=R, W=R].

Other variants: none fail this representative. Every full failed path remains in ROWS.json.

### P0-3-T06: okaiin=THERE

Coherent variants for this representative: ZL-P00-V00, ZL-P00-V02, ZL-P00-V04, ZL-P00-V06. New whole-word aliases: 62; distinct new THEN aliases: 3.

ZL3b|f112v|f112v.45-f112v.47

Source flag: False; cargo: W; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| ycheey chokeey okasal tchdy oteol | INITIAL: INIT CARGOS COLOC M HOME |
| chcthy alaiin char al kamdam | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE W |
| ykeey lor chaiin cheky chokain char | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| am chey kain | CONVEY: CONVEY_OUT NEXT W |
| chdal okaiin | STAY: LEAVE THERE |
| daldy [?:e] otar aig | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| oaral alor aiiin olkaiin oty ary | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, M=L, W=L] → load W [B=R, M=R, W=R].

IT2a|f24v|f24v.1-f24v.5

Source flag: True; cargo: G; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| tchodar chocfhhg opom shod chcphy | INITIAL: INIT CARGOS COLOC M HOME |
| opshody ocphoraiin okokom ydals | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| ckhor shy cho dchar otol | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE G |
| otaiir | THEN: THEN |
| otchos | THEN: THEN |
| okchom okcho octhol odchees oesearees okam | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| chcth | THEN: THEN |
| ydal sh | FERRY: FERRY FIRST_CARGO |
| okol okaiin | STAY: LEAVE THERE |
| odaiin dlos oeor oraiin tchar oro | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, G=L, M=L] → load G [B=R, G=R, M=R].

Other variants: none fail this representative. Every full failed path remains in ROWS.json.

### P0-3-T07: okaiin=C

Coherent variants for this representative: ZL-P00-V00, ZL-P00-V02, ZL-P00-V04, ZL-P00-V06. New whole-word aliases: 62; distinct new THEN aliases: 4.

ZL3b|f112v|f112v.45-f112v.47

Source flag: False; cargo: C; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| ycheey chokeey okasal tchdy oteol | INITIAL: INIT CARGOS COLOC M HOME |
| chcthy alaiin char al kamdam | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE C |
| ykeey lor chaiin cheky chokain char | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| am | THEN: THEN |
| chey kain chdal okaiin | WITH_OUT: WITH_TRIP B TAKE_OUT C |
| daldy [?:e] otar aig | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| oaral alor aiiin olkaiin oty ary | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, C=L, M=L] → load C [B=R, C=R, M=R].

IT2a|f24v|f24v.1-f24v.5

Source flag: True; cargo: C; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| tchodar chocfhhg opom shod chcphy | INITIAL: INIT CARGOS COLOC M HOME |
| opshody ocphoraiin okokom ydals | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| ckhor shy cho dchar otol otaiir | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| otchos okchom | FERRY: FERRY C |
| okcho | THEN: THEN |
| octhol odchees | STAY: LEAVE THERE |
| oesearees | THEN: THEN |
| okam | THEN: THEN |
| chcth ydal sh okol okaiin | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE C |
| odaiin dlos oeor oraiin tchar oro | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, C=L, M=L] → load C [B=R, C=R, M=R].

Other variants: none fail this representative. Every full failed path remains in ROWS.json.

### P0-3-T08: okaiin=G

Coherent variants for this representative: ZL-P00-V00, ZL-P00-V02, ZL-P00-V04, ZL-P00-V06. New whole-word aliases: 62; distinct new THEN aliases: 2.

ZL3b|f112v|f112v.45-f112v.47

Source flag: False; cargo: G; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| ycheey chokeey okasal tchdy oteol | INITIAL: INIT CARGOS COLOC M HOME |
| chcthy alaiin char al kamdam | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE G |
| ykeey lor chaiin cheky chokain char | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| am | THEN: THEN |
| chey kain chdal okaiin | WITH_OUT: WITH_TRIP B TAKE_OUT G |
| daldy [?:e] otar aig | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| oaral alor aiiin olkaiin oty ary | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, G=L, M=L] → load G [B=R, G=R, M=R].

IT2a|f24v|f24v.1-f24v.5

Source flag: True; cargo: G; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| tchodar chocfhhg opom shod chcphy | INITIAL: INIT CARGOS COLOC M HOME |
| opshody ocphoraiin okokom ydals ckhor shy | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| cho | THEN: THEN |
| dchar otol otaiir otchos | WITH_OUT: WITH_TRIP B TAKE_OUT G |
| okchom okcho octhol odchees | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| oesearees okam | STAY: LEAVE THERE |
| chcth ydal sh okol okaiin | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE G |
| odaiin dlos oeor oraiin tchar oro | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, G=L, M=L] → load G [B=R, G=R, M=R].

Other variants: none fail this representative. Every full failed path remains in ROWS.json.

## P2-4 — 16 complete shared tuples


### P2-4-T01: dcheor=M, s=W, shodol=M

Coherent variants for this representative: ZL-P00-V04, ZL-P00-V06. New whole-word aliases: 61; distinct new THEN aliases: 5.

IT2a|f100r|f100r.12-f100r.15

Source flag: True; cargo: W; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| pcheol sheod qocpheeckhy shodol cthdaoto | INITIAL: INIT CARGOS COLOC M HOME |
| ch qeos sheey chcthso s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE W |
| dsheor cthey qokeey oteey | WITH_OUT: WITH_TRIP B TAKE_OUT OTHER_CARGO |
| ykeeodain sorary | STAY: LEAVE THERE |
| daiin | THEN: THEN |
| daiin | THEN: THEN |
| deeamshol | THEN: THEN |
| shor chkeey qoteey qokeody | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| qoteold | THEN: THEN |
| qokeol so raiin otal ykecho dcheor | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| shol qokeeol chor chol qokeeody dorean | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, M=L, W=L] → load W [B=R, M=R, W=R].

IT2a|f96r|f96r.9-f96r.13

Source flag: False; cargo: W; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| todar sheo cthody shokocfhy chopcho | INITIAL: INIT CARGOS COLOC M HOME |
| dory otcho dol shocthody | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| shockhy otchodor chocty teol cheody shodol | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| qokchod s | FERRY: FERRY W |
| aiin chokey dcheor cheol cheodain | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE W |
| ol | THEN: THEN |
| dy | THEN: THEN |
| d chs archeody oteeo dsho qotchos | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, M=L, W=L] → load W [B=R, M=R, W=R].

Other variants: ZL-P00-V00: IT2a|f100r|f100r.12-f100r.15 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER; ZL-P00-V02: IT2a|f100r|f100r.12-f100r.15 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER Every full failed path remains in ROWS.json.

### P2-4-T02: dcheor=M, s=G, shodol=M

Coherent variants for this representative: ZL-P00-V00, ZL-P00-V02, ZL-P00-V04, ZL-P00-V06. New whole-word aliases: 61; distinct new THEN aliases: 3.

IT2a|f100r|f100r.12-f100r.15

Source flag: True; cargo: G; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| pcheol sheod qocpheeckhy shodol cthdaoto | INITIAL: INIT CARGOS COLOC M HOME |
| ch qeos sheey chcthso s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE G |
| dsheor cthey qokeey oteey | WITH_OUT: WITH_TRIP B TAKE_OUT G |
| ykeeodain sorary | STAY: LEAVE THERE |
| daiin | THEN: THEN |
| daiin | THEN: THEN |
| deeamshol | THEN: THEN |
| shor chkeey qoteey qokeody | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| qoteold | THEN: THEN |
| qokeol so raiin otal ykecho dcheor | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| shol qokeeol chor chol qokeeody dorean | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, G=L, M=L] → load G [B=R, G=R, M=R].

IT2a|f96r|f96r.9-f96r.13

Source flag: False; cargo: G; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| todar sheo cthody shokocfhy chopcho | INITIAL: INIT CARGOS COLOC M HOME |
| dory otcho dol shocthody | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| shockhy otchodor chocty teol cheody shodol | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| qokchod s | FERRY: FERRY G |
| aiin chokey dcheor cheol cheodain | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE G |
| ol dy | STAY: LEAVE THERE |
| d chs archeody oteeo dsho qotchos | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, G=L, M=L] → load G [B=R, G=R, M=R].

Other variants: none fail this representative. Every full failed path remains in ROWS.json.

### P2-4-T03: dcheor=M, s=C, shodol=M

Coherent variants for this representative: ZL-P00-V00, ZL-P00-V02, ZL-P00-V04, ZL-P00-V06. New whole-word aliases: 61; distinct new THEN aliases: 3.

IT2a|f100r|f100r.12-f100r.15

Source flag: True; cargo: C; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| pcheol sheod qocpheeckhy shodol cthdaoto | INITIAL: INIT CARGOS COLOC M HOME |
| ch qeos sheey chcthso s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE C |
| dsheor cthey qokeey oteey | WITH_OUT: WITH_TRIP B TAKE_OUT FIRST_CARGO |
| ykeeodain | THEN: THEN |
| sorary | THEN: THEN |
| daiin | THEN: THEN |
| daiin | THEN: THEN |
| deeamshol shor | STAY: LEAVE THERE |
| chkeey qoteey qokeody qoteold | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| qokeol so raiin otal ykecho dcheor | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| shol qokeeol chor chol qokeeody dorean | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, C=L, M=L] → load C [B=R, C=R, M=R].

IT2a|f96r|f96r.9-f96r.13

Source flag: False; cargo: C; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| todar sheo cthody shokocfhy chopcho | INITIAL: INIT CARGOS COLOC M HOME |
| dory otcho dol shocthody | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| shockhy otchodor chocty teol cheody shodol | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| qokchod s | FERRY: FERRY C |
| aiin chokey dcheor cheol cheodain | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE C |
| ol dy | STAY: LEAVE THERE |
| d chs archeody oteeo dsho qotchos | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, C=L, M=L] → load C [B=R, C=R, M=R].

Other variants: none fail this representative. Every full failed path remains in ROWS.json.

### P2-4-T04: dcheor=THEN, s=G, shodol=M

Coherent variants for this representative: ZL-P00-V04, ZL-P00-V06. New whole-word aliases: 61; distinct new THEN aliases: 6.

IT2a|f100r|f100r.12-f100r.15

Source flag: True; cargo: G; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| pcheol sheod qocpheeckhy shodol cthdaoto | INITIAL: INIT CARGOS COLOC M HOME |
| ch qeos sheey chcthso s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE G |
| dsheor cthey qokeey oteey | WITH_OUT: WITH_TRIP B TAKE_OUT OTHER_CARGO |
| ykeeodain | THEN: THEN |
| sorary | THEN: THEN |
| daiin | THEN: THEN |
| daiin | THEN: THEN |
| deeamshol shor chkeey qoteey | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| qokeody | THEN: THEN |
| qoteold qokeol so raiin otal ykecho | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| dcheor | THEN: THEN |
| shol qokeeol chor chol qokeeody dorean | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, G=L, M=L] → load G [B=R, G=R, M=R].

IT2a|f96r|f96r.9-f96r.13

Source flag: False; cargo: G; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| todar sheo cthody shokocfhy chopcho | INITIAL: INIT CARGOS COLOC M HOME |
| dory otcho dol shocthody shockhy otchodor | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| chocty | THEN: THEN |
| teol cheody shodol qokchod s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE G |
| aiin chokey | FERRY: FERRY FIRST_CARGO |
| dcheor | THEN: THEN |
| cheol cheodain ol dy | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| d chs archeody oteeo dsho qotchos | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, G=L, M=L] → load G [B=R, G=R, M=R].

Other variants: ZL-P00-V00: IT2a|f100r|f100r.12-f100r.15 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER; ZL-P00-V02: IT2a|f100r|f100r.12-f100r.15 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER Every full failed path remains in ROWS.json.

### P2-4-T05: dcheor=M, s=THEN, shodol=M

Coherent variants for this representative: ZL-P00-V00, ZL-P00-V02, ZL-P00-V04, ZL-P00-V06. New whole-word aliases: 61; distinct new THEN aliases: 6.

IT2a|f100r|f100r.12-f100r.15

Source flag: True; cargo: W; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| pcheol sheod qocpheeckhy shodol cthdaoto | INITIAL: INIT CARGOS COLOC M HOME |
| ch qeos sheey chcthso | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| s | THEN: THEN |
| dsheor cthey qokeey oteey | WITH_OUT: WITH_TRIP B TAKE_OUT W |
| ykeeodain | THEN: THEN |
| sorary | THEN: THEN |
| daiin | THEN: THEN |
| daiin | THEN: THEN |
| deeamshol shor chkeey qoteey qokeody | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE W |
| qoteold | THEN: THEN |
| qokeol so raiin otal ykecho dcheor | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| shol qokeeol chor chol qokeeody dorean | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, M=L, W=L] → load W [B=R, M=R, W=R].

IT2a|f96r|f96r.9-f96r.13

Source flag: False; cargo: W; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| todar sheo cthody shokocfhy chopcho | INITIAL: INIT CARGOS COLOC M HOME |
| dory otcho dol shocthody | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| shockhy otchodor chocty teol cheody shodol | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| qokchod | THEN: THEN |
| s | THEN: THEN |
| aiin chokey dcheor cheol cheodain | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE W |
| ol dy | FERRY: FERRY FIRST_CARGO |
| d chs archeody oteeo dsho qotchos | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, M=L, W=L] → load W [B=R, M=R, W=R].

Other variants: none fail this representative. Every full failed path remains in ROWS.json.

### P2-4-T06: dcheor=THEN, s=C, shodol=M

Coherent variants for this representative: ZL-P00-V04, ZL-P00-V06. New whole-word aliases: 61; distinct new THEN aliases: 6.

IT2a|f100r|f100r.12-f100r.15

Source flag: True; cargo: C; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| pcheol sheod qocpheeckhy shodol cthdaoto | INITIAL: INIT CARGOS COLOC M HOME |
| ch qeos sheey chcthso s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE C |
| dsheor cthey qokeey oteey | WITH_OUT: WITH_TRIP B TAKE_OUT OTHER_CARGO |
| ykeeodain | THEN: THEN |
| sorary | THEN: THEN |
| daiin | THEN: THEN |
| daiin | THEN: THEN |
| deeamshol | THEN: THEN |
| shor chkeey qoteey qokeody | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| qoteold qokeol so raiin otal ykecho | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| dcheor | THEN: THEN |
| shol qokeeol chor chol qokeeody dorean | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, C=L, M=L] → load C [B=R, C=R, M=R].

IT2a|f96r|f96r.9-f96r.13

Source flag: False; cargo: C; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| todar sheo cthody shokocfhy chopcho | INITIAL: INIT CARGOS COLOC M HOME |
| dory | THEN: THEN |
| otcho dol shocthody shockhy otchodor chocty | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| teol cheody shodol qokchod s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE C |
| aiin chokey | FERRY: FERRY OTHER_CARGO |
| dcheor | THEN: THEN |
| cheol cheodain ol dy | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| d chs archeody oteeo dsho qotchos | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, C=L, M=L] → load C [B=R, C=R, M=R].

Other variants: ZL-P00-V00: IT2a|f100r|f100r.12-f100r.15 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER, IT2a|f96r|f96r.9-f96r.13 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER; ZL-P00-V02: IT2a|f100r|f100r.12-f100r.15 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER, IT2a|f96r|f96r.9-f96r.13 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER Every full failed path remains in ROWS.json.

### P2-4-T07: dcheor=THEN, s=W, shodol=M

Coherent variants for this representative: ZL-P00-V04, ZL-P00-V06. New whole-word aliases: 61; distinct new THEN aliases: 6.

IT2a|f100r|f100r.12-f100r.15

Source flag: True; cargo: W; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| pcheol sheod qocpheeckhy shodol cthdaoto | INITIAL: INIT CARGOS COLOC M HOME |
| ch qeos sheey chcthso s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE W |
| dsheor cthey qokeey oteey | WITH_OUT: WITH_TRIP B TAKE_OUT OTHER_CARGO |
| ykeeodain | THEN: THEN |
| sorary | THEN: THEN |
| daiin | THEN: THEN |
| daiin | THEN: THEN |
| deeamshol | THEN: THEN |
| shor chkeey qoteey qokeody | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| qoteold qokeol so raiin otal ykecho | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| dcheor | THEN: THEN |
| shol qokeeol chor chol qokeeody dorean | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, M=L, W=L] → load W [B=R, M=R, W=R].

IT2a|f96r|f96r.9-f96r.13

Source flag: False; cargo: W; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| todar sheo cthody shokocfhy chopcho | INITIAL: INIT CARGOS COLOC M HOME |
| dory | THEN: THEN |
| otcho dol shocthody shockhy otchodor chocty | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| teol cheody shodol qokchod s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE W |
| aiin chokey | FERRY: FERRY OTHER_CARGO |
| dcheor | THEN: THEN |
| cheol cheodain ol dy | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| d chs archeody oteeo dsho qotchos | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, M=L, W=L] → load W [B=R, M=R, W=R].

Other variants: ZL-P00-V00: IT2a|f100r|f100r.12-f100r.15 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER, IT2a|f96r|f96r.9-f96r.13 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER; ZL-P00-V02: IT2a|f100r|f100r.12-f100r.15 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER, IT2a|f96r|f96r.9-f96r.13 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER Every full failed path remains in ROWS.json.

### P2-4-T08: dcheor=OTHER_CARGO, s=G, shodol=M

Coherent variants for this representative: ZL-P00-V04, ZL-P00-V06. New whole-word aliases: 61; distinct new THEN aliases: 2.

IT2a|f100r|f100r.12-f100r.15

Source flag: True; cargo: G,W; voyages: [3]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| pcheol sheod qocpheeckhy shodol cthdaoto | INITIAL: INIT CARGOS COLOC M HOME |
| ch qeos sheey chcthso s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE G |
| dsheor cthey qokeey oteey | WITH_OUT: WITH_TRIP B TAKE_OUT W |
| ykeeodain sorary | ALONE: RETURN ALONE |
| daiin | THEN: THEN |
| daiin | THEN: THEN |
| deeamshol shor chkeey qoteey | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| qokeody qoteold qokeol so raiin otal | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| ykecho dcheor | FERRY: FERRY OTHER_CARGO |
| shol qokeeol chor chol qokeeody dorean | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, G=L, M=L, W=L] → load W [B=R, G=L, M=R, W=R] → load None [B=L, G=L, M=L, W=R] → load G [B=R, G=R, M=R, W=R].

IT2a|f96r|f96r.9-f96r.13

Source flag: False; cargo: G; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| todar sheo cthody shokocfhy chopcho | INITIAL: INIT CARGOS COLOC M HOME |
| dory | THEN: THEN |
| otcho dol shocthody shockhy otchodor chocty | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| teol cheody shodol qokchod s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE G |
| aiin chokey dcheor | CONVEY: CONVEY_OUT NEXT OTHER_CARGO |
| cheol cheodain ol dy | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| d chs archeody oteeo dsho qotchos | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, G=L, M=L] → load G [B=R, G=R, M=R].

Other variants: ZL-P00-V00: IT2a|f100r|f100r.12-f100r.15 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER, IT2a|f96r|f96r.9-f96r.13 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER; ZL-P00-V02: IT2a|f100r|f100r.12-f100r.15 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER, IT2a|f96r|f96r.9-f96r.13 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER Every full failed path remains in ROWS.json.

### P2-4-T09: dcheor=OTHER_CARGO, s=C, shodol=M

Coherent variants for this representative: ZL-P00-V04, ZL-P00-V06. New whole-word aliases: 61; distinct new THEN aliases: 2.

IT2a|f100r|f100r.12-f100r.15

Source flag: True; cargo: C,W; voyages: [3]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| pcheol sheod qocpheeckhy shodol cthdaoto | INITIAL: INIT CARGOS COLOC M HOME |
| ch qeos sheey chcthso s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE C |
| dsheor cthey qokeey oteey | WITH_OUT: WITH_TRIP B TAKE_OUT W |
| ykeeodain sorary | ALONE: RETURN ALONE |
| daiin | THEN: THEN |
| daiin | THEN: THEN |
| deeamshol shor chkeey qoteey | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| qokeody qoteold qokeol so raiin otal | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| ykecho dcheor | FERRY: FERRY OTHER_CARGO |
| shol qokeeol chor chol qokeeody dorean | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, C=L, M=L, W=L] → load W [B=R, C=L, M=R, W=R] → load None [B=L, C=L, M=L, W=R] → load C [B=R, C=R, M=R, W=R].

IT2a|f96r|f96r.9-f96r.13

Source flag: False; cargo: C; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| todar sheo cthody shokocfhy chopcho | INITIAL: INIT CARGOS COLOC M HOME |
| dory | THEN: THEN |
| otcho dol shocthody shockhy otchodor chocty | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| teol cheody shodol qokchod s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE C |
| aiin chokey dcheor | CONVEY: CONVEY_OUT NEXT OTHER_CARGO |
| cheol cheodain ol dy | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| d chs archeody oteeo dsho qotchos | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, C=L, M=L] → load C [B=R, C=R, M=R].

Other variants: ZL-P00-V00: IT2a|f100r|f100r.12-f100r.15 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER, IT2a|f96r|f96r.9-f96r.13 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER; ZL-P00-V02: IT2a|f100r|f100r.12-f100r.15 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER, IT2a|f96r|f96r.9-f96r.13 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER Every full failed path remains in ROWS.json.

### P2-4-T10: dcheor=FIRST_CARGO, s=C, shodol=M

Coherent variants for this representative: ZL-P00-V00, ZL-P00-V02, ZL-P00-V04, ZL-P00-V06. New whole-word aliases: 61; distinct new THEN aliases: 2.

IT2a|f100r|f100r.12-f100r.15

Source flag: True; cargo: C,W; voyages: [3]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| pcheol sheod qocpheeckhy shodol cthdaoto | INITIAL: INIT CARGOS COLOC M HOME |
| ch qeos sheey chcthso s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE C |
| dsheor cthey qokeey oteey | WITH_OUT: WITH_TRIP B TAKE_OUT W |
| ykeeodain sorary | ALONE: RETURN ALONE |
| daiin | THEN: THEN |
| daiin | THEN: THEN |
| deeamshol shor chkeey qoteey | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| qokeody qoteold qokeol so raiin otal | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| ykecho dcheor | FERRY: FERRY FIRST_CARGO |
| shol qokeeol chor chol qokeeody dorean | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, C=L, M=L, W=L] → load W [B=R, C=L, M=R, W=R] → load None [B=L, C=L, M=L, W=R] → load C [B=R, C=R, M=R, W=R].

IT2a|f96r|f96r.9-f96r.13

Source flag: False; cargo: C; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| todar sheo cthody shokocfhy chopcho | INITIAL: INIT CARGOS COLOC M HOME |
| dory | THEN: THEN |
| otcho dol shocthody shockhy otchodor chocty | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| teol cheody shodol qokchod s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE C |
| aiin chokey dcheor | CONVEY: CONVEY_OUT NEXT FIRST_CARGO |
| cheol cheodain ol dy | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| d chs archeody oteeo dsho qotchos | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, C=L, M=L] → load C [B=R, C=R, M=R].

Other variants: none fail this representative. Every full failed path remains in ROWS.json.

### P2-4-T11: dcheor=C, s=C, shodol=M

Coherent variants for this representative: ZL-P00-V00, ZL-P00-V02, ZL-P00-V04, ZL-P00-V06. New whole-word aliases: 61; distinct new THEN aliases: 2.

IT2a|f100r|f100r.12-f100r.15

Source flag: True; cargo: C,W; voyages: [3]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| pcheol sheod qocpheeckhy shodol cthdaoto | INITIAL: INIT CARGOS COLOC M HOME |
| ch qeos sheey chcthso s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE C |
| dsheor cthey qokeey oteey | WITH_OUT: WITH_TRIP B TAKE_OUT W |
| ykeeodain sorary | ALONE: RETURN ALONE |
| daiin | THEN: THEN |
| daiin | THEN: THEN |
| deeamshol shor chkeey qoteey | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| qokeody qoteold qokeol so raiin otal | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| ykecho dcheor | FERRY: FERRY C |
| shol qokeeol chor chol qokeeody dorean | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, C=L, M=L, W=L] → load W [B=R, C=L, M=R, W=R] → load None [B=L, C=L, M=L, W=R] → load C [B=R, C=R, M=R, W=R].

IT2a|f96r|f96r.9-f96r.13

Source flag: False; cargo: C; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| todar sheo cthody shokocfhy chopcho | INITIAL: INIT CARGOS COLOC M HOME |
| dory | THEN: THEN |
| otcho dol shocthody shockhy otchodor chocty | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| teol cheody shodol qokchod s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE C |
| aiin chokey dcheor | CONVEY: CONVEY_OUT NEXT C |
| cheol cheodain ol dy | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| d chs archeody oteeo dsho qotchos | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, C=L, M=L] → load C [B=R, C=R, M=R].

Other variants: none fail this representative. Every full failed path remains in ROWS.json.

### P2-4-T12: dcheor=FIRST_CARGO, s=G, shodol=M

Coherent variants for this representative: ZL-P00-V00, ZL-P00-V02, ZL-P00-V04, ZL-P00-V06. New whole-word aliases: 61; distinct new THEN aliases: 2.

IT2a|f100r|f100r.12-f100r.15

Source flag: True; cargo: G,W; voyages: [3]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| pcheol sheod qocpheeckhy shodol cthdaoto | INITIAL: INIT CARGOS COLOC M HOME |
| ch qeos sheey chcthso s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE G |
| dsheor cthey qokeey oteey | WITH_OUT: WITH_TRIP B TAKE_OUT W |
| ykeeodain sorary | ALONE: RETURN ALONE |
| daiin | THEN: THEN |
| daiin | THEN: THEN |
| deeamshol shor chkeey qoteey | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| qokeody qoteold qokeol so raiin otal | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| ykecho dcheor | FERRY: FERRY FIRST_CARGO |
| shol qokeeol chor chol qokeeody dorean | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, G=L, M=L, W=L] → load W [B=R, G=L, M=R, W=R] → load None [B=L, G=L, M=L, W=R] → load G [B=R, G=R, M=R, W=R].

IT2a|f96r|f96r.9-f96r.13

Source flag: False; cargo: G; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| todar sheo cthody shokocfhy chopcho | INITIAL: INIT CARGOS COLOC M HOME |
| dory | THEN: THEN |
| otcho dol shocthody shockhy otchodor chocty | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| teol cheody shodol qokchod s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE G |
| aiin chokey dcheor | CONVEY: CONVEY_OUT NEXT FIRST_CARGO |
| cheol cheodain ol dy | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| d chs archeody oteeo dsho qotchos | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, G=L, M=L] → load G [B=R, G=R, M=R].

Other variants: none fail this representative. Every full failed path remains in ROWS.json.

### P2-4-T13: dcheor=FIRST_CARGO, s=W, shodol=M

Coherent variants for this representative: ZL-P00-V00, ZL-P00-V02, ZL-P00-V04, ZL-P00-V06. New whole-word aliases: 61; distinct new THEN aliases: 2.

IT2a|f100r|f100r.12-f100r.15

Source flag: True; cargo: G,W; voyages: [3]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| pcheol sheod qocpheeckhy shodol cthdaoto | INITIAL: INIT CARGOS COLOC M HOME |
| ch qeos sheey chcthso s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE W |
| dsheor cthey qokeey oteey | WITH_OUT: WITH_TRIP B TAKE_OUT G |
| ykeeodain sorary | EXCLUDE: RETURN_EXCLUDING G |
| daiin | THEN: THEN |
| daiin | THEN: THEN |
| deeamshol shor chkeey qoteey | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| qokeody qoteold qokeol so raiin otal | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| ykecho dcheor | FERRY: FERRY FIRST_CARGO |
| shol qokeeol chor chol qokeeody dorean | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, G=L, M=L, W=L] → load G [B=R, G=R, M=R, W=L] → load None [B=L, G=R, M=L, W=L] → load W [B=R, G=R, M=R, W=R].

IT2a|f96r|f96r.9-f96r.13

Source flag: False; cargo: W; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| todar sheo cthody shokocfhy chopcho | INITIAL: INIT CARGOS COLOC M HOME |
| dory | THEN: THEN |
| otcho dol shocthody shockhy otchodor chocty | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| teol cheody shodol qokchod s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE W |
| aiin chokey dcheor | CONVEY: CONVEY_OUT NEXT FIRST_CARGO |
| cheol cheodain ol dy | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| d chs archeody oteeo dsho qotchos | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, M=L, W=L] → load W [B=R, M=R, W=R].

Other variants: none fail this representative. Every full failed path remains in ROWS.json.

### P2-4-T14: dcheor=OTHER_CARGO, s=W, shodol=M

Coherent variants for this representative: ZL-P00-V04, ZL-P00-V06. New whole-word aliases: 61; distinct new THEN aliases: 2.

IT2a|f100r|f100r.12-f100r.15

Source flag: True; cargo: G,W; voyages: [3]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| pcheol sheod qocpheeckhy shodol cthdaoto | INITIAL: INIT CARGOS COLOC M HOME |
| ch qeos sheey chcthso s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE W |
| dsheor cthey qokeey oteey | WITH_OUT: WITH_TRIP B TAKE_OUT G |
| ykeeodain sorary | EXCLUDE: RETURN_EXCLUDING G |
| daiin | THEN: THEN |
| daiin | THEN: THEN |
| deeamshol shor chkeey qoteey | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| qokeody qoteold qokeol so raiin otal | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| ykecho dcheor | FERRY: FERRY OTHER_CARGO |
| shol qokeeol chor chol qokeeody dorean | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, G=L, M=L, W=L] → load G [B=R, G=R, M=R, W=L] → load None [B=L, G=R, M=L, W=L] → load W [B=R, G=R, M=R, W=R].

IT2a|f96r|f96r.9-f96r.13

Source flag: False; cargo: W; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| todar sheo cthody shokocfhy chopcho | INITIAL: INIT CARGOS COLOC M HOME |
| dory | THEN: THEN |
| otcho dol shocthody shockhy otchodor chocty | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| teol cheody shodol qokchod s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE W |
| aiin chokey dcheor | CONVEY: CONVEY_OUT NEXT OTHER_CARGO |
| cheol cheodain ol dy | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| d chs archeody oteeo dsho qotchos | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, M=L, W=L] → load W [B=R, M=R, W=R].

Other variants: ZL-P00-V00: IT2a|f100r|f100r.12-f100r.15 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER, IT2a|f96r|f96r.9-f96r.13 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER; ZL-P00-V02: IT2a|f100r|f100r.12-f100r.15 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER, IT2a|f96r|f96r.9-f96r.13 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER Every full failed path remains in ROWS.json.

### P2-4-T15: dcheor=W, s=W, shodol=M

Coherent variants for this representative: ZL-P00-V00, ZL-P00-V02, ZL-P00-V04, ZL-P00-V06. New whole-word aliases: 61; distinct new THEN aliases: 2.

IT2a|f100r|f100r.12-f100r.15

Source flag: True; cargo: G,W; voyages: [3]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| pcheol sheod qocpheeckhy shodol cthdaoto | INITIAL: INIT CARGOS COLOC M HOME |
| ch qeos sheey chcthso s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE W |
| dsheor cthey qokeey oteey | WITH_OUT: WITH_TRIP B TAKE_OUT G |
| ykeeodain sorary | EXCLUDE: RETURN_EXCLUDING G |
| daiin | THEN: THEN |
| daiin | THEN: THEN |
| deeamshol shor chkeey qoteey qokeody qoteold | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| qokeol so raiin otal | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| ykecho dcheor | FERRY: FERRY W |
| shol qokeeol chor chol qokeeody dorean | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, G=L, M=L, W=L] → load G [B=R, G=R, M=R, W=L] → load None [B=L, G=R, M=L, W=L] → load W [B=R, G=R, M=R, W=R].

IT2a|f96r|f96r.9-f96r.13

Source flag: False; cargo: W; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| todar sheo cthody shokocfhy chopcho | INITIAL: INIT CARGOS COLOC M HOME |
| dory | THEN: THEN |
| otcho dol shocthody shockhy otchodor chocty | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| teol cheody shodol qokchod s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE W |
| aiin chokey dcheor | CONVEY: CONVEY_OUT NEXT W |
| cheol cheodain ol dy | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| d chs archeody oteeo dsho qotchos | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, M=L, W=L] → load W [B=R, M=R, W=R].

Other variants: none fail this representative. Every full failed path remains in ROWS.json.

### P2-4-T16: dcheor=G, s=G, shodol=M

Coherent variants for this representative: ZL-P00-V04, ZL-P00-V06. New whole-word aliases: 61; distinct new THEN aliases: 2.

IT2a|f100r|f100r.12-f100r.15

Source flag: True; cargo: C,G; voyages: [3]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| pcheol sheod qocpheeckhy shodol cthdaoto | INITIAL: INIT CARGOS COLOC M HOME |
| ch qeos sheey chcthso s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE G |
| dsheor cthey qokeey oteey | WITH_OUT: WITH_TRIP B TAKE_OUT C |
| ykeeodain sorary | EXCLUDE: RETURN_EXCLUDING OTHER_CARGO |
| daiin | THEN: THEN |
| daiin | THEN: THEN |
| deeamshol shor chkeey qoteey qokeody qoteold | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| qokeol so raiin otal | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| ykecho dcheor | FERRY: FERRY G |
| shol qokeeol chor chol qokeeody dorean | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, C=L, G=L, M=L] → load C [B=R, C=R, G=L, M=R] → load None [B=L, C=R, G=L, M=L] → load G [B=R, C=R, G=R, M=R].

IT2a|f96r|f96r.9-f96r.13

Source flag: False; cargo: G; voyages: [1]; hazard pairs: 0.

| Written groups, complete clause | Assumed fixed interpretation |
|---|---|
| todar sheo cthody shokocfhy chopcho | INITIAL: INIT CARGOS COLOC M HOME |
| dory | THEN: THEN |
| otcho dol shocthody shockhy otchodor chocty | SAFETY: UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M |
| teol cheody shodol qokchod s | CAPACITY: AT_MOST_ONE BESIDES M EXAMPLE G |
| aiin chokey dcheor | CONVEY: CONVEY_OUT NEXT G |
| cheol cheodain ol dy | GOAL: GOAL FAR_BANK WITHOUT_HARM HARM |
| d chs archeody oteeo dsho qotchos | CONCLUSION: THUS ALL UNHARMED THERE ATTENDED_BY M |

Complete successful path: initial [B=L, G=L, M=L] → load G [B=R, G=R, M=R].

Other variants: ZL-P00-V00: IT2a|f100r|f100r.12-f100r.15 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER; ZL-P00-V02: IT2a|f100r|f100r.12-f100r.15 BINDING_CONTRADICTION NO_PAIR_FOR_OTHER Every full failed path remains in ROWS.json.
