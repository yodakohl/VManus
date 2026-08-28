# GDT603 decision contract

- Primary model: capacity-saturated `U=138`.
- Navigation only: `U=115` and `U=132`.
- Blind inputs: pinned ciphertext, independent Caesar corpus, public
  23-letter/six-table capacity.
- Blind exclusions: published table, aligned plaintext, true segmentation and
  true key.
- Pass: primary exact segmentation `>=0.95`, end-to-end edit accuracy
  `>=0.94`, and key accuracy given exact segmentation `>=0.99`.
- Scope: control recovery only; no Voynich decoding claim.
