# Exact maximum of minimum proof support

For a fixed threshold t let W_t contain the original whole types with source
support at least t. The quotient closure Q(W_t) is the least set containing
W_t and closed under u,v=u+r implies r. Every remainder is a suffix of an
original word, so the state universe is finite. Give absent suffixes weight0.

Initialize original weights. Repeatedly apply b(r)=max(b(r),min(b(u),b(v))).
Weights only increase and belong to the finite set of source weights. Each
increase has two earlier, already justified parent events. Thus the result
is attainable by a finite proof. At saturation it dominates every finite
proof by induction. Consequently b(r)>=t exactly when r belongs to Q(W_t).
This is a maximum bottleneck, not a minimum deletion count: duplicated leaves
in a proof are not counted as independent evidence or added together.

Prefix cancellation remains conditional on a fixed prefix-free, nonempty
letter code preserving these whole-word seams. At a threshold we apply1234's
same necessary bound to precisely Q(W_t), with the signs observed in W_t.
No new code is fitted. The1-threshold result must equal the original1234result.
Counts and distinct selectors are calculated separately for each transcription.
The fixed threshold family is descriptive; no significance, best threshold or
preferred transcription is selected.
