# Receipt correction: E-detail crop hash

Correction recorded 2026-09-27T00:07:37Z. The frozen `HONEY_QOD_NATIVE_RECEIPTS.json` incorrectly records the SHA-256 of `honey_qod_E_text.png` as `00ae58bb2ea20a845cdfe37b2c20afe8dc3ac002baf506d42b93183ea9f77ffa`. That value has the same trailing characters as the full-E crop and is not the saved E-detail file’s hash.

The saved, inspected file `honey_qod_E_text.png` hashes to **`00ae58bb2ea20a845cdfe37b2c20afe8dc3ac002baf506d42b9313aa8c2f39e8`**. Its crop box in parent coordinates is `(1800, 800, 2400, 1900)` (xyxy); dimensions are 600×1100 px. The exact operation was Pillow `Image.open(parent).crop((1800,800,2400,1900)).save(output, format="PNG")`, using default PNG encoding. The temporary output directory is omitted; only the basename is retained here.

Provenance was checked without viewing pixels again: the saved PNG has the stated dimensions and its decoded pixels compare equal to the corresponding crop of the admitted parent image. The parent hash remains `9a65d78de2a0d7941fb33c09def73a30a189371109f6ec2753c4c1b9b15fd229`. The other five crop files’ hashes and dimensions match the frozen receipt, and each decoded crop is pixel-equal to its recorded parent coordinates. All six boxes lie within the 2400×3112 rendition.

This addendum preserves the original receipt bytes and corrects only the E-detail file digest. It does not repeat native interpretation or change the report’s uncertainty conclusion.
