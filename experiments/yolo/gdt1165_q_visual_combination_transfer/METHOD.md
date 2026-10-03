# GDT1165: held q+base visual-combination transfer

## Decision and scope

One-hour block started2026-10-03 16:04:53UTC, planned result/publication checkpoint17:04:53UTC. Preparation, implementation, validation and publication are included; reassess expansion at that checkpoint, never fabricate completion. Existing1157 whole-word search failed,753 role switch failed,316/317 establish a preceding-formal-DY production tendency. New question: does a common inversion of a base-only visual association predict q-choice for a family whose q observations never fit that transformation, on wholly excluded physical leaves? Positive would nominate an image-linked transformation for further interpretation, not translate q as NOT. Negative closes this fixed model; no automatic feature/word/threshold repair.

Exploratory exposed data: exactly1157's38imagepages/32physicalleaves, both original observers' six codes, and169original word inventory. No new images, reserves, f84/f84r or f116v; ZL3b only. Prior selection and exposure preclude independent confirmation or project-wide significance. No authorial word-owner or inscription-to-inscription edge is asserted; GDT388 edge scoring is not this endpoint (see RELATION_GATE_SCOPE_CORRECTION).

Capacity was fixed before inspecting counts: literal(X,qX), both in169inventory, each presence/absence on at least4physicalleaves, at least6eligiblepairs. Twelve of13pairs pass; otchey/qotchey fails and stays excluded. All counts retained in Q_VISUAL_COMBINATION_CAPACITY.json. No associations were inspected for that screen.

## Sources and preprocessing

Original1157 word presence inherits1090's ZL,kindP, definite-boundary scope: left LINE_START/DEFINITE_SPACE/DRAWING_INTERRUPTION and right DEFINITE_SPACE/LINE_END/DRAWING_INTERRUPTION. Query all38allowed pages through selector-first guard before materializing data. Retain complete guarded rows, including ineligible rows with their reasons. Every eligible exact X/qX event in twelvepairs enters the new task. Check every one of38×24presence cells against1157; any remaining discrepancy stops scoring. The initial preparer omitted these scope columns and found9mismatches; preserve its files and receipt, correct the projection to the original scope before fitting, never reinterpret these as a changed semantic result.

Preceding DY means the frozen formal dy_closure, not raw ending or free DY. Apply unchanged run_gdt012_core_semantic_atlas.strip_layers(raw)[2] to a lowercase-a-z preceding whole, as already used by1051; marked/nonlowercase predecessor is unknown. First group has previousDY=0known. Validate against all hash-matched legacy278rows; any disagreement stops scoring. Initial legacy-only join left112of232candidateeventsunknown because inventory coverage was partial; retain that failed join receipt. This is reuse of a frozen formal function, not a new decoder. Pin source/function hashes.

Each event retains page/leaf/locus/index/count/raw, exact base-family ID, qchoice0/1, previousDY, DYunknown, physical line start, relativeposition=(index−1)/max(count−1,1), and full ZLpage groupcount. Page length uses all raw ZLgroups within the guarded page, not q outcomes. All pages H/A/1; no between-hand/Currier inference.

## Base visual learner

For every held physical leaf, fit the unchanged1157 single-feature base model on remaining leaves for the twelve BASE words only. qform columns never fit base models or select their features. Retain1157's64-state joint uncertainty calculation, total Dirichlet1, word/feature capacity, exact beta grid/penalty, background and tie averaging. No new unions or posthoc feature selection. Produce visual probability and background for all training and held pages, using only training states/labels. Word-level fit independence must be checked when reducing169columns to12.

Base visual score =logit(clipped visual probability)−logit(clipped background), clip1e−9 to1−1e−9. For each family standardize this score using its training-page mean and population SD; if SD≤1e−12, score0everywhere. This retains a known base-only visual association for the held combination; withholding the whole unmapped root would not identify a property to transform.

## Shared q transformation, crossed exclusions

For each of12targetfamilies and32heldleaves, qclassifier training excludes BOTH all events of that family and all events of the held leaf. Thus targetq observations cannot fit coefficients, select sign, impute features or calibrate an intercept. All other11families contribute. Predict only events of targetfamily on heldleaf; retain empty folds as empty, never a successful prediction. Base X learning on other leaves is permitted and disclosed.

Context covariates: previousformalDY, DYunknown, line_start, relativeposition, log1p(full page groupcount), base backgroundlogit. Standardize the three continuous covariates (position,loglength,backgroundlogit) by weighted training moments; SD≤1e−12 maps to0. Binary covariates remain0/1. Intercept included. These address known production/position and text-amount competitors; no claim they exhaust all confounding.

Each training family has equal total weight; withinfamily each nonempty physicalleaf has equal weight; withinfamily-leaf each event equal. Weights sum1. Minimize weighted mean logistic NLL +0.05/2 times squared nonintercept coefficients. Fit C=context only and FULL=context plus standardized base visual score. Newton with backtracking, max100 iterations, max absolute gradient≤1e−9. Preserve convergence diagnostics; unresolved fit failure invalidates the result, with no adaptive regularizer/iteration repair.

ID constrains visual coefficient≥0; INV constrains≤0. By convexity, use FULL when its coefficient satisfies the constraint, otherwise C (the zero-coefficient boundary optimum). At coefficient exactly0 both are C. Store C/FULL coefficients, scaling, fit losses, gradient norms, iteration counts and selected constrained model. The intercept of the unseen family is never separately fit. This is conditional q-choice among known-family occurrences, not a calibrated occurrence rate for unseen words.

## Score, controls and fixed decision

For each nonempty targetfamily/heldleaf cell, average event log2 losses; each family's loss is its equal mean over active heldleaves. Overall loss equal mean over twelvefamilies. Gains are C_loss−INV_loss and ID_loss−INV_loss. T is their minimum. Positive eligibility requires bothgains≥0.01bits, both strictlypositive for≥8of12families, and FULLvisualcoefficient<−1e−8 in≥80%ofactivefolds. Report all family and fold results, even failures. No per-word favourable subset is nominated.

199image-bundle permutations, seed1165, with1157's physicalleaf blocks by sorted(face,hand,Currier). Move both observers and allsixfeatures of a leaf jointly, preserving r/v positions, and refit the entire base+qpipeline in every world. Text/events/families/eligibility remain fixed. Raw T is computed for EVERY world without gate censoring. Conditional rank=(1+count(nullT≥observedT−1e−12))/200. Require≤.05 plus allobservedgates. Reuse1157's mobility gate≥12mobileleaves and≥100observable assignments; export distinct raw/consensus hashes, orbit and all199results. No reduced null schedule, adaptive deduplication or new seed. Up to32workers; BLASthreads1.

PASS is IMAGE_LINKED_INVERSE_COMBINATION_TRANSFER, otherwise NO_SUPPORTED_INVERSE_COMBINATION_TRANSFER; source/capacity/convergence failures have separate states, not negative semantic results. Even aPASS permits topic/register or case/derivation explanations rather than logicalnegation. Conditioning on known family itself creates substitution/complementarity; image-shuffle controls and comparison with context/identity are essential, but do not identify denotation. No word, prefix, language or NOT meaning is confirmed.

## Reproduction and independent validation

Pin METHOD, preparation, runner, sources and preparedINPUT in PREREG_LOCK.json before first model execution. Public pre-score commit intended; report if absent. Independent validator checks source preservation/scope, allpresence cells, fixed pairs, frozenDY replay, strict two-axis training exclusions, weights/scales, baselearner equivalence, everyobservedprediction/score, convex-gradient conditions, independent optimizer sample, nullmap reproduction and all199decision summaries. Do not call an accounting check meaning confirmation.
