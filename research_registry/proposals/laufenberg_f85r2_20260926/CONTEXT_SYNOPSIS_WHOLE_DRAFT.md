# IDEA581 whole-scope exploratory draft

**Exact partial.** Two complete ZL scope units (.1 and E), plus the first S clause, are authored. N, the rest of S, W and the final annulus remain unparsed. All156 ZL groups and473 reader rows remain obligations. No translation is confirmed.

## Manual complete unit accounts

### A1 — COMPLETE_ZL_SCOPED_UNIT_HYPOTHESIS

There is a generic thing and a choice of the two sick/healthy recipient contexts such that it is possible for those contexts to differ, the thing to require judgment, young and old to respond differently to cold/heat, and that same thing to benefit one recipient context and harm the other. Bodily natures vary over the year; the seasons differ in nature. Age and seasonal contrasts require judgment.

```json
{
  "op": "ExistsKind",
  "args": [
    "k_H",
    "THING",
    {
      "op": "ExistsPair",
      "args": [
        [
          "c_H0",
          "c_H1"
        ],
        "HEALTH_PAIR",
        {
          "op": "And",
          "args": [
            {
              "op": "Possible",
              "args": [
                {
                  "op": "And",
                  "args": [
                    {
                      "op": "DistinctContexts",
                      "args": [
                        "c_H0",
                        "c_H1"
                      ]
                    },
                    {
                      "op": "InputRequiresJudgment",
                      "args": [
                        "k_H"
                      ]
                    },
                    {
                      "op": "DifferentialResponse",
                      "args": [
                        "AGE_PAIR",
                        "COLD",
                        "HEAT"
                      ]
                    },
                    {
                      "op": "Eval",
                      "args": [
                        "k_H",
                        "c_H0",
                        "GOOD"
                      ]
                    },
                    {
                      "op": "Eval",
                      "args": [
                        "k_H",
                        "c_H1",
                        "HARM"
                      ]
                    }
                  ]
                }
              ]
            },
            {
              "op": "VariesOver",
              "args": [
                "BODILY_NATURES",
                "YEAR"
              ]
            },
            {
              "op": "DifferIn",
              "args": [
                {
                  "op": "Members",
                  "args": [
                    "SEASONS"
                  ]
                },
                "NATURE"
              ]
            },
            {
              "op": "PairRequiresJudgment",
              "args": [
                {
                  "op": "PairUnion",
                  "args": [
                    "AGE_PAIR",
                    "SEASON_PAIR"
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

- Direction between sick/healthy and GOOD/HARM remains existentially unordered.
- The first five propositions share possibility scope; later three assertions are outside it.
- No patient, dose or actual treatment episode is named.

### N — UNRESOLVED

- sain, or, or, aiin, opchdy does not yet have a typed parse. aiin stays SEASONS. A proposed higher-order double-quantifier header was considered but not adopted; no values or rules for it exist in this packet.

### E — COMPLETE_ZL_SCOPED_UNIT_HYPOTHESIS

There is a generic thing and a choice of two distinct temporal contexts such that it is possible for that thing to benefit in the first context, for the yearly cycle to vary, and for the same thing to harm in the second. Temporal contrasts require judgment; young and old differ in responses to cold/heat; seasons require judgment.

```json
{
  "op": "ExistsKind",
  "args": [
    "k_T",
    "THING",
    {
      "op": "ExistsPair",
      "args": [
        [
          "c_T0",
          "c_T1"
        ],
        "TIME_PAIR",
        {
          "op": "Possible",
          "args": [
            {
              "op": "And",
              "args": [
                {
                  "op": "Eval",
                  "args": [
                    "k_T",
                    "c_T0",
                    "GOOD"
                  ]
                },
                {
                  "op": "And",
                  "args": [
                    {
                      "op": "CycleVaries",
                      "args": [
                        "YEAR"
                      ]
                    },
                    {
                      "op": "Eval",
                      "args": [
                        "k_T",
                        "c_T1",
                        "HARM"
                      ]
                    }
                  ]
                },
                {
                  "op": "PairRequiresJudgment",
                  "args": [
                    "TIME_PAIR"
                  ]
                },
                {
                  "op": "DifferentialResponse",
                  "args": [
                    "AGE_PAIR",
                    "COLD",
                    "HEAT"
                  ]
                },
                {
                  "op": "SeasonsRequireJudgment",
                  "args": [
                    "SEASONS"
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

- All five propositions are inside one possibility scope.
- The shared-temporal-input reading is the predeclared uncertain source interpretation.
- The second evaluation incorporates a written context-reference instruction in tchedy; this is a charged lexical compound payload, not a discovered morphological decomposition.
- k_T and k_H are different binders without an asserted equality.

### S — ONE_COMPLETE_INITIAL_CLAUSE_REMAINDER_UNRESOLVED

Young and old differ in their responses across cold and heat.

- No modal/binder opener precedes this first S clause, so it is an unmodalized generic comparison. The rest of S is not parsed or asserted.

### W — UNRESOLVED


### A24 — UNRESOLVED

- ar is PairDesc at every occurrence; no final annular ar/ar repair, aram split or reference cast is assigned.

## Complete ZL interlinear inventory

A value label identifies a hypothesis, not a confirmed gloss. A known value outside a derived span remains unparsed. Unknowns are not dropped.

### f85r2.1

| ID | Literal group | Hypothetical value | Ownership |
|---|---|---|---|
| G001 | `odeedy` | BIND_KIND | A1_OPEN_KIND |
| G002 | `otedy` | THING | A1_OPEN_KIND |
| G003 | `opaees` | BIND_PAIR | A1_OPEN_PAIR |
| G004 | `ar` | HEALTH_PAIR | A1_OPEN_PAIR |
| G005 | `chcthy` | POSSIBLE | A1_OPEN_MODAL |
| G006 | `otchdy` | DISTINCT_CONTEXTS | A1_DIFFER |
| G007 | `otody` | REF_CONTEXT_0 | A1_DIFFER |
| G008 | `otar` | REF_CONTEXT_1 | A1_DIFFER |
| G009 | `chepaiin` | INPUT_REQUIRES_JUDGMENT | A1_JUDGE_INPUT |
| G010 | `otodar` | REF_KIND | A1_JUDGE_INPUT |
| G011 | `otodaiin` | DIFFERENTIAL_RESPONSE | A1_AGE |
| G012 | `opaiin` | AGE_PAIR | A1_AGE |
| G013 | `otaiin` | COLD | A1_AGE |
| G014 | `qopchas` | HEAT | A1_AGE |
| G015 | `otchedy` | APPLY_EVAL | A1_GOOD |
| G016 | `olkaiin` | REF_CONTEXT_0 | A1_GOOD |
| G017 | `odar` | REF_KIND | A1_GOOD |
| G018 | `aloees` | GOOD | A1_GOOD |
| G019 | `otchedy` | APPLY_EVAL | A1_HARM |
| G020 | `qotedaiin` | REF_CONTEXT_1 | A1_HARM |
| G021 | `odar` | REF_KIND | A1_HARM |
| G022 | `octhody` | HARM | A1_HARM |
| G023 | `shedaiin` | CLOSE_MODAL | A1_CLOSE_MODAL |
| G024 | `olaiin` | VARIES_OVER | A1_BODIES_YEAR |
| G025 | `olfor` | BODILY_NATURES | A1_BODIES_YEAR |
| G026 | `daiin` | YEAR | A1_BODIES_YEAR |
| G027 | `ol` | AND | A1_AND |
| G028 | `lkech[ch:?]` | DIFFER_IN | A1_SEASON_NATURE |
| G029 | `os` | MEMBERS | A1_SEASON_NATURE |
| G030 | `aiin` | SEASONS | A1_SEASON_NATURE |
| G031 | `oteedy` | NATURE | A1_SEASON_NATURE |
| G032 | `dar` | PAIR_REQUIRES_JUDGMENT | A1_JUDGE_PAIRS |
| G033 | `otees` | PAIR_UNION | A1_JUDGE_PAIRS |
| G034 | `opaiin` | AGE_PAIR | A1_JUDGE_PAIRS |
| G035 | `chcphdar` | SEASON_PAIR | A1_JUDGE_PAIRS |

### f85r2.2

| ID | Literal group | Hypothetical value | Ownership |
|---|---|---|---|
| G001 | `sain` | **UNKNOWN** | UNPARSED |
| G002 | `or` | **UNKNOWN** | UNPARSED |
| G003 | `or` | **UNKNOWN** | UNPARSED |
| G004 | `aiin` | SEASONS | UNPARSED |
| G005 | `opchdy` | **UNKNOWN** | UNPARSED |

### f85r2.3

| ID | Literal group | Hypothetical value | Ownership |
|---|---|---|---|
| G001 | `qotor` | **UNKNOWN** | UNPARSED |
| G002 | `sheedy` | **UNKNOWN** | UNPARSED |
| G003 | `shodaiin` | **UNKNOWN** | UNPARSED |
| G004 | `olfar` | **UNKNOWN** | UNPARSED |
| G005 | `ary` | **UNKNOWN** | UNPARSED |

### f85r2.4

| ID | Literal group | Hypothetical value | Ownership |
|---|---|---|---|
| G001 | `dair` | **UNKNOWN** | UNPARSED |
| G002 | `sheo` | **UNKNOWN** | UNPARSED |
| G003 | `oraiin` | **UNKNOWN** | UNPARSED |
| G004 | `chol` | **UNKNOWN** | UNPARSED |
| G005 | `daiin` | YEAR | UNPARSED |

### f85r2.5

| ID | Literal group | Hypothetical value | Ownership |
|---|---|---|---|
| G001 | `ockhdar` | **UNKNOWN** | UNPARSED |
| G002 | `olkar` | **UNKNOWN** | UNPARSED |
| G003 | `shoral` | **UNKNOWN** | UNPARSED |

### f85r2.6

| ID | Literal group | Hypothetical value | Ownership |
|---|---|---|---|
| G001 | `roseer` | **UNKNOWN** | UNPARSED |

### f85r2.7

| ID | Literal group | Hypothetical value | Ownership |
|---|---|---|---|
| G001 | `pchedeey` | BIND_KIND | E_OPEN_KIND |
| G002 | `olkey` | THING | E_OPEN_KIND |
| G003 | `qokedy` | BIND_PAIR | E_OPEN_PAIR |
| G004 | `sheos` | TIME_PAIR | E_OPEN_PAIR |
| G005 | `fcheey` | POSSIBLE | E_OPEN_MODAL |

### f85r2.8

| ID | Literal group | Hypothetical value | Ownership |
|---|---|---|---|
| G001 | `otchedy` | APPLY_EVAL | E_GOOD |
| G002 | `chotey` | REF_CONTEXT_0 | E_GOOD |
| G003 | `qocthey` | REF_KIND | E_GOOD |
| G004 | `oteey` | GOOD | E_GOOD |
| G005 | `ol` | AND | E_AND |
| G006 | `oloqorain` | CONJOIN_PREDICATION | E_CONJOIN_HEAD |

### f85r2.9

| ID | Literal group | Hypothetical value | Ownership |
|---|---|---|---|
| G001 | `daiin` | YEAR | E_CYCLE_OPERANDS |
| G002 | `qotaiin` | CYCLE_VARIES | E_CYCLE_OPERANDS |
| G003 | `tchedy` | EVAL_AT_CONTEXT_1 | E_HARM |
| G004 | `otedy` | THING | E_HARM |
| G005 | `qotchdy` | REF_KIND | E_HARM |
| G006 | `chckhey` | HARM | E_HARM |

### f85r2.10

| ID | Literal group | Hypothetical value | Ownership |
|---|---|---|---|
| G001 | `ytchedy` | PAIR_REQUIRES_JUDGMENT | E_JUDGE_TIME |
| G002 | `qodar` | TIME_PAIR | E_JUDGE_TIME |
| G003 | `qotedar` | DIFFERENTIAL_RESPONSE | E_AGE |
| G004 | `qokar` | AGE_PAIR | E_AGE |
| G005 | `qotchd` | COLD | E_AGE |
| G006 | `qotom` | HEAT | E_AGE |

### f85r2.11

| ID | Literal group | Hypothetical value | Ownership |
|---|---|---|---|
| G001 | `soiis` | SEASONS_REQUIRE_JUDGMENT | E_JUDGE_SEASONS |
| G002 | `aiin` | SEASONS | E_JUDGE_SEASONS |
| G003 | `shedaiin` | CLOSE_MODAL | E_CLOSE_MODAL |
| G004 | `chok{co}m` | END_UNIT | E_END |

### f85r2.12

| ID | Literal group | Hypothetical value | Ownership |
|---|---|---|---|
| G001 | `otchs` | DIFFERENTIAL_RESPONSE | S_AGE |
| G002 | `shedor` | AGE_PAIR | S_AGE |
| G003 | `chey` | COLD | S_AGE |
| G004 | `sorain` | HEAT | S_AGE |

### f85r2.13

| ID | Literal group | Hypothetical value | Ownership |
|---|---|---|---|
| G001 | `or` | **UNKNOWN** | UNPARSED |
| G002 | `shedy` | **UNKNOWN** | UNPARSED |
| G003 | `tedy` | **UNKNOWN** | UNPARSED |
| G004 | `sodaiiin` | **UNKNOWN** | UNPARSED |
| G005 | `chy` | **UNKNOWN** | UNPARSED |

### f85r2.14

| ID | Literal group | Hypothetical value | Ownership |
|---|---|---|---|
| G001 | `ytedar` | **UNKNOWN** | UNPARSED |
| G002 | `chz[s:r]` | **UNKNOWN** | UNPARSED |
| G003 | `aiin` | SEASONS | UNPARSED |
| G004 | `arody` | **UNKNOWN** | UNPARSED |

### f85r2.15

| ID | Literal group | Hypothetical value | Ownership |
|---|---|---|---|
| G001 | `ypshedy` | **UNKNOWN** | UNPARSED |
| G002 | `dar` | PAIR_REQUIRES_JUDGMENT | UNPARSED |
| G003 | `chedy` | **UNKNOWN** | UNPARSED |
| G004 | `or` | **UNKNOWN** | UNPARSED |
| G005 | `am` | **UNKNOWN** | UNPARSED |

### f85r2.16

| ID | Literal group | Hypothetical value | Ownership |
|---|---|---|---|
| G001 | `oteey` | GOOD | UNPARSED |
| G002 | `qodaiin` | **UNKNOWN** | UNPARSED |
| G003 | `odain` | **UNKNOWN** | UNPARSED |
| G004 | `an` | **UNKNOWN** | UNPARSED |
| G005 | `chey` | COLD | UNPARSED |

### f85r2.17

| ID | Literal group | Hypothetical value | Ownership |
|---|---|---|---|
| G001 | `orar` | **UNKNOWN** | UNPARSED |
| G002 | `oldar` | **UNKNOWN** | UNPARSED |
| G003 | `ain` | **UNKNOWN** | UNPARSED |

### f85r2.18

| ID | Literal group | Hypothetical value | Ownership |
|---|---|---|---|
| G001 | `okees` | **UNKNOWN** | UNPARSED |
| G002 | `olaiin` | VARIES_OVER | UNPARSED |
| G003 | `qokal` | **UNKNOWN** | UNPARSED |
| G004 | `chdy` | **UNKNOWN** | UNPARSED |
| G005 | `sary` | **UNKNOWN** | UNPARSED |

### f85r2.19

| ID | Literal group | Hypothetical value | Ownership |
|---|---|---|---|
| G001 | `qokshedy` | **UNKNOWN** | UNPARSED |
| G002 | `qodain` | **UNKNOWN** | UNPARSED |
| G003 | `chckhy` | **UNKNOWN** | UNPARSED |
| G004 | `ykeedy` | **UNKNOWN** | UNPARSED |
| G005 | `chedy` | **UNKNOWN** | UNPARSED |

### f85r2.20

| ID | Literal group | Hypothetical value | Ownership |
|---|---|---|---|
| G001 | `or` | **UNKNOWN** | UNPARSED |
| G002 | `aiin` | SEASONS | UNPARSED |
| G003 | `ckhed[a:y]` | **UNKNOWN** | UNPARSED |
| G004 | `or` | **UNKNOWN** | UNPARSED |
| G005 | `ain` | **UNKNOWN** | UNPARSED |
| G006 | `olchey` | **UNKNOWN** | UNPARSED |
| G007 | `qokal` | **UNKNOWN** | UNPARSED |
| G008 | `shedy` | **UNKNOWN** | UNPARSED |

### f85r2.21

| ID | Literal group | Hypothetical value | Ownership |
|---|---|---|---|
| G001 | `qokeody` | **UNKNOWN** | UNPARSED |
| G002 | `qoekedy` | **UNKNOWN** | UNPARSED |
| G003 | `dody` | **UNKNOWN** | UNPARSED |
| G004 | `shedy` | **UNKNOWN** | UNPARSED |
| G005 | `qodaiin` | **UNKNOWN** | UNPARSED |

### f85r2.22

| ID | Literal group | Hypothetical value | Ownership |
|---|---|---|---|
| G001 | `los` | **UNKNOWN** | UNPARSED |
| G002 | `ar` | HEALTH_PAIR | UNPARSED |
| G003 | `shedy` | **UNKNOWN** | UNPARSED |
| G004 | `qokshey` | **UNKNOWN** | UNPARSED |
| G005 | `qose?y` | **UNKNOWN** | UNPARSED |
| G006 | `or` | **UNKNOWN** | UNPARSED |
| G007 | `aiin` | SEASONS | UNPARSED |
| G008 | `og` | **UNKNOWN** | UNPARSED |

### f85r2.23

| ID | Literal group | Hypothetical value | Ownership |
|---|---|---|---|
| G001 | `ol` | AND | UNPARSED |
| G002 | `lcheol` | **UNKNOWN** | UNPARSED |
| G003 | `chol` | **UNKNOWN** | UNPARSED |
| G004 | `ol` | AND | UNPARSED |
| G005 | `sheoly` | **UNKNOWN** | UNPARSED |

### f85r2.24

| ID | Literal group | Hypothetical value | Ownership |
|---|---|---|---|
| G001 | `okees` | **UNKNOWN** | UNPARSED |
| G002 | `ochar` | **UNKNOWN** | UNPARSED |
| G003 | `oted[o:a]r` | **UNKNOWN** | UNPARSED |
| G004 | `ochedy` | **UNKNOWN** | UNPARSED |
| G005 | `otody` | REF_CONTEXT_0 | UNPARSED |
| G006 | `olchedy` | **UNKNOWN** | UNPARSED |
| G007 | `oteedo` | **UNKNOWN** | UNPARSED |
| G008 | `ar` | HEALTH_PAIR | UNPARSED |
| G009 | `or` | **UNKNOWN** | UNPARSED |
| G010 | `airol` | **UNKNOWN** | UNPARSED |
| G011 | `otees` | PAIR_UNION | UNPARSED |
| G012 | `ar` | HEALTH_PAIR | UNPARSED |
| G013 | `aram` | **UNKNOWN** | UNPARSED |

## Manual derivation spans

- **A1_OPEN_KIND** (`f85r2.1` G001–G002): BIND_KIND(THING): bind k_H; no assertion yet.
- **A1_OPEN_PAIR** (`f85r2.1` G003–G004): BIND_PAIR(HEALTH_PAIR): bind c_H0,c_H1; no assertion yet.
- **A1_OPEN_MODAL** (`f85r2.1` G005–G005): Open POSSIBLE; body begins at G006.
- **A1_DIFFER** (`f85r2.1` G006–G008): DISTINCT_CONTEXTS(REF_CONTEXT_0,REF_CONTEXT_1) -> DistinctContexts(c_H0,c_H1).
- **A1_JUDGE_INPUT** (`f85r2.1` G009–G010): INPUT_REQUIRES_JUDGMENT(REF_KIND) -> InputRequiresJudgment(k_H).
- **A1_AGE** (`f85r2.1` G011–G014): DIFFERENTIAL_RESPONSE(AGE_PAIR,COLD,HEAT).
- **A1_GOOD** (`f85r2.1` G015–G018): APPLY_EVAL(REF_CONTEXT_0,REF_KIND,GOOD) -> Eval(k_H,c_H0,GOOD).
- **A1_HARM** (`f85r2.1` G019–G022): APPLY_EVAL(REF_CONTEXT_1,REF_KIND,HARM) -> Eval(k_H,c_H1,HARM).
- **A1_CLOSE_MODAL** (`f85r2.1` G023–G023): CLOSE_MODAL returns possibility of all five preceding body clauses; Kind/pair binders stay open.
- **A1_BODIES_YEAR** (`f85r2.1` G024–G026): VARIES_OVER(BODILY_NATURES,YEAR).
- **A1_AND** (`f85r2.1` G027–G027): Infix AND joins G024–26 with G028–31; no gap.
- **A1_SEASON_NATURE** (`f85r2.1` G028–G031): DIFFER_IN(MEMBERS(SEASONS),NATURE).
- **A1_JUDGE_PAIRS** (`f85r2.1` G032–G035): PAIR_REQUIRES_JUDGMENT(PAIR_UNION(AGE_PAIR,SEASON_PAIR)); layout then closes the two binders.
- **E_OPEN_KIND** (`f85r2.7` G001–G002): BIND_KIND(THING): bind k_T.
- **E_OPEN_PAIR** (`f85r2.7` G003–G004): BIND_PAIR(TIME_PAIR): bind c_T0,c_T1.
- **E_OPEN_MODAL** (`f85r2.7` G005–G005): Open POSSIBLE.
- **E_GOOD** (`f85r2.8` G001–G004): APPLY_EVAL(REF_CONTEXT_0,REF_KIND,GOOD) -> Eval(k_T,c_T0,GOOD).
- **E_AND** (`f85r2.8` G005–G005): Infix AND; right operand starts G006 and continues through .9 G006.
- **E_CONJOIN_HEAD** (`f85r2.8` G006–G006): CONJOIN_PREDICATION awaits YEAR, CYCLE_VARIES as a function value, and the complete second evaluation.
- **E_CYCLE_OPERANDS** (`f85r2.9` G001–G002): YEAR and CYCLE_VARIES are the first two written operands of CONJOIN_PREDICATION.
- **E_HARM** (`f85r2.9` G003–G006): EVAL_AT_CONTEXT_1(CheckedRef(THING,REF_KIND),HARM) -> Eval(k_T,c_T1,HARM); same binder k_T.
- **E_JUDGE_TIME** (`f85r2.10` G001–G002): PAIR_REQUIRES_JUDGMENT(TIME_PAIR).
- **E_AGE** (`f85r2.10` G003–G006): DIFFERENTIAL_RESPONSE(AGE_PAIR,COLD,HEAT).
- **E_JUDGE_SEASONS** (`f85r2.11` G001–G002): SEASONS_REQUIRE_JUDGMENT(SEASONS).
- **E_CLOSE_MODAL** (`f85r2.11` G003–G003): Close the single POSSIBLE scope after all five body clauses.
- **E_END** (`f85r2.11` G004–G004): END_UNIT closes pair/Kind binders, only at the actual end of E.
- **S_AGE** (`f85r2.12` G001–G004): DIFFERENTIAL_RESPONSE(AGE_PAIR,COLD,HEAT), with no preceding modal scope in S.

## All reader consequences

The JSON contains all473 original native rows with every source field preserved, exact-string binding or UNKNOWN, and a separate parse-status field. Alternate rows are not normalized or treated as independent evidence. No complete IT/RF AST is asserted.

## Exact alternate gaps in the authored units

- **IT2a A1**: `IT2a|f85r2.1|G001` = `odchdy`, `IT2a|f85r2.1|G003` = `opoees`, `IT2a|f85r2.1|G010` = `otadar`, `IT2a|f85r2.1|G012` = `opoiin`, `IT2a|f85r2.1|G014` = `qopchchs`, `IT2a|f85r2.1|G028` = `lkech?`, `IT2a|f85r2.1|G034` = `ofaiin`. No complete alternate unit AST is asserted.
- **IT2a E**: `IT2a|f85r2.8|G006` = `oloeorain`, `IT2a|f85r2.10|G001` = `qtchedy`, `IT2a|f85r2.11|G004` = `chokcod`. No complete alternate unit AST is asserted.
- **IT2a S12**: no unknown literal in this local span. No complete alternate unit AST is asserted.
- **RF1b A1**: `RF1b|f85r2.1|G001` = `odee@152;y`, `RF1b|f85r2.1|G003` = `opoees`, `RF1b|f85r2.1|G007` = `oto@152;y`, `RF1b|f85r2.1|G010` = `ot@221;dar`, `RF1b|f85r2.1|G015` = `otche@152;y`, `RF1b|f85r2.1|G028` = `lkechch`, `RF1b|f85r2.1|G030` = `@221;iin`, `RF1b|f85r2.1|G034` = `ofaiin`, `RF1b|f85r2.1|G035` = `chcph@152;ar`. No complete alternate unit AST is asserted.
- **RF1b E**: `RF1b|f85r2.7|G003` = `qoke@152;y`, `RF1b|f85r2.7|G004` = `{ch'}eos`, `RF1b|f85r2.8|G001` = `otche@152;y`, `RF1b|f85r2.9|G004` = `ote@152;y`, `RF1b|f85r2.10|G002` = `qo@152;ar`, `RF1b|f85r2.11|G004` = `chot{co}g`. No complete alternate unit AST is asserted.
- **RF1b S12**: no unknown literal in this local span. No complete alternate unit AST is asserted.

IT .1 G007 is a separate fixed-template problem: `otedy` is KindDesc, whereas the preceding `otchdy` requires ContextRef. This is not an alias or a global all-grammar rejection. S.12 is the same four-group local span across readers; that agreement is one manuscript, not independent evidence.

## All assigned whole values and interfaces

Every row is hypothetical. Synonyms are free whole assignments, never normalized alternate spellings.

| Literal form | Type | Meaning | Stage |
|---|---|---|---|
| `odeedy` | `BinderHead[KindDesc]` | Existentially bind a generic kind satisfying the following descriptor. | contract |
| `otedy` | `KindDesc` | Unrestricted generic evaluated-kind descriptor. | contract |
| `opaees` | `BinderHead[PairDesc]` | Existentially bind an ordered pair satisfying the following description. | contract |
| `ar` | `PairDesc` | Unordered sick/healthy recipient-class pair; no fixed clinical direction. | contract |
| `chcthy` | `ModalHead` | Joint possibility of its scoped proposition. | contract |
| `otchedy` | `ContextRef -> KindRef -> Outcome -> Atom` | Resolve the two explicit references and evaluate the same kind in that context with the written outcome. | contract |
| `olkaiin` | `ContextRef` | First slot of nearest overt pair binder. | contract |
| `qotedaiin` | `ContextRef` | Second slot of nearest overt pair binder. | contract |
| `odar` | `KindRef` | Kind of nearest overt Kind binder. | contract |
| `aloees` | `Outcome` | Beneficial health response, not merely absence of harm. | contract |
| `octhody` | `Outcome` | Harmful health response, not merely absence of benefit. | contract |
| `otchdy` | `ContextRef -> ContextRef -> Atom` | The explicitly resolved contexts differ. | new |
| `otody` | `ContextRef` | First slot of nearest overt pair binder; an independently guessed synonym, not normalization. | new |
| `otar` | `ContextRef` | Second slot of nearest overt pair binder; an independently guessed synonym. | new |
| `chepaiin` | `KindRef -> Atom` | The resolved generic input requires judgment; the judgment faculty is lexical content, not an implicit patient. | new |
| `otodar` | `KindRef` | Kind of nearest overt Kind binder; separately guessed reference spelling. | new |
| `otodaiin` | `PairDesc -> ThermalCondition -> ThermalCondition -> Atom` | Members of the supplied pair differ in response profiles across the two supplied thermal conditions. | new |
| `opaiin` | `PairDesc` | Unordered pair of young/old life-stage contexts tagged as AtTime. | new |
| `otaiin` | `ThermalCondition` | Cold as an environmental condition, without a treatment or age polarity. | new |
| `qopchas` | `ThermalCondition` | Heat as an environmental condition, without a treatment or age polarity. | new |
| `shedaiin` | `ModalCloser` | Close the nearest explicit open modal scope; do not close kind/pair binders. | new |
| `olaiin` | `NaturalAspect -> TimeCycle -> Atom` | The supplied collective natural aspect varies over the supplied temporal cycle. | new |
| `olfor` | `NaturalAspect` | Collective bodily natures, without a persisting individual. | new |
| `daiin` | `TimeCycle` | The generic yearly cycle, not a dated year or particular episode. | new |
| `ol` | `Prop -> Prop -> Prop` | Explicit infix conjunction of complete propositions. | new |
| `lkech[ch:?]` | `ComparisonDomain -> Aspect -> Atom` | The members of the supplied comparison domain differ in the supplied aspect; generic, undirected. | new |
| `os` | `SeasonDomain -> ComparisonDomain` | Members of the supplied seasonal domain as a comparison domain. | new |
| `aiin` | `SeasonDomain` | The generic seasons as a domain; no picture ownership or number code. | new |
| `oteedy` | `Aspect` | Nature or constitution as an aspect of comparison, not an individual constitution. | new |
| `dar` | `PairDesc -> Atom` | The contrasts described by the supplied pair restriction require judgment. | new |
| `otees` | `PairDesc -> PairDesc -> PairDesc` | Disjunction of two pair restrictions: lambda c0,c1. P(c0,c1) OR Q(c0,c1). | new |
| `chcphdar` | `PairDesc` | Any unequal pair of seasonal TimeSituations, both tagged AtTime. | new |
| `pchedeey` | `BinderHead[KindDesc]` | A separately guessed spelling of the Kind binder. | new |
| `olkey` | `KindDesc` | A separately guessed unrestricted generic-kind descriptor. | new |
| `qokedy` | `BinderHead[PairDesc]` | A separately guessed spelling of the pair binder. | new |
| `sheos` | `PairDesc` | Any two distinct AtTime contexts; no concrete dates, shared person, or observed episodes. | new |
| `fcheey` | `ModalHead` | A separately guessed possibility marker with the same scope law. | new |
| `chotey` | `ContextRef` | First bound context slot. | new |
| `qocthey` | `KindRef` | Current bound generic kind. | new |
| `oteey` | `Outcome` | A separately guessed GOOD outcome word. | new |
| `oloqorain` | `TimeCycle -> (TimeCycle -> Atom) -> Prop -> Prop` | Given y, P, Q, form P(y) AND Q. Subject and predicate are both written operands. | new |
| `qotaiin` | `TimeCycle -> Atom` | The supplied cycle is variable in its conditions; no actual dated cycle. | new |
| `tchedy` | `KindRef -> Outcome -> Atom` | Explicit lexical partial application of APPLY_EVAL to REF_CONTEXT_1; still requires written kind reference and outcome. | new |
| `qotchdy` | `KindRef` | Current bound generic kind; another independently guessed reference spelling. | new |
| `chckhey` | `Outcome` | A separately guessed HARM outcome word. | new |
| `ytchedy` | `PairDesc -> Atom` | Same pair-judgment predicate, separately guessed whole value. | new |
| `qodar` | `PairDesc` | Same unequal temporal-context pair restriction, separately guessed whole value. | new |
| `qotedar` | `PairDesc -> ThermalCondition -> ThermalCondition -> Atom` | Same undirected response-profile comparison, separately guessed whole value. | new |
| `qokar` | `PairDesc` | Same young/old life-stage pair restriction, separately guessed whole value. | new |
| `qotchd` | `ThermalCondition` | Same cold condition, separately guessed whole value. | new |
| `qotom` | `ThermalCondition` | Same heat condition, separately guessed whole value. | new |
| `soiis` | `SeasonDomain -> Atom` | The supplied seasonal domain requires contextual judgment. | new |
| `chok{co}m` | `ScopeEnd` | Explicitly close/check all remaining binder scopes at the current unit end; no proposition content. | new |
| `otchs` | `PairDesc -> ThermalCondition -> ThermalCondition -> Atom` | Same undirected response comparison, used outside any modal scope at S start. | new |
| `shedor` | `PairDesc` | Same young/old life-stage pair restriction. | new |
| `chey` | `ThermalCondition` | Same cold condition; its S.16 recurrence remains a typed obligation. | new |
| `sorain` | `ThermalCondition` | Same heat condition. | new |

## Five added productions

**R10 Finite typed prefix application.** A declared non-binder function consumes its required immediately following typed expressions in declared curried order. Functions explicitly required as arguments remain function values. This is typed application, not implicit conversion or reordering. APPLY_EVAL retains R2 exactly.

**R11 Explicit infix AND.** Prop ol Prop forms AND of the immediately adjacent complete propositions at the same active scope. It does not join incomplete spans, close scopes, or turn a noun/reference into a proposition.

**R12 Written modal closer.** shedaiin closes the nearest overt active modal head and returns POSSIBLE(conjunction of that completed body) as a Prop in the containing scope. It consumes no unknown body and does not close Kind/pair scopes. Unmatched use fails this production. This instantiates R4's prospectively allowed explicit closer, only after both selected health applications.

**R13 Descriptor-checked KindRef.** KindDesc D followed by KindRef r can form CheckedRef(D,r):KindRef only in an argument slot explicitly requiring KindRef. Resolution uses exactly resolve(r), with D(resolve(r)) as a side condition in the enclosing scope. It introduces no new kind and is not a KindDesc-to-Kind cast. Here THING is unrestricted and its test is trivially satisfied; that fact does not identify a concrete thing.

**R14 Explicit unit end.** END_UNIT is legal only as the last token of a fixed scope unit with every remaining body complete. It closes all remaining binders by R8, then the layout boundary has no remaining open scopes. No proposition is supplied by the marker; it cannot repair an incomplete body.


Frozen 2026-09-27 05:26:06 UTC. The packet remains an exact partial and will not be edited after handoff.
