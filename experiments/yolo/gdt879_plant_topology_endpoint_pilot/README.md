# GDT879 — plant topology endpoint pilot

Status: `REGISTERED_UNSCORED`.

The local scripts verify the three admitted source images and two native
observation packets. They preserve approximate locators and uncertainty and
require a root-owned explicit adjudication before a proceed/stop claim.

```bash
python3 experiments/yolo/gdt879_plant_topology_endpoint_pilot/src/run.py
python3 experiments/yolo/gdt879_plant_topology_endpoint_pilot/src/validate.py
```

The validator checks packet structure and adjudication support; it cannot
independently verify what an observer sees.
