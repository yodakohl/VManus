# f83r P1/P2 joint medical working reading (RAW_UNREVIEWED)

Bounded scope: only the existing GDT928 paragraph packet for `f83r.1–8` and `f83r.9–17`, in ZL3b and IT2a. ZL3b has 72+84 groups; IT2a has 71+83. RF1b has no complete paragraph flags. No other target rows, images, reserves or source text were opened for this draft.

## Content hypothesis

P1 introduces one case `C`, an affected sensory state `S`, and one treatment kind `M`. Its report first locates the problem at an initial/distal site `D`, then records a preceding history `H` that points to a different/proximal causal site `P`. The working intervention chain is `APPLY(M,D) → NO_BENEFIT(M,D,S) → APPLY(M,P) → RESPONSE(C,R)`. “Same M” means the same treatment kind under an explicit reference assumption; it does not mean the same physical dose or portion. The reported response does not by itself prove that P caused recovery.

P2 is provisionally a second presentation of the same case under `REPRISE(P1,P2)`. It reuses the variables `C, M, D, P, S, H, R` through the grammar relation, while allowing different report detail and clause order. `qokshedy` is read as a mentioned alternative medicine in the main reading; it is not silently administered. The main hypothesis therefore carries the content relation requested by the source analogy without claiming a literal Galen parallel or importing Rome, Pausanias, thirty days, or any other external detail.

## Core whole-form dictionary

| Whole form | Working value | Binding limit |
|---|---|---|
| `tchedy` | CASE_FRAME | introduces/reopens C; repetition does not create a new patient |
| `chedy` | STATE_ASSERTION | marks a state/proposition about S; it is not a body-part gloss |
| `chey` | NEGATE_OR_EXCLUDE | scope is assigned by the line frame, not by proximity alone |
| `lchedy` | SITE_P_REFERENCE | points to P in the working relation; repeated spelling does not prove referent identity |
| `lo` | CLOSE_OR_RESULT_SCOPE | closes a report/result scope; it does not mean cure by itself |
| `lsheedy` | HISTORY_OR_CAUSE_LINK | links H to a report/localization step; it does not make H unreported fact |
| `qokaiin` | SITE_D_REFERENCE | points to D in the working relation; it is not an anatomical noun |
| `qokal` | APPLY_OR_DIRECT | introduces an application/directive relation |
| `qokedy` | RESPONSE_OR_REPORTED_EFFECT | records R or a reported response; it does not encode causal success |
| `qokeedy` | NO_BENEFIT_OR_FAILURE_FLAG | licenses the changed-site branch only under the main alternative |
| `qokshedy` | OTHER_MEDICINE_CONTRAST | a mentioned rival treatment in the main reading, not an executed event |
| `shedy` | MEDICINE_KIND | denotes M as a treatment kind, not conserved material |

## Variables and explicit assumptions

- `C` is unified across P1/P2 only by the explicit `REPRISE` relation; shared words do not prove patient identity.
- `M` is unified across P1/P2 only by `REPRISE` plus the `MEDICINE_KIND` argument rule; no same-dose or same-portion claim follows.
- `D` and `P` are distinct sites in the main reading. The history-to-P link is an assumed content relation, not an independently observed target fact.
- `S` persists while motor status remains an unbound separate argument. The working reading never turns a response into a universal causal law.
- Every non-core whole form is retained as one persistent unknown lexical variable wherever it repeats. It is assigned a finite argument role in its line frame or left semantically unknown; no group is filler.

## Full raw-group ledger

Each row below preserves every source group. `U:form` means that exact whole form remains unknown but is retained as one identity wherever repeated. Core tags use the dictionary above; they are not EVA substring meanings.

### ZL3b — `f83r|f83r.1-f83r.8` (72 groups)

| Locus | Raw groups | Working tags | Line role |
|---|---|---|---|
| `f83r.1` | `tchedy lpchedy op{ch'}edy chepol pchedar shedy qopchedy` | `CASE U:lpchedy U:op{ch'}edy U:chepol U:pchedar MED U:qopchedy` | case introduction: C, S and M are introduced; remaining slots are unknown case descriptors |
| `f83r.2` | `sol cheey qokaiin shol lchs shey qoteedy rches ar chedy dor` | `U:sol U:cheey SITE_D U:shol U:lchs U:shey U:qoteedy U:rches U:ar STATE U:dor` | reported affected state at D; unknowns carry participant, extent and report framing |
| `f83r.3` | `olkeedy qotal chkeedy chey daiin chey lchedy qokaiin qotal dar` | `U:olkeedy U:qotal U:chkeedy NEG U:daiin NEG SITE_P SITE_D U:qotal U:dar` | reported history H contrasts or excludes a prior account and relates D to P |
| `f83r.4` | `qokshedy chedy qokedy chkedy daiin shetar shedy qekaiin chedy` | `OTHER_MED STATE RESPONSE U:chkedy U:daiin U:shetar MED U:qekaiin STATE` | M and an alternative-medication contrast are mentioned with a reported response |
| `f83r.5` | `d{ch'}eey qotaiin checkhy qoty che[g:d] shedy qokeey rchedy qoteedy lo` | `U:d{ch'}eey U:qotaiin U:checkhy U:qoty U:che[g:d] MED U:qokeey U:rchedy U:qoteedy CLOSE` | M and a scoped report close; remaining slots are unbound qualifiers |
| `f83r.6` | `schedy chedchy qokal olchedy qokaiin chedy qokeedy lchedy qoky` | `U:schedy U:chedchy APPLY U:olchedy SITE_D STATE NO_BENEFIT SITE_P U:qoky` | APPLY(M,D), STATE(S), NO_BENEFIT and SITE_P are linked in the working chain |
| `f83r.7` | `solshed lsheedy qeeedy qoky o qol rsheedy qokedy qoteedy qoteedy` | `U:solshed HISTORY U:qeeedy U:qoky U:o U:qol U:rsheedy RESPONSE U:qoteedy U:qoteedy` | HISTORY and RESPONSE are revisited; repeated qoteedy remains one unknown value, not an intensifier |
| `f83r.8` | `pchedal otedy shecthedchy qoky chedy chary` | `U:pchedal U:otedy U:shecthedchy U:qoky STATE U:chary` | state/result continuation; all six groups retained, with no filler deletion |

### ZL3b — `f83r|f83r.9-f83r.17` (84 groups)

| Locus | Raw groups | Working tags | Line role |
|---|---|---|---|
| `f83r.9` | `pchor checphedy qokedy lsheedy qokchdy r shedkedy qopshdy qopy` | `U:pchor U:checphedy RESPONSE HISTORY U:qokchdy U:r U:shedkedy U:qopshdy U:qopy` | response and history reopen the second presentation of C |
| `f83r.10` | `olkeey rchs cheeb ols aiin skal dain cthal s aiin chky lal sam` | `U:olkeey U:rchs U:cheeb U:ols U:aiin U:skal U:dain U:cthal U:s U:aiin U:chky U:lal U:sam` | reported-history/detail frame; all groups remain unknown arguments or modifiers |
| `f83r.11` | `sor shedy qokaiin chkain shcthey qokedy okair sheedy lchedy lo` | `U:sor MED SITE_D U:chkain U:shcthey RESPONSE U:okair U:sheedy SITE_P CLOSE` | M at D, reported response, then P reference and scope close |
| `f83r.12` | `qockhol sheckhy otal qokeal sheckhdy {ck}al okedy qokedy qokal` | `U:qockhol U:sheckhy U:otal U:qokeal U:sheckhdy U:{ck}al U:okedy RESPONSE APPLY` | response and APPLY frame; non-core groups remain unbound slots |
| `f83r.13` | `salcheol tar shedy s altedy sair qokedy q{cphh}edy lchcphedy ldar` | `U:salcheol U:tar MED U:s U:altedy U:sair RESPONSE U:q{cphh}edy U:lchcphedy U:ldar` | M and RESPONSE are repeated under a new report/detail frame |
| `f83r.14` | `qokchedy qokeedy shedy qokshedy dal lchedy qokaiin shcthy dal sy` | `U:qokchedy NO_BENEFIT MED OTHER_MED U:dal SITE_P SITE_D U:shcthy U:dal U:sy` | failure flag, M, alternative-medication contrast, stage and site relations |
| `f83r.15` | `saiin shedal shecthy chey tal shcthy dalchdy qotchedy lchedy` | `U:saiin U:shedal U:shecthy NEG U:tal U:shcthy U:dalchdy U:qotchedy SITE_P` | negative/contrastive report and P reference; no new patient is introduced |
| `f83r.16` | `tchedy qokchdy cheedar chldaiin chedy qokain checthy chealror` | `CASE U:qokchdy U:cheedar U:chldaiin STATE U:qokain U:checthy U:chealror` | CASE restatement and affected STATE; remaining anatomical/history slots unknown |
| `f83r.17` | `dche[o:?]kedy lkeed shckhey ytaiin shechy schety` | `U:dche[o:?]kedy U:lkeed U:shckhey U:ytaiin U:shechy U:schety` | closing report/outcome frame; six groups retained as unknown scope-bearing slots |

### IT2a — `f83r|f83r.1-f83r.8` (71 groups)

| Locus | Raw groups | Working tags | Line role |
|---|---|---|---|
| `f83r.1` | `tchedy lpchedy opcsedy chepol pchedar shedy qopchedy` | `CASE U:lpchedy U:opcsedy U:chepol U:pchedar MED U:qopchedy` | case introduction: C, S and M are introduced; remaining slots are unknown case descriptors |
| `f83r.2` | `sol cheey qokaiin shol lchs shey qoteedy sches ar chedy dor` | `U:sol U:cheey SITE_D U:shol U:lchs U:shey U:qoteedy U:sches U:ar STATE U:dor` | reported affected state at D; unknowns carry participant, extent and report framing |
| `f83r.3` | `olkeedy qotal chkeedy chey daiin chey lchedy qokaiin qotal dar` | `U:olkeedy U:qotal U:chkeedy NEG U:daiin NEG SITE_P SITE_D U:qotal U:dar` | reported history H contrasts or excludes a prior account and relates D to P |
| `f83r.4` | `qokshedy chedy qokedy chkedy daiin shetar shedy qekaiin chedy` | `OTHER_MED STATE RESPONSE U:chkedy U:daiin U:shetar MED U:qekaiin STATE` | M and an alternative-medication contrast are mentioned with a reported response |
| `f83r.5` | `dsheey qotaiin checkhy qoty cheg shedy qokeey rchedy qokeedy lo` | `U:dsheey U:qotaiin U:checkhy U:qoty U:cheg MED U:qokeey U:rchedy NO_BENEFIT CLOSE` | M and a scoped report close; remaining slots are unbound qualifiers |
| `f83r.6` | `schedy chedchy qokal olchedy qokaiin chedy qokeedy lchedy qoky` | `U:schedy U:chedchy APPLY U:olchedy SITE_D STATE NO_BENEFIT SITE_P U:qoky` | APPLY(M,D), STATE(S), NO_BENEFIT and SITE_P are linked in the working chain |
| `f83r.7` | `solshed lsheedy qeeedy qoky oqol rsheedy qokedy qoteedy qoteedy` | `U:solshed HISTORY U:qeeedy U:qoky U:oqol U:rsheedy RESPONSE U:qoteedy U:qoteedy` | HISTORY and RESPONSE are revisited; repeated qoteedy remains one unknown value, not an intensifier |
| `f83r.8` | `pchedal otedy shecthedchy qoky chedy chary` | `U:pchedal U:otedy U:shecthedchy U:qoky STATE U:chary` | state/result continuation; all six groups retained, with no filler deletion |

### IT2a — `f83r|f83r.9-f83r.17` (83 groups)

| Locus | Raw groups | Working tags | Line role |
|---|---|---|---|
| `f83r.9` | `pchor checphedy qokedy lsheedy qokchdy r shedkedy qofshdy qopy` | `U:pchor U:checphedy RESPONSE HISTORY U:qokchdy U:r U:shedkedy U:qofshdy U:qopy` | response and history reopen the second presentation of C |
| `f83r.10` | `olkeey rchs cheen ols aiin skal dain cthal saiin chky lal ram` | `U:olkeey U:rchs U:cheen U:ols U:aiin U:skal U:dain U:cthal U:saiin U:chky U:lal U:ram` | reported-history/detail frame; all groups remain unknown arguments or modifiers |
| `f83r.11` | `sor shedy qokaiin chkain shcthey qokedy okair sheedy lchedy lo` | `U:sor MED SITE_D U:chkain U:shcthey RESPONSE U:okair U:sheedy SITE_P CLOSE` | M at D, reported response, then P reference and scope close |
| `f83r.12` | `qockhol sheckhy otal qokeal cseckhdy ckol okedy qokedy qokal` | `U:qockhol U:sheckhy U:otal U:qokeal U:cseckhdy U:ckol U:okedy RESPONSE APPLY` | response and APPLY frame; non-core groups remain unbound slots |
| `f83r.13` | `solcheol tar shedy saltedy sair qokedy qpchedy lchcphedy ldar` | `U:solcheol U:tar MED U:saltedy U:sair RESPONSE U:qpchedy U:lchcphedy U:ldar` | M and RESPONSE are repeated under a new report/detail frame |
| `f83r.14` | `qokchedy qokeedy shedy qokshedy dal lchedy qokaiin shcthy dal sy` | `U:qokchedy NO_BENEFIT MED OTHER_MED U:dal SITE_P SITE_D U:shcthy U:dal U:sy` | failure flag, M, alternative-medication contrast, stage and site relations |
| `f83r.15` | `saiin shedal shecthy chey tal shcthy dalchdy qotchedy lchedy` | `U:saiin U:shedal U:shecthy NEG U:tal U:shcthy U:dalchdy U:qotchedy SITE_P` | negative/contrastive report and P reference; no new patient is introduced |
| `f83r.16` | `tchedy qokchdy cheedar chldaiin chedy qokain checthy chealror` | `CASE U:qokchdy U:cheedar U:chldaiin STATE U:qokain U:checthy U:chealror` | CASE restatement and affected STATE; remaining anatomical/history slots unknown |
| `f83r.17` | `dcheo kedy lkeed shckhey ytaiin shechy schety` | `U:dcheo U:kedy U:lkeed U:shckhey U:ytaiin U:shechy U:schety` | closing report/outcome frame; six groups retained as unknown scope-bearing slots |

## Transparent counts and stop rule

| Stream | P1 groups | P2 groups | occurrences | exact types | singleton types | cross-paragraph core types / occurrences | non-core unknown occurrences |
|---|---:|---:|---:|---:|---:|---:|---:|
| ZL3b | 72 | 84 | 156 | 113 | 92 | 12 / 43 | 113 |
| IT2a | 71 | 83 | 154 | 112 | 92 | 12 / 44 | 110 |

Across the four streams there are 310 occurrences and 128 pooled exact surface types. The 12 core types account for 87 occurrences; 223 occurrences from 116 pooled non-core types remain unknown. The 92 singleton types in each reader stream are therefore not silently converted into 92 sentence meanings. If the unknown roles cannot be reduced to a finite shared argument grammar without assigning those singleton meanings or changing a repeated value, this working reading stops with the exact unknown ledger above.

## Binary alternatives

1. **A — same M at D then P / different M at D.** The main reading preserves M while changing site. The rival substitutes a different medicine at the original site and leaves the history-to-P relation unused.
2. **B — failure flag / planned stage.** The main reading makes `qokeedy` a no-benefit report that licenses relocation. The rival treats it as a planned stage, so relocation is permitted even after success.
3. **C — reprise / independent second case.** The main reading unifies C, M, D, P, S and H through an explicit `REPRISE` relation. The rival keeps all paragraph variables distinct and predicts no cross-paragraph content transfer.
4. **D — mentioned alternative / executed alternative.** The main reading keeps `qokshedy` as a contrastive medicine mention. The rival adds a second intervention and an additional treatment outcome.

No old 376 fallback meanings, 993 Goat/Wolf/Cabbage glosses, renderer roles, or EVA-shape semantics are inherited. This is a constructed source-inspired working reading, not a translation or a claim of Galen provenance.
