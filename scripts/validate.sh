#!/usr/bin/env bash
set -euo pipefail

MARKETPLACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 - "${MARKETPLACE_ROOT}" <<'PY'
import json
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1])
manifest_path = root / ".claude-plugin" / "marketplace.json"
if not manifest_path.is_file():
    raise SystemExit("missing .claude-plugin/marketplace.json")
marketplace = json.loads(manifest_path.read_text(encoding="utf-8"))
if marketplace.get("name") != "jlbank-plugin-marketplace":
    raise SystemExit("unexpected marketplace name")
plugins = marketplace.get("plugins")
if not isinstance(plugins, list) or not plugins:
    raise SystemExit("marketplace has no plugins")
names = [plugin.get("name") for plugin in plugins]
if any(not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name or "") for name in names):
    raise SystemExit("marketplace contains an invalid plugin name")
if len(names) != len(set(names)):
    raise SystemExit("marketplace contains duplicate plugin names")

missing = []
external = []
for plugin in plugins:
    source = plugin.get("source")
    if not isinstance(source, str) or not source.startswith("./plugins/"):
        external.append((plugin["name"], source))
        continue
    target = (root / source.removeprefix("./")).resolve()
    if root.resolve() not in target.parents or not target.is_dir():
        missing.append((plugin["name"], source))
if external:
    raise SystemExit(f"marketplace contains non-local plugin sources: {external[:5]}")
if missing:
    raise SystemExit(f"marketplace contains missing plugin sources: {missing[:5]}")

report_path = root / "catalog" / "sync-report.json"
provenance_path = root / "catalog" / "provenance.json"
license_report_path = root / "catalog" / "license-report.json"
trust_report_path = root / "catalog" / "trust-boundaries.json"
if not all(path.is_file() for path in (report_path, provenance_path, license_report_path, trust_report_path)):
    raise SystemExit("missing sync, provenance, license, or trust-boundary report")
report = json.loads(report_path.read_text(encoding="utf-8"))
provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
if report.get("failed_records"):
    raise SystemExit(f"sync report contains {report['failed_records']} failures")

anthropic_expected = report.get("anthropic", {}).get("expected", 0)
anthropic_actual = sum(item.get("kind") == "anthropic-marketplace" and item.get("status") == "mirrored" for item in provenance)
skills_expected = report.get("skills_sh", {}).get("expected_skills", 0)
skills_actual = sum(len(item.get("skills", [])) for item in provenance if item.get("kind") == "skills.sh" and item.get("status") == "mirrored")
if anthropic_actual != anthropic_expected:
    raise SystemExit(f"Anthropic mirror incomplete: {anthropic_actual}/{anthropic_expected}")
if skills_actual != skills_expected:
    raise SystemExit(f"skills.sh mirror incomplete: {skills_actual}/{skills_expected}")
missing_hashes = [item.get("name") for item in provenance if item.get("status") == "mirrored" and not re.fullmatch(r"[0-9a-f]{64}", item.get("content_sha256", ""))]
if missing_hashes:
    raise SystemExit(f"provenance records are missing content hashes: {missing_hashes[:5]}")
license_report = json.loads(license_report_path.read_text(encoding="utf-8"))
if len(license_report.get("packages", [])) != len([item for item in provenance if item.get("status") == "mirrored"]):
    raise SystemExit("license report does not cover every mirrored package")
print(f"local marketplace validation passed: {len(plugins)} packages, {anthropic_actual} Anthropic plugins, {skills_actual} skills.sh skills")
PY

if command -v claude >/dev/null 2>&1 && claude plugin validate --help >/dev/null 2>&1; then
  claude plugin validate "${MARKETPLACE_ROOT}"
else
  echo "warning: Claude Code marketplace validation is unavailable; local validation passed" >&2
fi
