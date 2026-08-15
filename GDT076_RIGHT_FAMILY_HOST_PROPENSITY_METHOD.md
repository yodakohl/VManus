# GDT076 — RIGHT_FAMILY host-propensity transfer

Status: **YOLO formal-class mechanism test**

Test whether a PAGE_HOST's tendency to select each explicit RIGHT_FAMILY is a
stable cross-register property rather than a proxy for host frequency.  For
each of the five HPR2 registers, hold that register out.  Retain a host only
when it has at least 20 training occurrences on at least three physical folios
and at least five held occurrences on at least two folios.  Compare the
training and held rates for `aiin`, `air`, `ain`, `ar`, and `al`.

For the fixed HPR3 class `R=aiin >= .25`, report held-register confusion,
balanced accuracy, and every error.  Its matched frequency control predicts the
same number of high hosts in each fold by choosing the most frequent training
hosts.  A 20,000-draw null permutes training-high labels within held-register
training-frequency quartiles and reruns the binary score.  This test is
source-only and does not use external visual labels.  A positive result may
establish a transferable formal host class, never content or meaning.  f84r is
excluded.
