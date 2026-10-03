# GDT1160 — context resolves real source ambiguity; the fixed neural arm adds value

**CONTEXT_AND_NEURAL_INCREMENT.** In this supervised historical-source task,
linear context improves the registered macro accuracy from the stronger
frequency/layout baseline of68.857% to76.155%. The fixed neural arm reaches
**79.651%**, a further **3.496 percentage points**. All four held books favor
both contextual arms, and all four favor N over C. Both predeclared promotion
gates pass. This result does not identify a Voynich word or writing channel.

The task includes every one of21,512 test sites licensed by training-only
ambiguity support, with exact original marked spellings preserved. The same
observed marked group can receive several editorial expansions. No hidden
answer is supplied to a candidate domain or neighboring input. The sample is
not the whole-source denominator underlying GDT155's93.7% lookup result.

## Complete primary result

Each form type has equal weight within its book; the four book metrics then
have equal weight. F is candidate frequency, L adds layout, C adds linear
context, N is one64-unit ReLU architecture on the same C input.

|Held book|Sites|Types|F|L|C|N|
|---|---:|---:|---:|---:|---:|---:|
|Band2|3043|83|63.188%|62.555%|70.154%|74.111%|
|Band3|4870|79|67.340%|68.508%|76.625%|78.532%|
|Band4|4763|95|72.241%|71.609%|80.042%|82.815%|
|Band5|8836|75|70.489%|72.753%|77.800%|83.147%|
|Equal-book primary mean|||68.315%|68.857%|76.155%|79.651%|

C improves on max(mean F,mean L) by7.299points, above the fixed3point minimum,
and beats both in4/4 books. N improves on that baseline by10.795points and on
C by3.496points, above the extra1point minimum; all required fold counts are4.

Token-weighted correct counts are F=17018, L=16989,
C=18566, N=19098 out of21,512. N repairs825 C errors and
introduces293 errors where C was correct: a net532 additional correct source
expansions. **N still makes2,414 errors**, including all171 answers absent from
the training candidate domains. They remain in every relevant denominator.

The complete332-row CANDIDATE_TABLE.md gives each exact form's entire training
candidate inventory, held answers, all four accuracies and context-dependent
N prediction counts. All21,512 rows and every seed's legal-candidate probability
vector are preserved in the compressed prediction/result artifacts. No
favorable examples substitute for this full panel.

## Registered secondary checks

Only0/0/2/15 test contexts respectively exactly match a same-type sixteen-neighbor
training window. Retaining only novel windows leaves each primary book score
unchanged to within0.011percentage points; all original duplicate rows remain
in the primary panel. This does not exclude longer source relationships,
near-matching formulas or shared editorial habits.

The training-defined terminal m/n subset contains851/1009/679/1494 held sites.
All candidate expansions remain possible, including outputs other than m/n.
N versus C type-macro gains are0.172/4.895/3.076/5.898percentage points. These
are formal ending contrasts; the test did not independently label their
syntactic case or semantics. Complete secondary metrics and complete-record
ambiguous-site accuracies are in RESULT.json.

## What the positive does and does not buy

Preserving written context demonstrably helps rank alternative expansions that
this retained source representation cannot distinguish in isolation. Within
the fixed training budget, the selected small neural architecture earns its
additional complexity over the linear contextual arm. It is a control-tested
supervised candidate ranker, not a discovered source language or an unsupervised
lexicon method. It cannot score unconstrained Voynich glosses without a separately
justified candidate representation and training relationship. No such target
lattice was constructed here, and no decoder family is reopened.

The synthetic editorial marker collapses sign information: these are not proven
native graphical homographs. Human editorial expansions are the reference,
not an independent new paleographic collation. Related held books are not
independent traditions; all source labels had earlier project exposure.

All learned training-loss curves still descend at epoch20. The fixed-budget
comparison is real, but does not prove a converged linear optimum, neural
necessity or the causal value of nonlinearity alone. N differs in bottleneck,
parameterization and optimization. There was no held-result tuning or second
architecture. The positional local features do not establish long-range grammar.
Softmax values were not assessed for probability calibration and are not
probabilities that a Voynich meaning is true. No significance claim is made.

## Execution and independent validation

Public preregistration commit:c14ae2eee323411df25b1416eb0ca3f9dcbb4c39,
pushed before all24 real fits. Two fixed seeds were averaged for each learned
arm in each book; no restart was selected. All four prediction files and fit
receipts were hash-locked before the separate scoring command. The original
runner and SPEC remain byte-identical to the registration commit.

Independent validation passes **122/122 checks**, including every source-site
join, candidate domain, probability mean/tie, site/type/secondary metric,
OOV penalty and gate. All24 local saved-weight forward replays use independently
constructed features and match the stored probabilities exactly. No runner
imports or refits were used. This certifies accounting, not manuscript meaning.
The validator's release extension followed preregistration and is disclosed;
its original preparation helper is retained in commit history.

Local fitted NPZ files are not published; pinned software, seeds and complete
source permit retraining, while published legal-candidate probability vectors
permit independent result accounting. Release checks cover this experiment and
explicit shared updates, not unrelated legacy index/manifest issues. The existing
index rows were retained when a global rebuild proposed unrelated changes.

Selected06:25:07UTC; scoring completed06:46UTC and independent validation before
07:00UTC. Publication completion is recorded in the work decision dossier.
The ongoing ten-hour research block began02:27UTC and is not complete.
