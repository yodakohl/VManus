# GDT1312 binary whole-group capacity

Read REPORT.md for the codebook-only scope. No native source-character values are assigned.

From repository root:
`PYTHONDONTWRITEBYTECODE=1 python experiments/yolo/gdt1312_binary_whole_code_capacity/src/reproduce.py run`

Independent exhaustive verification:
`PYTHONDONTWRITEBYTECODE=1 python experiments/yolo/gdt1312_binary_whole_code_capacity/src/reproduce.py validate`

Requires Python with NumPy and a C++17 compiler. Executables use a disposable temporary directory outside the checkout and are not published. COUNT_FORMAT.json describes the compressed exhaustive arrays and the excluded zero-mask reference.
