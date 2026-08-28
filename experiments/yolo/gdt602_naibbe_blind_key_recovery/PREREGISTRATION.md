# GDT602 executable contract

- Complete shipped Pliny control; no target Voynich text.
- Oracle U/P/S segmentation constructed outside `solve()`.
- Independent Caesar char-4 model.
- Public 23-letter alphabet and six-homophone capacity per state/letter.
- Seeds 1, 2, and 3; 30,000 iterations and one restart each.
- Positive result only if every seed exceeds 99.9% weighted character and 98%
  type recovery.
- Unconstrained 100,000-iteration, two-restart comparison at seed 11.
- Aligned plaintext and published key used only after optimization for scoring.
