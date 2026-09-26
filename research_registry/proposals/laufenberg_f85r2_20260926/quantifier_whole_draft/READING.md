# IDEA000558 — complete group accounting, incomplete semantic closure

**All-token gloss draft; typed/source completion remains unresolved.** This
is an exploratory source-constrained hypothesis, not a translation or a
completed semantic test. All 156 ZL groups and 115 raw types are accounted for.
The fixed seed keeps every or as ALL, every aiin as the Person domain, and
every ain as the Treatment domain.

[Assumptions and limits](ASSUMPTIONS.md) and [source coverage](SOURCE_COVERAGE.json)
are part of the reading, not optional caveats. [All occurrences](ALL_OCCURRENCES.json)
preserve marks and separators; [alternate gaps](ALTERNATE_GAPS.json) remain separate.

## N

### N2

| Exact group | Fixed candidate gloss |
|---|---|
| `sain` | the four elements |
| `or` | all |
| `or` | all |
| `aiin` | human persons |
| `opchdy` | is a component of |

Candidate: Every one of the four elements is a component of every person.

Formula: `forall e in E forall p in P COMPONENT(e,p)`.

### N3

| Exact group | Fixed candidate gloss |
|---|---|
| `qotor` | human nature |
| `sheedy` | fourfold |
| `shodaiin` | analogous to |
| `olfar` | year |
| `ary` | four divisions |

Candidate: Human nature is fourfold, analogously to the year’s four divisions.

Formula: `FOURFOLD(HumanNature) & ANALOGOUS_TO(HumanNature,PARTITION(Year,4)); HumanNature and Year retain different sorts`.

### N4

| Exact group | Fixed candidate gloss |
|---|---|
| `dair` | predominance |
| `sheo` | grounds |
| `oraiin` | inclination |
| `chol` | and |
| `daiin` | constitution |

Candidate: Predominance grounds inclination and constitution.

Formula: `GROUNDS(PredominanceAttribute,InclinationAttribute) & GROUNDS(PredominanceAttribute,ConstitutionAttribute)`.

**Unresolved:** Schema-level relation between attributes; no individual patient is supplied. Pointwise human-owner interpretation needs acceptance of G11.

### N56

| Exact group | Fixed candidate gloss |
|---|---|
| `ockhdar` | different |
| `olkar` | elements |
| `shoral` | predominates in |
| `roseer` | persons |

Candidate: Different elements predominate in different persons.

Formula: `PROPOSED_DISTRIBUTION: forall e in E exists p in P PREDOMINATES(e,p); differing strict dominant elements may have different owners; not EXCLUSIVE_COMPONENT(e,p)`.

**Unresolved:** The each-element/existing-person distribution is an added scope choice, not licensed by the fixed ALL frames. Literal word DIFFERENT alone does not establish it.

## W

### W18

| Exact group | Fixed candidate gloss |
|---|---|
| `okees` | regimen |
| `olaiin` | persons |
| `qokal` | relative to |
| `chdy` | inclination |
| `sary` | constitutional |

Candidate: The regimen of persons is relative to constitutional inclination.

Formula: `RELEVANT_CRITERION(ConstitutionalInclination,IMAGE(Regimen,P))`.

**Unresolved:** Nominal datum + criterion frame G12, and image-domain application G08, are added interpretations; relevance does not assert that any particular treatment succeeds.

### W19

| Exact group | Fixed candidate gloss |
|---|---|
| `qokshedy` | constitution names |
| `qodain` | arise from |
| `chckhy` | predominant |
| `ykeedy` | elements |
| `chedy` | contribution |

Candidate: Constitution names arise from the predominant elemental contribution.

Formula: `ARISE_FROM(ConstitutionNameDomain,PredominantElementContributionAttribute)`.

**Unresolved:** Attribute/domain relation is schematic; no individual owner or exact names are supplied.

### W20

| Exact group | Fixed candidate gloss |
|---|---|
| `or` | all |
| `aiin` | human persons |
| `ckhed[a:y]` | is benefited by |
| `or` | all |
| `ain` | candidate treatments |
| `olchey` | not |
| `qokal` | relative to |
| `shedy` | constitutions |

Candidate: Not every treatment benefits every person; constitution is a relevant criterion.

Formula: `P0 = NOT(forall p in P forall t in T BENEFIT(p,t)); PROPOSED_TAIL = P0 & RELEVANT_CRITERION(C,P0)`.

**Unresolved:** First six groups retain the exact raw proposition. qokal shedy is not discarded. Whether a criterion-domain can modify that completed proposition as G12 proposes remains an explicit source/type audit obligation.

### W21

| Exact group | Fixed candidate gloss |
|---|---|
| `qokeody` | conduct |
| `qoekedy` | voluntary |
| `dody` | may |
| `shedy` | constitutions |
| `qodaiin` | goes against |

Candidate: Voluntary conduct may run contrary to constitution.

Formula: `WEAK_MODAL_CANDIDATE: POSSIBLE(COUNTER_TO(VoluntaryConduct,ConstitutionDomain)); no forall-person ability or achieved change follows`.

**Unresolved:** The source’s fine agency/scope syntax is uncertain. This remains a weak possibility schema between concepts; no individual actor is identified or inserted.

### W22a

| Exact group | Fixed candidate gloss |
|---|---|
| `los` | names |
| `ar` | and |
| `shedy` | constitutions |
| `qokshey` | follow |
| `qose?y` | predominance |

Candidate: Names and constitutions follow predominance.

Formula: `FOLLOW(NameDomain,PredominanceAttribute) & FOLLOW(ConstitutionDomain,PredominanceAttribute)`.

**Unresolved:** Added schema-level relation; a pointwise naming rule is not independently bound.

### W22b23

| Exact group | Fixed candidate gloss |
|---|---|
| `or` | all |
| `aiin` | human persons |
| `og` | nevertheless |
| `ol` | is |
| `lcheol` | mixed |
| `chol` | and |
| `ol` | is |
| `sheoly` | inclined |

Candidate: Every person nevertheless is mixed and has an inclination.

Formula: `forall p in P (MIXED(p) & INCLINED(p)); NEVERTHELESS contrasts common membership with the preceding predominance schema`.

## E

### E7

| Exact group | Fixed candidate gloss |
|---|---|
| `pchedeey` | share |
| `olkey` | of |
| `qokedy` | elements |
| `sheos` | vary among |
| `fcheey` | persons |

Candidate: The shares of the elements vary among persons.

Formula: `exists e in E exists p,q in P SHARE(e,p) != SHARE(e,q)`.

### E8a

| Exact group | Fixed candidate gloss |
|---|---|
| `otchedy` | supplies |
| `chotey` | air |
| `qocthey` | breath |

Candidate: Air supplies breath.

Formula: `SUPPLIES(AIR,BREATH)`.

### E8b

| Exact group | Fixed candidate gloss |
|---|---|
| `oteey` | cold |
| `ol` | is |
| `oloqorain` | opposing heat |

Candidate: Cold is opposed to heat.

Formula: `COUNTER_TO(COLD,HEAT)`.

### E9

| Exact group | Fixed candidate gloss |
|---|---|
| `daiin` | constitution |
| `qotaiin` | depends |
| `tchedy` | within |
| `otedy` | living bodies |
| `qotchdy` | on |
| `chckhey` | predominance |

Candidate: Within living bodies, constitution depends on predominance.

Formula: `DEPENDENCE(ConstitutionAttribute,PredominanceAttribute; owner_domain=LivingBodies)`.

**Unresolved:** The source speaks of living things’ complex/nature and human complexions. Extending the same ConstitutionAttribute schema to the whole LivingBody domain needs source review; no species or organ is invented.

### E10a

| Exact group | Fixed candidate gloss |
|---|---|
| `ytchedy` | dryness |
| `qodar` | opposes |
| `qotedar` | moisture |

Candidate: Dryness is opposed to moisture.

Formula: `COUNTER_TO(DRYNESS,MOISTURE)`.

### E10b

| Exact group | Fixed candidate gloss |
|---|---|
| `qokar` | conflict |
| `qotchd` | can cause |
| `qotom` | harm |

Candidate: Conflict can cause harm.

Formula: `POSSIBLE(CAUSE(CONFLICT,HARM))`.

### E11

| Exact group | Fixed candidate gloss |
|---|---|
| `soiis` | composition |
| `aiin` | human persons |
| `shedaiin` | of |
| `chok{co}m` | elements |

Candidate: Persons’ composition is of the elements.

Formula: `COMPOSITION_DOMAIN(P,E)`.

**Unresolved:** This is a proposed domain-level composition frame, not a replacement of aiin by an individual. Its relationship to pointwise composition is not derived from the fixed seed grammar. N2 already independently states the candidate all-element/all-person clause.

## S

### S12

| Exact group | Fixed candidate gloss |
|---|---|
| `otchs` | conflict |
| `shedor` | can cause |
| `chey` | harm |
| `sorain` | death |

Candidate: Conflict can cause harm and death.

Formula: `POSSIBLE(CAUSE(CONFLICT,HARM)) & POSSIBLE(CAUSE(CONFLICT,DEATH))`.

### S13

| Exact group | Fixed candidate gloss |
|---|---|
| `or` | all |
| `shedy` | constitutions |
| `tedy` | inclines |
| `sodaiiin` | toward |
| `chy` | predominant element |

Candidate: Every constitution inclines toward its predominant element.

Formula: `forall c in C INCLINES_TOWARD(c,PREDOMINANT_ELEMENT(c))`.

**Unresolved:** An explicit owner quantifier is present, but the attribute PredominantElement(c) is a new derived term; the source principally describes persons bearing that inclination.

### S14

| Exact group | Fixed candidate gloss |
|---|---|
| `ytedar` | constitutions |
| `chz[s:r]` | classifies |
| `aiin` | human persons |
| `arody` | four ways |

Candidate: Constitutions classify persons in four ways.

Formula: `CLASSIFICATION(P,C) & CARDINALITY(C)=4`.

### S15

| Exact group | Fixed candidate gloss |
|---|---|
| `ypshedy` | human mixture |
| `dar` | from |
| `chedy` | contribution |
| `or` | all |
| `am` | elements |

Candidate: Human mixture derives from the contribution of every element.

Formula: `forall e in E FROM(HumanMixture,CONTRIBUTION(e))`.

### S16

| Exact group | Fixed candidate gloss |
|---|---|
| `oteey` | cold |
| `qodaiin` | goes against |
| `odain` | heat |
| `an` | can cause |
| `chey` | harm |

Candidate: Cold contending with heat can cause harm.

Formula: `POSSIBLE(CAUSE(CONFLICT_EVENT(COLD,HEAT),HARM))`.

**Unresolved:** G14 reifies the opposition as a conflict event. It must not equate mere co-presence of opposite qualities with an actual harmful conflict.

### S17

| Exact group | Fixed candidate gloss |
|---|---|
| `orar` | constitution |
| `oldar` | guides |
| `ain` | candidate treatments |

Candidate: Constitution guides treatment.

Formula: `GUIDES_SELECTION(ConstitutionAttribute,TreatmentDomain)`.

**Unresolved:** GUIDES is a criterion relation, not a claim that constitution acts as an agent or that every treatment benefits every person.

## Outer .1/.24

### O1a

| Exact group | Fixed candidate gloss |
|---|---|
| `odeedy` | all |
| `otedy` | living bodies |
| `opaees` | composite |
| `ar` | and |
| `chcthy` | elemental |

Candidate: All living bodies are composite and elemental.

Formula: `forall b in LivingBodies (COMPOSITE(b) & ELEMENTAL(b,E))`.

### O1b

| Exact group | Fixed candidate gloss |
|---|---|
| `otchdy` | fire |
| `otody` | contribution |
| `otar` | warmth |

Candidate: Fire contributes warmth.

Formula: `WARMTH in CONTRIBUTION(FIRE)`.

### O1c

| Exact group | Fixed candidate gloss |
|---|---|
| `chepaiin` | water |
| `otodar` | supplies |
| `otodaiin` | blood |
| `opaiin` | and |
| `otaiin` | moisture |

Candidate: Water supplies blood and moisture.

Formula: `SUPPLIES(WATER,BLOOD) & SUPPLIES(WATER,MOISTURE)`.

### O1d

| Exact group | Fixed candidate gloss |
|---|---|
| `qopchas` | earth |
| `otchedy` | supplies |
| `olkaiin` | flesh |
| `odar` | and |
| `aloees` | earth |
| `otchedy` | supplies |
| `qotedaiin` | bone |

Candidate: Earth supplies flesh, and earth supplies bone.

Formula: `SUPPLIES(EARTH,FLESH) & SUPPLIES(EARTH,BONE)`.

### O1e

| Exact group | Fixed candidate gloss |
|---|---|
| `odar` | and |
| `octhody` | study |
| `shedaiin` | of |
| `olaiin` | persons |
| `olfor` | explains |
| `daiin` | constitution |
| `ol` | is |
| `lkech[ch:?]` | necessary |
| `os` | for |
| `aiin` | human persons |
| `oteedy` | regimen |
| `dar` | from |
| `otees` | inclination |
| `opaiin` | and |
| `chcphdar` | constitution |

Candidate: Study of persons explains constitution and is necessary for their regimen based on inclination and constitution.

Formula: `EXPLAINS(STUDY(P),ConstitutionAttribute) & NECESSARY_FOR(STUDY(P),REGIMEN_DOMAIN(P; basis=InclinationAttribute,ConstitutionAttribute))`.

**Unresolved:** Two predicates share one overt study-subject by G15. Genitives, image-domain ownership and purpose attachment are newly proposed. Necessary-for-regimen is a goal condition, not an unconditional order that every person studies.

### O24

| Exact group | Fixed candidate gloss |
|---|---|
| `okees` | regimen |
| `ochar` | should consider |
| `oted[o:a]r` | predominant |
| `ochedy` | elements |
| `otody` | contribution |
| `olchedy` | common |
| `oteedo` | membership |
| `ar` | and |
| `or` | all |
| `airol` | persons |
| `otees` | inclination |
| `ar` | and |
| `aram` | nature |

Candidate: For every person, regimen should consider the predominant elemental contribution, common membership, inclination and nature.

Formula: `PROPOSED_OWNER_SCOPE: forall p in P SHOULD(CONSIDER(Regimen(p),[PredominantElementContribution(p),CommonMembership(p),Inclination(p),Nature(p)]))`.

**Unresolved:** The postposed ALL-person owner scope G10 spans the listed attributes in this one clause. This exact attachment is not independently bound. Treating common membership as a regimen criterion is a source-inference requiring review, not a quoted source instruction.

## Stop and actual next requirement

The packet contains a complete lexical display, while the source-constrained
semantic account remains partial. The first gaps are schema-level ownership
and distribution in N, the criterion tail in W.20, and the outer-locus
attachments. They must not be hidden by fluent prose. No seed was relaxed, unknown alternate normalized or target group dropped.
All proposed medical terms use the selected source’s concept inventory; that
does not establish every proposed relation. Unsupported relationships and owner
links remain explicit gaps. No UNSAT, source identity, decipherment or
preference supported by independent manuscript evidence follows.
