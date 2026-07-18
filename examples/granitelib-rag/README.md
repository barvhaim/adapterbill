# IBM Granite RAG adapter examples

These examples scan real LoRA and aLoRA artifacts from [ibm-granite/granitelib-rag-r1.0](https://huggingface.co/ibm-granite/granitelib-rag-r1.0). The Hugging Face repository contains adapters for six RAG tasks and publishes a `model.sig` signature alongside each adapter.

The script pins the source repository to commit `2f0b2c79c6731068625aca8045c2eb2e8912b353`, downloads only the selected adapter directory, and scans the downloaded files locally.

## Answerability LoRA

```bash
./examples/granitelib-rag/scan.sh
```

Equivalent explicit command:

```bash
./examples/granitelib-rag/scan.sh answerability/granite-4.0-micro/lora
```

## Query-rewrite aLoRA

```bash
./examples/granitelib-rag/scan.sh query_rewrite/granite-4.0-micro/alora
```

## JSON report

Arguments after the adapter path are forwarded to AdapterBill:

```bash
./examples/granitelib-rag/scan.sh \
  citations/granite-4.1-3b/lora \
  --format json > adapterbill.json
```

Downloads are stored under `.cache/granitelib-rag-r1.0` by default. Override this location with `ADAPTERBILL_EXAMPLE_CACHE`.

AdapterBill performs static inspection only. The presence of `model.sig` is included in the file inventory, but cryptographic signature verification is not yet performed by AdapterBill.
