# RTA001 anonymous operator atlas

Overall result: **FAIL**.

Operators are fold-local anonymous medoids. IDs carry no meaning.

## Holdout f67 — construction, K=8

### OP01

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START,FREE_L;dst=LB:LINE_START,FREE_L) -> INSERT(dst=BARE) -> SPLIT_BOUNDARY(dst=WB) -> INSERT(dst=BARE) -> KEEP_CORE(src=WB;dst=WB) -> SUBSTITUTE(src=FREE_L;dst=BARE) -> KEEP_CORE(src=RB:LINE_END;dst=RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR
- Training folios: f68, f69, f70, f71, f72
- Training/held-out support: 20/12
- Examples: SCARR013|f69r|E1:E021, SCARR024|f71v|S1:E008, SCARR012|f68v2|S1:E001
- Counterexamples: SCARR013|f69r|E1:E021, SCARR024|f71v|S1:E008, SCARR012|f68v2|S1:E001
- Residual: 541.333 bits; composition 5.000; cycle 0.000
- Survives removal of literal surface identity: True

### OP02

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> DELETE(src=BARE) -> KEEP_CORE(src=FREE_R,RB:LINE_END;dst=FREE_R,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f68, f69, f70, f71, f72, f73, f75, fRos
- Training/held-out support: 107/6
- Examples: SCARR030|f72r2|S2:E006, SCARR038|f72v1|S1:E010, SCARR042|f73r|S2:E001
- Counterexamples: SCARR030|f72r2|S2:E006, SCARR038|f72v1|S1:E010, SCARR042|f73r|S2:E001
- Residual: 1439.333 bits; composition 5.000; cycle 0.000
- Survives removal of literal surface identity: True

### OP03

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> INSERT(dst=BARE) -> KEEP_CORE(src=BARE,RB:LINE_END;dst=BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f68, f70, f71, f72, f73, fRos
- Training/held-out support: 33/7
- Examples: SCARR045|f73v|S2:E003, fRos:RECORD3:R2_TO_R3, SCARR018|f70v2|S2:E017
- Counterexamples: SCARR045|f73v|S2:E003, fRos:RECORD3:R2_TO_R3, SCARR018|f70v2|S2:E017
- Residual: 464.667 bits; composition 5.000; cycle 0.000
- Survives removal of literal surface identity: True

### OP04

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> DELETE(src=BARE) -> KEEP_CORE(src=BARE,BARE,RB:LINE_END;dst=BARE,BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SUCCESSOR
- Training folios: f68, f69, f70, f71, f72, f75
- Training/held-out support: 62/15
- Examples: SCARR036|f72v2|S1:E009, SCARR031|f72r3|S1:E008, SCARR010|f68r3|S1:E002
- Counterexamples: SCARR036|f72v2|S1:E009, SCARR031|f72r3|S1:E008, SCARR010|f68r3|S1:E002
- Residual: 1064.000 bits; composition 5.000; cycle 0.000
- Survives removal of literal surface identity: True

### OP05

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> INSERT(dst=BARE) -> KEEP_CORE(src=BARE,BARE,RB:LINE_END;dst=BARE,BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f68, f69, f70, f71, f72, f73, f75, fRos
- Training/held-out support: 111/19
- Examples: SCARR045|f73v|S2:E004, SCARR009|f68r2|S1:E024, SCARR045|f73v|S2:E006
- Counterexamples: SCARR045|f73v|S2:E004, SCARR009|f68r2|S1:E024, SCARR045|f73v|S2:E006
- Residual: 1734.167 bits; composition 5.000; cycle 0.000
- Survives removal of literal surface identity: True

### OP06

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> DELETE(src=FREE_L) -> KEEP_CORE(src=BARE;dst=BARE) -> MERGE_BOUNDARY(src=WB) -> SUBSTITUTE(src=BARE;dst=BOUND_E) -> KEEP_CORE(src=WB,BARE,RB:LINE_END;dst=WB,BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR
- Training folios: f68, f69, f70, f71, f72
- Training/held-out support: 21/19
- Examples: SCARR012|f68v2|S1:E002, SCARR013|f69r|E1:E019, SCARR013|f69r|E1:E002
- Counterexamples: SCARR012|f68v2|S1:E002, SCARR013|f69r|E1:E019, SCARR013|f69r|E1:E002
- Residual: 615.000 bits; composition 5.000; cycle 0.000
- Survives removal of literal surface identity: True

### OP07

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START,BARE;dst=LB:LINE_START,BARE) -> INSERT(dst=BOUND_E) -> KEEP_CORE(src=RB:LINE_END;dst=RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR
- Training folios: f68, f69, f70, f71, f72, f73
- Training/held-out support: 45/2
- Examples: SCARR038|f72v1|S1:E013, SCARR015|f69v|X1:E014, SCARR041|f73r|S1:E015
- Counterexamples: SCARR038|f72v1|S1:E013, SCARR015|f69v|X1:E014, SCARR041|f73r|S1:E015
- Residual: 479.333 bits; composition 5.000; cycle 0.000
- Survives removal of literal surface identity: True

### OP08

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START,FREE_L,RB:LINE_END;dst=LB:LINE_START,FREE_L,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f68, f69, f70, f71, f72, f73, f75, fRos
- Training/held-out support: 56/2
- Examples: SCARR038|f72v1|S1:E006, SCARR039|f72v1|S2:E005, SCARR015|f69v|X1:E003
- Counterexamples: SCARR038|f72v1|S1:E006, SCARR039|f72v1|S2:E005, SCARR015|f69v|X1:E003
- Residual: 243.333 bits; composition 5.000; cycle 0.000
- Survives removal of literal surface identity: True

## Holdout f68 — construction, K=4

### OP01

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START,BOUND_E;dst=LB:LINE_START,BOUND_E) -> DELETE(src=BARE) -> KEEP_CORE(src=RB:LINE_END;dst=RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f69, f70, f71, f72, f73, f75, fRos
- Training/held-out support: 200/37
- Examples: SCARR036|f72v2|S1:E009, SCARR045|f73v|S2:E003, SCARR030|f72r2|S2:E006
- Counterexamples: SCARR036|f72v2|S1:E009, SCARR045|f73v|S2:E003, SCARR030|f72r2|S2:E006
- Residual: 3198.833 bits; composition 80.000; cycle 0.000
- Survives removal of literal surface identity: True

### OP02

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START,BOUND_E;dst=LB:LINE_START,BOUND_E) -> MERGE_BOUNDARY(src=WB) -> KEEP_CORE(src=BARE,RB:LINE_END;dst=BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f69, f70, f71, f72
- Training/held-out support: 69/8
- Examples: SCARR031|f72r3|S1:E008, f67r2:Q1:0830:R2_TO_R3, SCARR024|f71v|S1:E009
- Counterexamples: SCARR031|f72r3|S1:E008, f67r2:Q1:0830:R2_TO_R3, SCARR024|f71v|S1:E009
- Residual: 1840.333 bits; composition 80.000; cycle 0.000
- Survives removal of literal surface identity: True

### OP03

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> INSERT(dst=BARE) -> KEEP_CORE(src=BARE,RB:LINE_END;dst=BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f69, f70, f71, f72, f73, f75, fRos
- Training/held-out support: 142/27
- Examples: SCARR045|f73v|S2:E004, SCARR003|f67r2|M2:E003, SCARR018|f70v2|S2:E017
- Counterexamples: SCARR045|f73v|S2:E004, SCARR003|f67r2|M2:E003, SCARR018|f70v2|S2:E017
- Residual: 2175.000 bits; composition 80.000; cycle 0.000
- Survives removal of literal surface identity: True

### OP04

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START,BOUND_E;dst=LB:LINE_START,BOUND_E) -> INSERT(dst=BARE) -> SPLIT_BOUNDARY(dst=WB) -> KEEP_CORE(src=BARE,RB:LINE_END;dst=BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f69, f70, f71, f72, f75, fRos
- Training/held-out support: 50/4
- Examples: f67r2:Q1:0630:R1_TO_R2, SCARR033|f72r3|S3:E004, SCARR013|f69r|E1:E021
- Counterexamples: f67r2:Q1:0630:R1_TO_R2, SCARR033|f72r3|S3:E004, SCARR013|f69r|E1:E021
- Residual: 1200.833 bits; composition 80.000; cycle 0.000
- Survives removal of literal surface identity: True

## Holdout f69 — construction, K=4

### OP01

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> INSERT(dst=BARE) -> KEEP_CORE(src=BARE,RB:LINE_END;dst=BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f70, f71, f72, f73, f75, fRos
- Training/held-out support: 157/14
- Examples: SCARR045|f73v|S2:E004, SCARR045|f73v|S2:E003, SCARR003|f67r2|M2:E003
- Counterexamples: SCARR045|f73v|S2:E004, SCARR045|f73v|S2:E003, SCARR003|f67r2|M2:E003
- Residual: 2502.333 bits; composition 60.000; cycle 0.000
- Survives removal of literal surface identity: True

### OP02

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START,FREE_L,BARE,RB:LINE_END;dst=LB:LINE_START,FREE_L,BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f70, f71, f72, f73, f75, fRos
- Training/held-out support: 67/12
- Examples: SCARR038|f72v1|S1:E006, SCARR038|f72v1|S1:E013, fRos:RECORD3:R2_TO_R3
- Counterexamples: SCARR038|f72v1|S1:E006, SCARR038|f72v1|S1:E013, fRos:RECORD3:R2_TO_R3
- Residual: 542.000 bits; composition 60.000; cycle 0.000
- Survives removal of literal surface identity: True

### OP03

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> DELETE(src=BARE) -> KEEP_CORE(src=BARE,BARE,RB:LINE_END;dst=BARE,BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f70, f71, f72, f73, f75, fRos
- Training/held-out support: 213/19
- Examples: SCARR036|f72v2|S1:E009, SCARR030|f72r2|S2:E006, SCARR038|f72v1|S1:E010
- Counterexamples: SCARR036|f72v2|S1:E009, SCARR030|f72r2|S2:E006, SCARR038|f72v1|S1:E010
- Residual: 4242.833 bits; composition 60.000; cycle 0.000
- Survives removal of literal surface identity: True

### OP04

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START,BOUND_E;dst=LB:LINE_START,BOUND_E) -> INSERT(dst=BARE) -> SPLIT_BOUNDARY(dst=WB) -> KEEP_CORE(src=BARE,RB:LINE_END;dst=BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f70, f71, f72, f75, fRos
- Training/held-out support: 44/11
- Examples: f67r2:Q1:0630:R1_TO_R2, SCARR009|f68r2|S1:E024, SCARR033|f72r3|S3:E004
- Counterexamples: f67r2:Q1:0630:R1_TO_R2, SCARR009|f68r2|S1:E024, SCARR033|f72r3|S3:E004
- Residual: 960.833 bits; composition 60.000; cycle 0.000
- Survives removal of literal surface identity: True

## Holdout f70 — construction, K=8

### OP01

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START,BARE,BARE,RB:LINE_END;dst=LB:LINE_START,BARE,BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f71, f72, f73, f75, fRos
- Training/held-out support: 66/6
- Examples: SCARR038|f72v1|S1:E006, SCARR038|f72v1|S1:E013, fRos:RECORD3:R2_TO_R3
- Counterexamples: SCARR038|f72v1|S1:E006, SCARR038|f72v1|S1:E013, fRos:RECORD3:R2_TO_R3
- Residual: 480.333 bits; composition 103.333; cycle 0.000
- Survives removal of literal surface identity: True

### OP02

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> INSERT(dst=BARE) -> KEEP_CORE(src=BARE,RB:LINE_END;dst=BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f71, f72, f73, f75, fRos
- Training/held-out support: 132/14
- Examples: SCARR045|f73v|S2:E004, SCARR003|f67r2|M2:E003, SCARR015|f69v|X1:E014
- Counterexamples: SCARR045|f73v|S2:E004, SCARR003|f67r2|M2:E003, SCARR015|f69v|X1:E014
- Residual: 1774.333 bits; composition 103.333; cycle 0.000
- Survives removal of literal surface identity: True

### OP03

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> DELETE(src=FREE_L) -> MERGE_BOUNDARY(src=WB) -> SUBSTITUTE(src=BARE;dst=FREE_R) -> KEEP_CORE(src=RB:LINE_END;dst=RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SUCCESSOR
- Training folios: f67, f68, f71, f72
- Training/held-out support: 21/13
- Examples: SCARR010|f68r3|S1:E002, SCARR022|f71r|S1:E001, SCARR032|f72r3|S2:E008
- Counterexamples: SCARR022|f71r|S1:E001, SCARR032|f72r3|S2:E008, f67r2:Q1:0030:R2_TO_R3
- Residual: 433.000 bits; composition 103.333; cycle 0.000
- Survives removal of literal surface identity: True

### OP04

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> SUBSTITUTE(src=FREE_L;dst=BARE) -> KEEP_CORE(src=WB,BARE,WB;dst=WB,BARE,WB) -> DELETE(src=BARE) -> KEEP_CORE(src=BARE,RB:LINE_END;dst=BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f71
- Training/held-out support: 29/3
- Examples: f67r2:Q1:0630:R1_TO_R2, SCARR024|f71v|S1:E009, SCARR024|f71v|S1:E008
- Counterexamples: f67r2:Q1:0630:R1_TO_R2, SCARR024|f71v|S1:E009, SCARR024|f71v|S1:E008
- Residual: 768.667 bits; composition 103.333; cycle 0.000
- Survives removal of literal surface identity: True

### OP05

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START,BOUND_E;dst=LB:LINE_START,BOUND_E) -> INSERT(dst=BARE) -> SPLIT_BOUNDARY(dst=WB) -> KEEP_CORE(src=BARE,RB:LINE_END;dst=BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f71, f72, f75, fRos
- Training/held-out support: 38/7
- Examples: SCARR009|f68r2|S1:E024, SCARR033|f72r3|S3:E004, SCARR013|f69r|E1:E021
- Counterexamples: SCARR009|f68r2|S1:E024, SCARR033|f72r3|S3:E004, SCARR013|f69r|E1:E021
- Residual: 861.833 bits; composition 103.333; cycle 0.000
- Survives removal of literal surface identity: True

### OP06

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> SUBSTITUTE(src=BARE;dst=BOUND_E) -> KEEP_CORE(src=BARE,RB:LINE_END;dst=BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f71, f72, f73, fRos
- Training/held-out support: 60/1
- Examples: SCARR031|f72r3|S1:E008, f67r2:Q1:0830:R2_TO_R3, SCARR012|f68v2|S1:E002
- Counterexamples: SCARR031|f72r3|S1:E008, f67r2:Q1:0830:R2_TO_R3, SCARR012|f68v2|S1:E002
- Residual: 707.333 bits; composition 103.333; cycle 0.000
- Survives removal of literal surface identity: True

### OP07

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> DELETE(src=BARE) -> KEEP_CORE(src=FREE_R,RB:LINE_END;dst=FREE_R,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f71, f72, f73, f75, fRos
- Training/held-out support: 107/15
- Examples: SCARR036|f72v2|S1:E009, SCARR045|f73v|S2:E003, SCARR030|f72r2|S2:E006
- Counterexamples: SCARR036|f72v2|S1:E009, SCARR045|f73v|S2:E003, SCARR030|f72r2|S2:E006
- Residual: 1502.833 bits; composition 103.333; cycle 0.000
- Survives removal of literal surface identity: True

### OP08

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START,BOUND_E;dst=LB:LINE_START,BOUND_E) -> DELETE(src=BARE) -> KEEP_CORE(src=WB;dst=WB) -> DELETE(src=BARE) -> KEEP_CORE(src=BARE,WB,BARE,RB:LINE_END;dst=BARE,WB,BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f71, f72
- Training/held-out support: 25/0
- Examples: SCARR013|f69r|E1:E019, f67r2:Q1:1130:R1_TO_R3, SCARR013|f69r|E1:E002
- Counterexamples: SCARR013|f69r|E1:E019, f67r2:Q1:1130:R1_TO_R3, SCARR013|f69r|E1:E002
- Residual: 658.333 bits; composition 103.333; cycle 0.000
- Survives removal of literal surface identity: True

## Holdout f71 — construction, K=4

### OP01

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START,BOUND_E;dst=LB:LINE_START,BOUND_E) -> MERGE_BOUNDARY(src=WB) -> KEEP_CORE(src=BARE,RB:LINE_END;dst=BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f70, f72
- Training/held-out support: 60/4
- Examples: SCARR031|f72r3|S1:E008, SCARR010|f68r3|S1:E002, SCARR015|f69v|X1:E026
- Counterexamples: SCARR031|f72r3|S1:E008, SCARR010|f68r3|S1:E002, SCARR013|f69r|E1:E019
- Residual: 1539.333 bits; composition 51.667; cycle 0.000
- Survives removal of literal surface identity: True

### OP02

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> DELETE(src=BARE) -> KEEP_CORE(src=BARE,BARE,RB:LINE_END;dst=BARE,BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f70, f72, f73, f75, fRos
- Training/held-out support: 138/12
- Examples: SCARR036|f72v2|S1:E009, SCARR042|f73r|S2:E001, f67r2:Q1:0830:R2_TO_R3
- Counterexamples: SCARR036|f72v2|S1:E009, SCARR042|f73r|S2:E001, f67r2:Q1:0830:R2_TO_R3
- Residual: 2370.500 bits; composition 51.667; cycle 0.000
- Survives removal of literal surface identity: True

### OP03

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START,BARE,RB:LINE_END;dst=LB:LINE_START,BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f70, f72, f73, f75, fRos
- Training/held-out support: 112/3
- Examples: SCARR045|f73v|S2:E003, SCARR030|f72r2|S2:E006, SCARR038|f72v1|S1:E010
- Counterexamples: SCARR045|f73v|S2:E003, SCARR030|f72r2|S2:E006, SCARR038|f72v1|S1:E010
- Residual: 1209.667 bits; composition 51.667; cycle 0.000
- Survives removal of literal surface identity: True

### OP04

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> INSERT(dst=BARE) -> KEEP_CORE(src=BARE,BARE,RB:LINE_END;dst=BARE,BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f70, f72, f73, f75, fRos
- Training/held-out support: 197/11
- Examples: SCARR045|f73v|S2:E004, f67r2:Q1:0630:R1_TO_R2, SCARR009|f68r2|S1:E024
- Counterexamples: SCARR045|f73v|S2:E004, f67r2:Q1:0630:R1_TO_R2, SCARR009|f68r2|S1:E024
- Residual: 3856.167 bits; composition 51.667; cycle 0.000
- Survives removal of literal surface identity: True

## Holdout f72 — construction, K=4

### OP01

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START,BARE,BARE,RB:LINE_END;dst=LB:LINE_START,BARE,BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f70, f71, f73, f75, fRos
- Training/held-out support: 58/29
- Examples: fRos:RECORD3:R2_TO_R3, SCARR007|f67v1|X1:E005, SCARR015|f69v|X1:E003
- Counterexamples: fRos:RECORD3:R2_TO_R3, SCARR007|f67v1|X1:E005, SCARR015|f69v|X1:E003
- Residual: 459.333 bits; composition 35.000; cycle 0.000
- Survives removal of literal surface identity: True

### OP02

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> INSERT(dst=BARE) -> KEEP_CORE(src=BOUND_E,BARE,WB,BARE,WB,BARE,RB:LINE_END;dst=BOUND_E,BARE,WB,BARE,WB,BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f70, f71
- Training/held-out support: 45/11
- Examples: f67r2:Q1:0630:R1_TO_R2, SCARR013|f69r|E1:E021, SCARR013|f69r|E1:E019
- Counterexamples: f67r2:Q1:0630:R1_TO_R2, SCARR013|f69r|E1:E021, SCARR013|f69r|E1:E019
- Residual: 1483.667 bits; composition 35.000; cycle 0.000
- Survives removal of literal surface identity: True

### OP03

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> DELETE(src=BARE) -> KEEP_CORE(src=BARE,BARE,RB:LINE_END;dst=BARE,BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f70, f71, f73, f75, fRos
- Training/held-out support: 156/56
- Examples: SCARR042|f73r|S2:E001, SCARR010|f68r3|S1:E002, f67r2:Q1:0830:R2_TO_R3
- Counterexamples: SCARR042|f73r|S2:E001, SCARR010|f68r3|S1:E002, f67r2:Q1:0830:R2_TO_R3
- Residual: 2961.833 bits; composition 35.000; cycle 0.000
- Survives removal of literal surface identity: True

### OP04

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> INSERT(dst=BARE) -> KEEP_CORE(src=BARE,RB:LINE_END;dst=BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f70, f71, f73, f75, fRos
- Training/held-out support: 129/53
- Examples: SCARR045|f73v|S2:E004, SCARR045|f73v|S2:E003, SCARR009|f68r2|S1:E024
- Counterexamples: SCARR045|f73v|S2:E004, SCARR045|f73v|S2:E003, SCARR009|f68r2|S1:E024
- Residual: 2014.833 bits; composition 35.000; cycle 0.000
- Survives removal of literal surface identity: True

## Holdout f73 — construction, K=4

### OP01

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> INSERT(dst=BARE) -> KEEP_CORE(src=BARE,RB:LINE_END;dst=BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f70, f71, f72, f75, fRos
- Training/held-out support: 202/32
- Examples: SCARR009|f68r2|S1:E024, SCARR003|f67r2|M2:E003, SCARR018|f70v2|S2:E017
- Counterexamples: SCARR009|f68r2|S1:E024, SCARR003|f67r2|M2:E003, SCARR018|f70v2|S2:E017
- Residual: 3303.000 bits; composition 85.000; cycle 0.000
- Survives removal of literal surface identity: True

### OP02

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START,BOUND_E;dst=LB:LINE_START,BOUND_E) -> MERGE_BOUNDARY(src=WB) -> KEEP_CORE(src=BARE,RB:LINE_END;dst=BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f70, f71, f72
- Training/held-out support: 75/1
- Examples: SCARR031|f72r3|S1:E008, SCARR010|f68r3|S1:E002, f67r2:Q1:0830:R2_TO_R3
- Counterexamples: SCARR031|f72r3|S1:E008, SCARR010|f68r3|S1:E002, f67r2:Q1:0830:R2_TO_R3
- Residual: 1913.333 bits; composition 85.000; cycle 0.000
- Survives removal of literal surface identity: True

### OP03

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> DELETE(src=BARE) -> KEEP_CORE(src=FREE_R,RB:LINE_END;dst=FREE_R,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f70, f71, f72, f75, fRos
- Training/held-out support: 154/27
- Examples: SCARR036|f72v2|S1:E009, SCARR030|f72r2|S2:E006, SCARR038|f72v1|S1:E010
- Counterexamples: SCARR036|f72v2|S1:E009, SCARR030|f72r2|S2:E006, SCARR038|f72v1|S1:E010
- Residual: 2432.833 bits; composition 85.000; cycle 0.000
- Survives removal of literal surface identity: True

### OP04

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> INSERT(dst=BARE) -> SPLIT_BOUNDARY(dst=WB) -> KEEP_CORE(src=BARE;dst=BARE) -> SPLIT_BOUNDARY(dst=WB) -> KEEP_CORE(src=BARE,RB:LINE_END;dst=BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f70, f71, f72, fRos
- Training/held-out support: 46/0
- Examples: f67r2:Q1:0630:R1_TO_R2, SCARR033|f72r3|S3:E004, SCARR013|f69r|E1:E021
- Counterexamples: f67r2:Q1:0630:R1_TO_R2, SCARR033|f72r3|S3:E004, SCARR013|f69r|E1:E021
- Residual: 1366.833 bits; composition 85.000; cycle 0.000
- Survives removal of literal surface identity: True

## Holdout f75 — construction, K=6

### OP01

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START,BARE,BARE,RB:LINE_END;dst=LB:LINE_START,BARE,BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f70, f71, f72, f73, fRos
- Training/held-out support: 75/4
- Examples: SCARR038|f72v1|S1:E006, SCARR038|f72v1|S1:E013, fRos:RECORD3:R2_TO_R3
- Counterexamples: SCARR038|f72v1|S1:E006, SCARR038|f72v1|S1:E013, fRos:RECORD3:R2_TO_R3
- Residual: 594.000 bits; composition 88.333; cycle 0.000
- Survives removal of literal surface identity: True

### OP02

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> INSERT(dst=BARE) -> KEEP_CORE(src=BARE,RB:LINE_END;dst=BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f70, f71, f72, f73, fRos
- Training/held-out support: 122/2
- Examples: SCARR045|f73v|S2:E004, SCARR003|f67r2|M2:E003, SCARR018|f70v2|S2:E017
- Counterexamples: SCARR045|f73v|S2:E004, SCARR003|f67r2|M2:E003, SCARR018|f70v2|S2:E017
- Residual: 1638.000 bits; composition 88.333; cycle 0.000
- Survives removal of literal surface identity: True

### OP03

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START,BOUND_E;dst=LB:LINE_START,BOUND_E) -> INSERT(dst=BARE) -> SPLIT_BOUNDARY(dst=WB) -> KEEP_CORE(src=BARE,RB:LINE_END;dst=BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f70, f71, f72, fRos
- Training/held-out support: 40/0
- Examples: SCARR033|f72r3|S3:E004, SCARR013|f69r|E1:E021, SCARR004|f67r2|M3:E007
- Counterexamples: SCARR033|f72r3|S3:E004, SCARR013|f69r|E1:E021, SCARR004|f67r2|M3:E007
- Residual: 851.167 bits; composition 88.333; cycle 0.000
- Survives removal of literal surface identity: True

### OP04

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> INSERT(dst=BARE) -> SUBSTITUTE(src=BOUND_E;dst=BARE) -> KEEP_CORE(src=BARE,RB:LINE_END;dst=BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f70, f71, f72, f73, fRos
- Training/held-out support: 50/0
- Examples: f67r2:Q1:0630:R1_TO_R2, SCARR009|f68r2|S1:E024, SCARR008|f68r1|S1:E013
- Counterexamples: f67r2:Q1:0630:R1_TO_R2, SCARR009|f68r2|S1:E024, SCARR008|f68r1|S1:E013
- Residual: 850.667 bits; composition 88.333; cycle 0.000
- Survives removal of literal surface identity: True

### OP05

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> DELETE(src=BARE) -> DELETE(src=BOUND_E) -> KEEP_CORE(src=BARE,WB,BARE;dst=BARE,WB,BARE) -> DELETE(src=BOUND_E) -> KEEP_CORE(src=RB:LINE_END;dst=RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f70, f71, f72
- Training/held-out support: 62/0
- Examples: SCARR036|f72v2|S1:E009, SCARR024|f71v|S1:E009, SCARR012|f68v2|S1:E002
- Counterexamples: SCARR036|f72v2|S1:E009, SCARR024|f71v|S1:E009, SCARR012|f68v2|S1:E002
- Residual: 1950.000 bits; composition 88.333; cycle 0.000
- Survives removal of literal surface identity: True

### OP06

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> DELETE(src=BARE) -> KEEP_CORE(src=FREE_R,RB:LINE_END;dst=FREE_R,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f70, f71, f72, f73, fRos
- Training/held-out support: 178/4
- Examples: SCARR045|f73v|S2:E003, SCARR030|f72r2|S2:E006, SCARR038|f72v1|S1:E010
- Counterexamples: SCARR045|f73v|S2:E003, SCARR030|f72r2|S2:E006, SCARR038|f72v1|S1:E010
- Residual: 2780.500 bits; composition 88.333; cycle 0.000
- Survives removal of literal surface identity: True

## Holdout fRos — construction, K=4

### OP01

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START,FREE_L,RB:LINE_END;dst=LB:LINE_START,FREE_L,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f70, f71, f72, f73, f75
- Training/held-out support: 71/9
- Examples: SCARR045|f73v|S2:E003, SCARR038|f72v1|S1:E006, SCARR007|f67v1|X1:E005
- Counterexamples: SCARR045|f73v|S2:E003, SCARR038|f72v1|S1:E006, SCARR007|f67v1|X1:E005
- Residual: 522.333 bits; composition 35.000; cycle 0.000
- Survives removal of literal surface identity: True

### OP02

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> DELETE(src=BARE) -> KEEP_CORE(src=BARE,BARE,RB:LINE_END;dst=BARE,BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f70, f71, f72, f73, f75
- Training/held-out support: 206/3
- Examples: SCARR036|f72v2|S1:E009, SCARR030|f72r2|S2:E006, SCARR038|f72v1|S1:E010
- Counterexamples: SCARR036|f72v2|S1:E009, SCARR030|f72r2|S2:E006, SCARR038|f72v1|S1:E010
- Residual: 3553.333 bits; composition 35.000; cycle 0.000
- Survives removal of literal surface identity: True

### OP03

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START,BOUND_E;dst=LB:LINE_START,BOUND_E) -> DELETE(src=BARE) -> KEEP_CORE(src=WB;dst=WB) -> DELETE(src=BARE) -> KEEP_CORE(src=BARE,WB,BARE,RB:LINE_END;dst=BARE,WB,BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SKIP_ONE, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f70, f71, f72
- Training/held-out support: 36/1
- Examples: SCARR012|f68v2|S1:E002, SCARR013|f69r|E1:E019, f67r2:Q1:1130:R1_TO_R3
- Counterexamples: SCARR012|f68v2|S1:E002, SCARR013|f69r|E1:E019, f67r2:Q1:1130:R1_TO_R3
- Residual: 1129.000 bits; composition 35.000; cycle 0.000
- Survives removal of literal surface identity: True

### OP04

- Explicit DSL: `KEEP_CORE(src=LB:LINE_START;dst=LB:LINE_START) -> INSERT(dst=BARE) -> KEEP_CORE(src=BARE,BARE,RB:LINE_END;dst=BARE,BARE,RB:LINE_END)`
- Relation types: CYCLIC_SUCCESSOR, ROW_SUCCESSOR
- Training folios: f67, f68, f69, f70, f71, f72, f73, f75
- Training/held-out support: 209/2
- Examples: SCARR045|f73v|S2:E004, f67r2:Q1:0630:R1_TO_R2, SCARR009|f68r2|S1:E024
- Counterexamples: SCARR045|f73v|S2:E004, f67r2:Q1:0630:R1_TO_R2, SCARR009|f68r2|S1:E024
- Residual: 4040.667 bits; composition 35.000; cycle 0.000
- Survives removal of literal surface identity: True

## Ceiling

At most, anonymous formal transformations correspond to author-visible relations and predict held-out panels; no meaning, language, cipher, plaintext, or translation is assigned.
