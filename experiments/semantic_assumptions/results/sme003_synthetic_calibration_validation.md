# SME003 independent synthetic-calibration validation

Validation status: **PASS_INDEPENDENT_TARGET_FREE_CALIBRATION_RECONSTRUCTION**

The clean-room validator independently reconstructed all 402 frozen cases with 32 workers in 16 minutes 15 seconds: 64 null worlds, 128 power records, 160 whole-row controls, 10 invariance controls, one complement control, seven leakage controls, and 32 reading-dependence controls.

The reconstructed result decision is **FAIL_CLOSE_SME003_BEFORE_TARGET**. The null-union count is 2/64. Complement, invariance, leakage, mutation, and reading-dependence controls pass; `whole_row_controls_rejected` is false. This validates the stored failure decision and does not authorize target access.

Target isolation remained intact. The result records `target_rows_accessed: false`, `morphology_fields_accessed: false`, and `target_join_performed: false`; the validator independently confirmed that all registered target artifacts were absent before and after reconstruction.

Two formula-equivalent floating-point operation-order corrections were required before the final run:

- orientation vectors now use the frozen contrast-coefficient vector multiplied by the standardized page matrix, rather than subtracting separately reduced high/low means;
- score orbits now use the frozen small possible-shift contrast tables, ordered page accumulation, total-direction subtraction, `held @ W` followed by rowwise multiplication/sum, and packed contribution averaging, rather than a large assignment matrix multiplication, selected-fold means, optimized three-operand `einsum`, and incremental averaging.

These changes alter only low floating-point bits and preserve the frozen statistic. Exact targeted parity passed for all 475 required world-0 checkpoint leaves, all 551 required leaves of one planted power record, and all 678 required leaves of one nontrivial whole-row control before the full validation.

SHA-256:

- validator: `ba453136442988814bb1d59349baefe628a6e1d8ced246ae24843c0ab1703cba`
- stored result: `eeac17e8897d1745b398063796c68187f1c7692db1e496e5eba9a5afabf1036b`
- exact validator stdout artifact: `58b198ab2fc544d110bcdbc72fcac32e635b6170785f424be1099d9ca9c26d2c`
