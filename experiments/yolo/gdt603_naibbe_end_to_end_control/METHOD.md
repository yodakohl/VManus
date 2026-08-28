# GDT603 method

## Question

Can Greshko's public Naibbe architecture be recovered end to end from its
ciphertext tokens when the solver receives neither the internal U/P/S
segmentation nor the surface-to-letter key?

## Inputs and separation

Before the blind artifact is written, the runner fetches only the pinned
Naibbe ciphertext and an independent Caesar Latin corpus. It knows the public
architecture: 23 active Latin letters, six anonymous tables, and therefore at
most 138 surfaces in each of the U, P and S states. It does not fetch or open
the published table or aligned plaintext during this phase.

The complete segmentation maps and recovered keys are serialized to
`gdt603_blind_freeze.json` and rehashed. Only then does the same runner fetch
the table and aligned plaintext for scoring. The blind artifact contains no
truth field.

## Ciphertext-only segmentation

The supplied whitespace tokens are retained. Every distinct token is modeled
as either one whole U surface or the concatenation of one P and one S surface.

The primary U inventory is fixed at 138, the public saturated capacity. This
choice needs no fitted U-size selector. Given that size, the deterministic
algorithm alternates:

1. capped maximum-coverage P and S dictionaries;
2. hard-EM selection among viable internal cuts under independent P×S
   occurrence marginals; and
3. U reassignment by positive Poisson deviance from the best P×S explanation.

U=115 and U=132 are exported only as navigation. A precursor sparse grid made
U=115 look better, but its original selector transcript was incomplete and
tie behavior was not byte-reproducible. It cannot support the primary claim.

## Blind key recovery

Each recovered U, P and S surface receives one of the 23 letters. No state may
assign more than six surfaces to one letter. The GDT602 capacity solver uses a
line-reset Caesar character order-4 model, two restarts and 40,000 annealing
iterations per restart, followed by coordinate and capacity-preserving swap
polishing.

## Evaluation and decision

After the freeze, the public table and aligned plaintext supply only the outer
evaluation. The primary model passes if occurrence-level exact segmentation is
at least 95%, normalized end-to-end edit accuracy is at least 94%, and key
accuracy conditional on an exact segmentation is at least 99%.

The test gives the whitespace token boundaries. It recovers only the hidden
U-versus-P+S decision and the internal P/S cut. It does not test recovery of
the ciphertext whitespace itself or plaintext word spaces.

## Claim ceiling

Passing establishes identifiability for this modern, fully specified control
architecture. It neither establishes that Voynich uses Naibbe nor licenses a
Voynich plaintext, language, lexeme or meaning. f84 and f84r are forbidden.
