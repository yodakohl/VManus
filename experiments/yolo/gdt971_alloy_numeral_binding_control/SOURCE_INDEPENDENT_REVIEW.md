# GDT971 independent source review

**Scope:** source-only validation of the five final numerical accounts in Liber abbaci XI.6, Boncompagni 1857, printed pp.152–154 (cached render pages 159–161). No Voynich text/image, reserve, or target was accessed.

## Source receipt

- Registered source: `https://archive.org/download/bub_gb_CrdUBgtAZFoC/bub_gb_CrdUBgtAZFoC.pdf`
- Declared PDF SHA-256: `e0617041071d181ae61a5109fc21ad48b8503927ed9f8f2a1378575de797ed1a`
- Existing renders independently viewed: `abaci-159.png`, `abaci-160.png`, `abaci-161.png`; each 1606×2200.
- Render SHA-256: page 159 `f28a569d4cead306a4c78377010fd95ff27419dd498dcc576a7ac543bf51a5c8`; page 160 `68890d859ebf5b0db09423bc5ebc8d91ef7d311c393a78341b2cdfcec3558b85`; page 161 `3c20175c4394c09420bb46e540d23781a5f87d980040d9af50005399ef1e79ba`.

The renders show the relevant printed account diagrams and prose. The contract's source checks are: silver totals 25 and 80 on printed p.153, 100 on p.154; the mixed quantities are written as `2 + 1/2`, `6 + 1/4`, and `11 + 1/4`. The value 400 is computed in the fixed-first-10 discussion and is excluded; the scaled path's computed 100 is likewise not a separate written check. Number words/intermediates/full prose are excluded.

## Independent reconstruction

A printed digit `d` maps to the numeric digit `p[d]` under each of all 10! permutations in lexicographic order. Every multi-digit number rejects a mapped leading zero. Exact `Fraction` arithmetic is used for mixed quantities. All three component grades are the mapped values of printed 3, 4, and 6; desired grade is mapped printed 5. For each account the validator checks the weighted fine-content sum against mass × desired grade, plus only the written check where the source explicitly supplies one.

| Layer | Added obligation |
|---|---|
| L0 | positivity of every declared literal number and no mapped leading zero |
| L1 (Q) | alternative 20-unit path, weights 2/7/11, mass 20, written silver check 100 |
| L2 (Q+P) | add the complete mixed path 2+1/2, 6+1/4, 11+1/4 and common desired grade |
| L3 (Q+P+A+B+D) | add A weights 1/1/3, mass 5, check 25; B weights 2/5/9, mass 16, check 80; D weights 10/25/45 with computed mass only |

No standalone `N(0)`, fixed numeral 1, improper-fraction substitute, grade-order gate, or proper-mixed-fraction gate is introduced. The independent algorithm is in `src/validate.py`; default execution is registration-only and does not read `src/run.py` or `artifacts/RESULT.json`. `--full` is reserved until the public primary result is available, and performs the complete enumeration before opening that result.

The free-label diagnostic is also reconstructed independently: grades 3/4/7, target 5, paths (1,12,7) and (5,20/3,25/3). It is a countermodel to arbitrary independent content labels, not a source claim and not a Voynich result.

## Pre-enumeration correction

The initial validator draft omitted the explicit requirement that each prescribed
mass equal the sum of its component weights. This was corrected before any
primary result was opened; `account()` now checks `sum(weights) == mass` for
A, B, P and Q (D uses its declared computed sum). The first draft also used a
private absolute temporary-cache path for render verification. The stable validator now
stores only the registered render names, hashes and dimensions; `--source-dir`
is an optional local reinspection path and is not required for reproduction.
This is an implementation correction, not a source discrepancy.

## Claim ceiling

Even a complete agreement with the primary enumeration would validate only the frozen arithmetic contract and its conditional digit-binding consequences. It would not identify the source's language, recover a writing system, or confirm any target meaning. Any mismatch must be reported as a source projection, schema, or implementation discrepancy before interpreting the scientific result.

Root pre-enumeration review also added registered-hash verification, complete
candidate-table/status/identity checks and a nonzero exit on mismatch. The
independently constructed numerical predicates and enumeration are unchanged.
