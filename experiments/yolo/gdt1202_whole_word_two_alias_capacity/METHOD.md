# Why the bounds are optimistic and carrier-independent

A frequency n splits into at most two nonnegative integer cells. Their difference
is minimized at ceil(n/2),floor(n/2). Transferring one occurrence from a larger
cell to a cell smaller by at least2 cannot increase any sum of the largest k
pooled cells. Repeating this exchange for each word proves simultaneous minimal
pooled top-k sums at the balanced splits. The proof is unchanged by other words'
cells. Maximum positive-cell count is min(n,2)per word.

Merging two cells leaves their total mass but cannot lower any largest-k sum
(zero-pad the vectors) or increase the number of positive cells. Therefore even
cross-source-word homographs cannot improve the optimistic bounds. These facts
do not prescribe a human writing policy or constrain lengths/endings/meanings.

Distinct source word spellings remain separate, even if a philologist might
consider them forms of one word; merging meanings would change the contract.
Sampling is the first8000stored whole words of each book, rather than1196's
first8000fragments. The contract and source hashes are sealed before the census.
