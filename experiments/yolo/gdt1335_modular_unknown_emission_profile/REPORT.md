# GDT1335 — unknown spelling weights can be profiled, but conditioning differs

The exact source-free check confirms a usable nuisance-likelihood formula for
UNKNOWN spelling weights. It does not recover any key or supply the missing
native bank, source law or writing mechanism.1322's known-q normalization and
1324's known-channel recovery results remain correct under their own contracts.

For a fixed finite bank, surjective decoder D_K and independently fixed normalized
source law, unrestricted positive spelling weights can be profiled:

`logL_profile(K) = logP_source(D_K(w_1:N)) + sum_w n_w log(n_w/n_{D_K(w)})`.

Every class-normalized emission vector is realizable by a positive global q;
between-class scales are unidentifiable. The multinomial optimum assigns each
observed word its empirical share of its decoded class. If an unobserved bank
word lies in a visited class, its optimum is0, so strict positivity gives only
a SUPREMUM. Unvisited classes remain arbitrary. Bank and surjectivity are not
redefined from observed support. There are |B|-m effective emission parameters;
a compact grammar tying weights would require a different, constrained profile.

Under fixed IID pi, this equals a key-independent empirical word term minus
N*KL(decoded empirical frequencies || pi). It is generally NOT flat. Fitting
pi as well makes it flat again, recovering the already known pooling identity.
The profile itself is not a normalized probability distribution over all possible
data: q has been fitted separately for each dataset.

## A small complete example

Bank a,b,bb; modulo2 keys K1(a=0,b=1), K2(a=1,b=1); four observed packets
b,b,a,bb. Neither key is called true. Initial source probabilities(1/4,3/4).
IID transitions use those probabilities; the Markov law instead has persistence
3/4 and switch probability1/4, with the same initial law. Expected hand values
were disclosed before code execution; this is not blind recovery.

| Source law | Key | Profile likelihood/supremum | Probability conditional on exact word bag |
|---|---|---:|---:|
| IID | K1 |9/1024|1/12|
| IID | K2 |1/64|1/12|
| Markov | K1 |27/1024|27/104|
| Markov | K2 |1/64|1/6|

For the selected bag every bankword was observed, so these profiles are attained
maxima. Across all81possible four-packet datasets per case, only51profiles are
attained under strict positivity;30are boundary suprema. Summing the separately
profiled likelihoods gives45109/24576,23447/8192,50615/24576and21047/8192in table
order, all greater than1. These sums are NOT probabilities or recovery accuracies.
When the selected fitted emissions are held FIXED, the complete channel does
normalize to1 in each case, as required.

## Why removing the spelling factors is not enough

Conditioning on the exact cipher-word bag cancels all spelling factors, but its
correct probability is

`P_source(decoded order) / [A_K * P_source(source histogram = n_c)]`,

where `A_K = product_c n_c! / product_w n_w!` counts cipher arrangements per
source-character arrangement. The histogram probability and multiplicity depend
on the key. A zero-probability histogram cannot be rescued through0/0.

Under IID this becomes uniform over bag arrangements, independently of key and
pi. The selected bag has12arrangements. Under the stated Markov law, both selected
source-only sequence probabilities are27/256, yet the correctly conditioned
probabilities differ as27/104versus1/6. The omitted normalizer would hide that
contrast. Conditioning and profiling therefore answer different questions.

## Validation and research decision

All324cipher-tuple/key/law values and60bag normalizations were checked with exact
fractions. The independent validator directly optimizes the emission polynomial
on every possible rational count optimum for N=4; its conditional denominator
comes from separate binary source-histogram enumeration and factorial counts.
Four fixed-fitted-channel normalizations and both IID identities agree. Neither
program imports the other. A bounded reviewer independently derived the general
formulas before this check. No manuscript/source-language corpus was read.

Known q is not logically indispensable when a declared nuisance model is used
correctly. This does NOT justify a large native key search: the free spelling
parameters, fixed-bank/support assumptions, independent source law and realistic
recovery/calibration remain unpaid. Arbitrary source-language fitting would erase
the IID discriminator. No larger control, decoder, new source or native word
assignment is selected by this result. The source-law/generative-model cost must
be stated before any future search; a favorable in-sample score is not a reading.
