# AdapterBill

**A bill of materials for LoRA and PEFT adapters.**

AdapterBill statically inspects an adapter directory before you load it. It inventories files, hashes artifacts, reads PEFT configuration, and flags missing provenance or potentially unsafe serialized files.

## Quick start

```bash
python -m pip install -e .
adapterbill scan examples/minimal-adapter
adapterbill scan examples/minimal-adapter --format json
```

Example output:

```text
AdapterBill scan: examples/minimal-adapter
Format: PEFT LoRA
Base model: example/base-model
Base revision: NOT PINNED
Rank: 8
Target modules: q_proj, v_proj
Files: 1

Findings:
[MEDIUM] base_revision_missing: Base model revision is not pinned.
[MEDIUM] license_missing: Adapter license is not declared.
```

## Current checks

- SHA-256 inventory for every file
- PEFT/LoRA configuration extraction
- Base-model and revision declaration
- License and provenance declaration
- Potentially unsafe pickle or executable weight formats
- Machine-readable JSON output

AdapterBill reports deterministic metadata and risk signals. It does not certify that an adapter is safe or provide legal advice.

## Development

```bash
python -m unittest discover -s tests -v
```

## License

MIT
