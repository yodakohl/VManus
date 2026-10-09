# Exact necessary intervals

For one book let fi,fj,fk be source-entry counts and a<b<c their original code lengths. H is the baseline integer length histogram and T a target histogram, both with all source and target bins. Rl=Hl−Tl, B=sum |Rl|. TV≤.20 on 8,000 groups is L1≤3,200.

Forward residuals in bins a,b,c become Ra−fi+fk, Rb−fj+fi, Rc−fk+fj. Put p=fi−Ra, q=Rc+fj, radius=3200−(B−|Ra|−|Rb|−|Rc|)−|Rb−fj+fi|. The TV inequality is exactly |fk−p|+|fk−q|≤radius, hence radius≥|p−q| and ceil((p+q−radius)/2)≤fk≤floor((p+q+radius)/2).

Reverse residuals are Ra−fi+fj, Rb−fj+fk, Rc−fk+fi. Use p=fj−Rb, q=Rc+fi and radius=3200−(B−|Ra|−|Rb|−|Rc|)−|Ra−fi+fj| in the same interval formula.

Forward glyph total is K−D*fk with K=old+fi*(b−a)+fj*(c−b), D=c−a. Reverse has K=old+fi*(c−a)+fj*(a−b), D=c−b. Determine acceptable integer glyph totals [L,U] by directly evaluating the original mean inequality for every reader, with an outward 1e−12 guard only in this necessary filter. Then ceil((K−U)/D)≤fk≤floor((K−L)/D). All integer divisions use floor division and negated floor division for ceil, including negative numerators.

Intersect these ranges across targets within each book. Four-dimensional prefix bitsets over the actual k entries enforce all four books simultaneously. A fifth count-sum range enforces the affected-occurrence cap. Distinct length classes avoid duplicate cycles. Keep the lexicographically smallest 2,000 candidates in a bounded heap; full testing uses original unguarded criteria. The range filter omits SD and all non-length conditions and is only necessary. Reproducing the range algorithm is not independent mathematical proof; exhaustive small fixtures and direct candidate length reconstruction provide separate checks. The algebra and two-length reduction were independently reviewed without source counts or outcomes.
