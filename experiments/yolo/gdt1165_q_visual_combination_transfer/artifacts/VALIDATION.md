# GDT1165 independent validation

Phase: FINAL. Source/accounting: PASS. Registered convergence criterion: False. Checks satisfied: 40/41.

{
  "source": {
    "pages": 38,
    "leaves": 32,
    "families": 12,
    "events": 217,
    "scope_exclusions": 15,
    "presence_cells": 912,
    "DY_unknown": 8,
    "legacy_flag_comparisons": 987
  },
  "base_max_absolute_error": 0,
  "observed_folds": 152,
  "worst_observed_gradient": 4.458030101323063e-09,
  "worst_prediction_error": 7.771561172376096e-16,
  "scipy_selected_fits": [
    {
      "family": 8,
      "leaf": 2,
      "arm": "C",
      "prediction_max_error": 3.336504295070597e-09,
      "objective_difference": 1.1102230246251565e-16,
      "optimizer_success": false,
      "optimizer_message": "Desired error not necessarily achieved due to precision loss.",
      "optimizer_gradient_max": 1.407353608651185e-09
    },
    {
      "family": 8,
      "leaf": 2,
      "arm": "FULL",
      "prediction_max_error": 6.900191418246493e-09,
      "objective_difference": 3.3306690738754696e-16,
      "optimizer_success": false,
      "optimizer_message": "Desired error not necessarily achieved due to precision loss.",
      "optimizer_gradient_max": 1.5789454153869453e-09
    },
    {
      "family": 6,
      "leaf": 24,
      "arm": "C",
      "prediction_max_error": 5.889555509952515e-11,
      "objective_difference": 2.220446049250313e-16,
      "optimizer_success": true,
      "optimizer_message": "Optimization terminated successfully.",
      "optimizer_gradient_max": 8.385044394931818e-11
    },
    {
      "family": 6,
      "leaf": 24,
      "arm": "FULL",
      "prediction_max_error": 9.491296637520463e-12,
      "objective_difference": 1.1102230246251565e-16,
      "optimizer_success": false,
      "optimizer_message": "Desired error not necessarily achieved due to precision loss.",
      "optimizer_gradient_max": 5.947355984428637e-10
    },
    {
      "family": 11,
      "leaf": 56,
      "arm": "C",
      "prediction_max_error": 1.2931448689634806e-09,
      "objective_difference": 1.1102230246251565e-16,
      "optimizer_success": true,
      "optimizer_message": "Optimization terminated successfully.",
      "optimizer_gradient_max": 3.478540049864538e-11
    },
    {
      "family": 11,
      "leaf": 56,
      "arm": "FULL",
      "prediction_max_error": 5.225969657018936e-11,
      "objective_difference": 1.1102230246251565e-16,
      "optimizer_success": true,
      "optimizer_message": "Optimization terminated successfully.",
      "optimizer_gradient_max": 9.86449810724821e-11
    }
  ],
  "convergence_accounting": {
    "observed_failed": 12,
    "observed_fits": 304,
    "null_failed_declared": 2656,
    "null_fits": 60496,
    "null_gradients_independently_recomputed": false
  },
  "scientific_result": {
    "status": "NUMERICAL_FIT_FAIL",
    "T": -0.04652360685891694,
    "mean_INV_gain_C": -0.04652360685891694,
    "mean_INV_gain_ID": -0.04652360685891694,
    "positive_families": 4,
    "negative_fraction": 1.0,
    "null_rank": 0.32
  }
}

The frozen NUMERICAL_FIT_FAIL is retained. Correct accounting does not convert the invalid numerical assay into a supported or refuted scientific outcome. Observed T and rank are descriptive diagnostics only.

Failures: every_observed_fit_convex_optimality

Legacy strip_layers reused only for the expressly frozen formal DY definition.
All observed base and logistic predictions independently reconstructed; fitted coefficients checked by convex gradients.
All199 null mappings, hashes, candidate arithmetic and rank checked; their full underlying logistic fits are not independently refitted.
Selected independent SciPy solutions characterize numerical closeness only; precision-loss flags are retained and do not replace the registered fit or tolerance.
No images inspected, no source or author files changed, no semantic certification.
