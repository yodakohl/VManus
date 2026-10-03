# GDT1160 independent validation

Accounting: 122/122 checks pass. Scientific result: CONTEXT_AND_NEURAL_INCREMENT.

The validator reconstructs all source sites, complete-record written contexts, training-only candidate domains, all probability means and ties, every site/type/secondary metric and fixed gate without importing the runner. Independent frozen-weight forward replays: 24.

Primary accuracy gives each marked type equal weight within each book, then each book equal weight.

| Arm | Macro accuracy |
|---|---:|
| F | 68.315% |
| L | 68.857% |
| C | 76.155% |
| N | 79.651% |

C gains 7.299 percentage points over the stronger mean F/L; N gains 10.795. N gains 3.496 points over C. All three comparisons are positive in all four held books.

All 21,512 held sites remain included, including 171 out-of-domain truths counted as errors. Exact same-type training-context matches number 0/0/2/15 across the four books; all secondary subset metrics were recomputed.

Failed checks: none.

The helper was extended after public preregistration; source, specification and runner remain unchanged. Registered code is checked against the public commit.

Technical accounting is not word-meaning validation.

Source editorial markers do not certify native graphical homography.

No refitting: saved weights and all held probabilities checked when weights are supplied.

Local weights are not published; reproduction of fits requires pinned dependencies and retraining.

Locks bind bytes and sequencing in code; they do not independently certify analyst secrecy or exact first-access times.

Loss curves do not prove optimizer convergence; no held-result retuning permitted.

All learned-arm online training losses remain decreasing at epoch20. The fixed-budget comparison does not establish a converged linear optimum or causal necessity of nonlinearity.

Related held books and historical label exposure are retained; no independent tradition or fresh blinding claim.
