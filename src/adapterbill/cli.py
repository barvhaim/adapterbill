"""Command-line interface and static adapter scanner."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from adapterbill import __version__

UNSAFE_SUFFIXES = {".bin", ".ckpt", ".pkl", ".pickle", ".pt", ".pth"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _finding(severity: str, code: str, message: str) -> dict[str, str]:
    return {"severity": severity, "code": code, "message": message}


def scan_adapter(directory: Path) -> dict[str, Any]:
    """Return a deterministic static inventory and findings for an adapter directory."""
    directory = directory.resolve()
    if not directory.is_dir():
        raise ValueError(f"Adapter directory does not exist: {directory}")

    config_path = directory / "adapter_config.json"
    config: dict[str, Any] = {}
    findings: list[dict[str, str]] = []

    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            findings.append(_finding("high", "config_invalid", str(exc)))
    else:
        findings.append(
            _finding("high", "config_missing", "adapter_config.json is missing.")
        )

    files = []
    for path in sorted(p for p in directory.rglob("*") if p.is_file()):
        relative = path.relative_to(directory).as_posix()
        files.append(
            {
                "path": relative,
                "size_bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
        if path.suffix.lower() in UNSAFE_SUFFIXES:
            findings.append(
                _finding(
                    "high",
                    "unsafe_serialization",
                    f"{relative} may use executable pickle-based serialization.",
                )
            )

    base_model = config.get("base_model_name_or_path")
    base_revision = config.get("revision") or config.get("base_model_revision")
    license_name = config.get("license")
    provenance = config.get("training_data") or config.get("dataset")

    if not base_model:
        findings.append(
            _finding("high", "base_model_missing", "Base model is not declared.")
        )
    if base_model and not base_revision:
        findings.append(
            _finding("medium", "base_revision_missing", "Base model revision is not pinned.")
        )
    if not license_name:
        findings.append(
            _finding("medium", "license_missing", "Adapter license is not declared.")
        )
    if not provenance:
        findings.append(
            _finding("low", "provenance_missing", "Training-data provenance is not declared.")
        )

    target_modules = config.get("target_modules") or []
    if isinstance(target_modules, str):
        target_modules = [target_modules]

    return {
        "schema_version": "0.1",
        "adapter": {
            "path": str(directory),
            "format": config.get("peft_type", "unknown"),
            "base_model": base_model,
            "base_revision": base_revision,
            "rank": config.get("r"),
            "alpha": config.get("lora_alpha"),
            "target_modules": target_modules,
            "task_type": config.get("task_type"),
            "license": license_name,
        },
        "files": files,
        "findings": findings,
    }


def _render_terminal(report: dict[str, Any]) -> str:
    adapter = report["adapter"]
    targets = ", ".join(adapter["target_modules"]) or "UNKNOWN"
    lines = [
        f"AdapterBill scan: {adapter['path']}",
        f"Format: {adapter['format']}",
        f"Base model: {adapter['base_model'] or 'UNKNOWN'}",
        f"Base revision: {adapter['base_revision'] or 'NOT PINNED'}",
        f"Rank: {adapter['rank'] if adapter['rank'] is not None else 'UNKNOWN'}",
        f"Target modules: {targets}",
        f"Files: {len(report['files'])}",
        "",
        "Findings:",
    ]
    findings = report["findings"]
    if not findings:
        lines.append("No static metadata findings.")
    else:
        for finding in findings:
            lines.append(
                f"[{finding['severity'].upper()}] {finding['code']}: {finding['message']}"
            )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="adapterbill")
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    scan = subparsers.add_parser("scan", help="scan a local PEFT adapter directory")
    scan.add_argument("directory", type=Path)
    scan.add_argument("--format", choices=("terminal", "json"), default="terminal")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = scan_adapter(args.directory)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(_render_terminal(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
