# Source retention and reproduction

The three released article figures and four correctly localized native pixel
strips are included. Source URLs, hashes, coordinates and credit are in the
source JSON records. The original 18,969,779-byte JPEG is publicly downloadable
through the URL in NATIVE_SOURCE.json and is hash-checked before optional replay.

The four initially mislocalized PNGs are excluded from publication to avoid
32MB of calibration-area duplicates. Their original coordinate/hash receipts
and both reading/error records are preserved. The excluded image bytes were
retained outside the repository during this session. These paths in the original
receipt name optional reproducible artifacts, not missing required inputs.
No legacy tracked bytes were removed. PNG compression can vary by library;
pixel equality to the fixed JPEG is the relevant reproduction invariant.

From the repository root:

```sh
python3 experiments/yolo/gdt912_f1r_progressive_key/src/run.py
python3 experiments/yolo/gdt912_f1r_progressive_key/src/validate.py
```

Download the public original separately as `native_source.jpg`. For actual
source-pixel verification or optional recreation (Python3 and Pillow):

```sh
python3 experiments/yolo/gdt912_f1r_progressive_key/src/validate.py --native-source native_source.jpg
python3 experiments/yolo/gdt912_f1r_progressive_key/src/reproduce_crops.py native_source.jpg recreated_crops --include-mislocalized
```

The recorded validation checked all four corrected panels against the original.
The default replay does not fetch or inspect further source images and reports
zero additional original-pixel checks; it preserves that stronger recorded run.
Native-image credit: The Lazarus Project and the Chester F. Carlson Center for
Imaging Science at Rochester Institute of Technology; Beinecke MS408 f1r.
