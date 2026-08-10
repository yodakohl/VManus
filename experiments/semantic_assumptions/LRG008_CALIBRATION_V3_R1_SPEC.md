# LRG008 calibration v3-R1 polarity correction

Status: `FROZEN_RESULT_GATE_POLARITY_CORRECTION`.

The first v3 artifact has every scientific gate and count required by the v3
specification: 0/64 null, 8/8 full, 8/8 reduced, and 0/8 in every negative
family. It nevertheless emits `TARGET_FORBIDDEN` because the top-level gate
object contains the negatively named fact
`target_profile_or_family_surface_accessed: false` and then applies
`all(gates.values())`.

R1 must preserve every v3 world, numeric value, digest, per-world gate, pass,
count, assignment binding, input binding, and integrity result. It changes
only the top-level key/value to
`target_profile_and_family_surface_absent: true`, then recomputes status and
decision. The original v3 artifact is immutable and remains an invalid
implementation stop. No manuscript profile or family surface may be opened.
