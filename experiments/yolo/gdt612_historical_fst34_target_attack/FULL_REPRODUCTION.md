# GDT612 full reproduction

Run from the repository root. Generated references, binaries and multi-megabyte
decode tables stay in a disposable scratch directory.

```sh
gdt612_work=$(mktemp -d)
cp experiments/yolo/gdt612_historical_fst34_target_attack/src/full/* "$gdt612_work/"
python3 experiments/yolo/gdt604_naibbe_frozen_target_attack/src/fetch_references.py \
  --output-dir "$gdt612_work/references"
VMANUS_REPO_ROOT="$PWD" GDT612_WORK="$gdt612_work" python3 "$gdt612_work/prepare.py"
VMANUS_REPO_ROOT="$PWD" GDT612_WORK="$gdt612_work" python3 "$gdt612_work/make_synthetic.py"
g++ -O3 -std=c++17 -Wall -Wextra -pedantic "$gdt612_work/decoder.cpp" -o "$gdt612_work/decoder"
GDT612_WORK="$gdt612_work" python3 "$gdt612_work/run_all.py" synthetic --workers 6
GDT612_WORK="$gdt612_work" python3 "$gdt612_work/run_all.py" target --workers 12
GDT612_WORK="$gdt612_work" python3 "$gdt612_work/evaluate.py"
GDT612_WORK="$gdt612_work" python3 "$gdt612_work/summarize.py"
VMANUS_REPO_ROOT="$PWD" GDT612_WORK="$gdt612_work" python3 "$gdt612_work/full_validate.py"
```

Compare the generated `ARTIFACT_MANIFEST.tsv` with
`artifacts/FULL_RUN_MANIFEST.tsv`. Runtime JSON and reports contain elapsed-time
or source-path differences; the fitted maps and evaluation tables are the
deterministic scientific payload.
