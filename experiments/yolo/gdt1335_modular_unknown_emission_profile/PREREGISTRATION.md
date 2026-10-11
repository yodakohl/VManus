# GDT1335 — unknown spelling weights: profiling is not bag conditioning

Fixed source-free calculation11October2026. Inclusive budget09:02–09:22UTC:
proof, small exact computation, independent validation and publication. Expected
hand calculations were derived before implementation and are disclosed below;
this is not a blind recovery experiment. No native text or key search follows.

## Decision and scope
1322proved the normalized channel with KNOWN fixed bank weights q;1324studied
its exact toy recovery under supplied source laws. Their conclusions remain.
The bounded reviewer and root now derive the different UNKNOWN-q nuisance
contract. Unknown: whether the exact proposed profile score and word-bag
conditional normalization agree with direct finite-channel optimization and
enumeration, including support and nonnormalization caveats.

If valid, lack of supplied q alone is not a mathematical impossibility barrier;
a correct explicit nuisance model can optimize it. This does not supply an
independent bank, source law, realistic recovery control, native word grammar or
meanings. If formulas fail, do not use them. The smallest adequate check is the
following completely specified finite example; no decoder infrastructure,
additional corpus, smoothing search or larger automatic control is selected.

## General contract and proof targets
Finite bank B fixed before key comparison. Surjective D_K:B->m source characters,
positive spelling weights q(w), with replacement, independent of source history
conditional on the current character. The source law Psrc is a fixed normalized
law for the SAME source length and boundary convention, not fitted per key.
For fixed K, class emissions e_K(w)=q(w)/Z_K(D_K(w)) range over all independent
positive class probability vectors as unrestricted positive q varies.

Observed counts n_w, decoded counts n_c. The profile log likelihood is
 logPsrc(D_K(w_1:N)) + sum_w n_w log(n_w/n_{D_K(w)}).
It is an attained maximum if all words in visited classes are observed; otherwise
zero fitted emission weights may give only a SUPREMUM under strict positivity.
Unvisited source classes contribute nothing and leave their emissions arbitrary.
The bank and source coverage are NOT redefined from observed support. There are
|B|-m effective emission parameters, plus unidentifiable between-class q scales.
If q is tied by a compact shape model, this free-q expression is only a generous
upper bound, not that model's profile. A data-fitted profile is not itself a
normalized probability distribution over all possible datasets.

For known IID pi>0, exp(profile) equals the empirical cipher-word likelihood
product_w(n_w/N)^n_w times product_c(pi_c/(n_c/N))^n_c. In logs this is a
key-independent constant minus N*KL(f_K||pi). If pi is ALSO fitted as f_K,
the old flat empirical pooling identity returns. This is a different contract.

Conditioning on the exact cipher-word bag instead cancels emissions, but gives
 P_K(w_1:N | bag)=Psrc(c_1:N)/[A_K * Psrc(source histogram=n_c)],
 A_K=product_c n_c! / product_w n_w!.
Both factors in the denominator generally depend on K. If the histogram event
has probability0, this key cannot explain that bag; do not rescue0/0. Under IID,
the conditional probability becomes product_w n_w!/N! for every arrangement,
independent of K and pi. Markov sources retain order information, with the full
histogram normalizer still necessary. Conditioning is not the profile operation.

## Fixed finite check
Toy drawing alphabet a,b; source residues0,1 modulo2. Bank in exact order
[a,b,bb]. Compare K1(a=0,b=1), K2(a=1,b=1). These two illustrative keys are NOT
an exhaustive recovery benchmark; neither is declared true. Fixed N=4 and the
observed ordered packet tuple [b,b,a,bb], whose bag has12distinct arrangements.

Initial pi=(1/4,3/4) in0,1 order. Two source laws:
 IID: every transition row is pi;
 MARKOV: rows(3/4,1/4) and(1/4,3/4), with the same initial pi.
Both laws are normalized with their stated boundary convention. Enumerate all
3^4cipher tuples, not just the selected bag. Exact rational arithmetic throughout.
For every tuple/key/law save profile supremum and bag-conditional probability.
Retain the sum of profiled likelihoods over all81tuples as a NONNORMALIZATION
check, not a total probability. Every bag's conditional probabilities must sum1.

For the selected bag derive fitted class emissions once, hold them fixed, and
verify their full81-output channel probabilities sum1 for each key/law. Do not
confuse that fixed fitted channel with refitting q separately for every output.

Disclosed hand expectations:
 IID selected profile K1=9/1024, K2=1/64; bag-conditional both1/12.
 MARKOV selected source-only probabilities tie at27/256, but bag-conditional
 K1=27/104 and K2=1/6. This illustrates the needed key-dependent normalizer.
If source IID pi is refitted too, both selected profiles become1/64.
These are analysis examples, not recovered keys or messages.

## Independent validation
Primary computes profiles from counts and conditions by grouping all cipher
tuples with the same word bag. Independent validator maximizes explicit emissions
on the complete rational candidate set j/k,0<=j<=k<=4, including boundary optima
as suprema, using the concavity proof for the one free two-word class parameter.
It obtains conditional probabilities from separate binary source-string histogram
enumeration and the factorial multiplicity, rather than cipher-bag grouping.
Verify all324tuple/key/law values, all60bag normalizations, both IID identities,
fixed-fitted-channel normalization and the disclosed exact hand values. No native
cache, raw TSV, image, source-language book, reserve or word meaning.
