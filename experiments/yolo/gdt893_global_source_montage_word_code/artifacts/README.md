# Reproduction and retained results

ALIM_SOURCES.json and COREMA_INTAKE.json give official source URLs and byte
hashes. Store eight ALIM text downloads as alim<ID>.txt and the six COREMA XMLs
as <name>.recipes.xml. Full modern editions are not republished here.

From the repository root (arguments denote chosen working directories):

```sh
python3 experiments/yolo/gdt893_global_source_montage_word_code/src/source.py --cache-dir ALIM_CACHE --corema-dir COREMA_CACHE --output SOURCE_UNITS.json
python3 experiments/yolo/gdt893_global_source_montage_word_code/src/prepare_cpp.py --source-units SOURCE_UNITS.json --output-dir FIT_DIRECTORY
python3 experiments/yolo/gdt893_global_source_montage_word_code/src/run_cpp.py --fit-dir FIT_DIRECTORY --budget-seconds 1500
```

INPUT_LOCK and CANDIDATE_LOCK bind the deterministic source/target packet and
all complete candidate records. Candidate provenance aliases are retained.
The frozen constraint records plus each proved maximum represent the entire
optimum family; solve_projection --member INPUT WEIGHT INDEX... checks members.
It does not independently prove maximality. No IT family is called complete.

Independent validate_windows.cpp enumerates every local bijective window;
validate_optima.cpp enumerates all optimum sets when feasible;
validate_projection.cpp separately proves maximum and universal projection.
validate_symbolic.py compares primary certificates with those independent
results. Source/constraint hashes and compact witnesses are published here.
Old large explicit families remain reproducible from bound inputs and their
unchanged enumerators; their hashes/counts and parity receipts are preserved.
Runtime can vary; timeout yields unknown, never an optimum or uniqueness claim.
