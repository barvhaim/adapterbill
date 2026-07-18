# AdapterBill

**A bill of materials for LoRA and PEFT adapters.**

AdapterBill statically inspects an adapter directory before you load it. It inventories files, hashes artifacts, reads PEFT configuration, and flags missing provenance or potentially unsafe serialized files.

## Quick start

```bash
uv sync --locked
uv run adapterbill scan examples/minimal-adapter
uv run adapterbill scan examples/minimal-adapter --format json
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

## Real-world Granite examples

Scan signed LoRA and aLoRA artifacts from [IBM Granite's RAG adapter library](https://huggingface.co/ibm-granite/granitelib-rag-r1.0):

```bash
./examples/granitelib-rag/scan.sh
./examples/granitelib-rag/scan.sh query_rewrite/granite-4.0-micro/alora
```

The examples pin the Hugging Face repository revision and download only the selected adapter directory. See [`examples/granitelib-rag`](examples/granitelib-rag) for additional variants and JSON output.

## Development

```bash
uv sync --locked
uv run python -m unittest discover -s tests -v
uv build
```

## License

MIT
