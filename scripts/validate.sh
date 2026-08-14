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
skills_catalog_path = root / "catalog" / "skills-sh-top-50.json"
metadata_path = root / "catalog" / "skills-sh-metadata.json"
anthropic_descriptions_path = root / "catalog" / "anthropic-description-zh.json"
localization_details_path = root / "catalog" / "plugin-description-localization.json"
if not all(path.is_file() for path in (report_path, provenance_path, license_report_path, trust_report_path, skills_catalog_path, metadata_path, anthropic_descriptions_path, localization_details_path)):
    raise SystemExit("missing sync, provenance, license, or trust-boundary report")
report = json.loads(report_path.read_text(encoding="utf-8"))
provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
skills_catalog = json.loads(skills_catalog_path.read_text(encoding="utf-8"))
skills_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
anthropic_descriptions = json.loads(anthropic_descriptions_path.read_text(encoding="utf-8"))
localization_details = json.loads(localization_details_path.read_text(encoding="utf-8"))
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
def has_chinese(value):
    return any("\u4e00" <= char <= "\u9fff" for char in value or "")

missing_chinese_descriptions = [plugin.get("name") for plugin in plugins if not has_chinese(plugin.get("description"))]
if missing_chinese_descriptions:
    raise SystemExit(f"marketplace contains non-Chinese descriptions: {missing_chinese_descriptions[:5]}")
if not isinstance(anthropic_descriptions, dict):
    raise SystemExit("Anthropic 中文描述目录必须是对象")
if not isinstance(localization_details, list):
    raise SystemExit("插件描述本地化记录必须是数组")
runtime_manifest_failures = []
for plugin_root in (root / "plugins" / "anthropic", root / "plugins" / "skills-sh"):
    for plugin_dir in plugin_root.iterdir():
        if not plugin_dir.is_dir():
            continue
        manifest = next(
            (plugin_dir / relative for relative in ("plugin.json", ".grok-plugin/plugin.json", ".claude-plugin/plugin.json") if (plugin_dir / relative).is_file()),
            None,
        )
        if manifest is None:
            continue
        value = json.loads(manifest.read_text(encoding="utf-8"))
        if not has_chinese(value.get("description")):
            runtime_manifest_failures.append(manifest.relative_to(root).as_posix())
if runtime_manifest_failures:
    raise SystemExit(f"Grok-readable plugin manifests contain non-Chinese descriptions: {runtime_manifest_failures[:5]}")
ranked_entries = [plugin for plugin in plugins if plugin.get("source", "").startswith("./plugins/skills-sh/")]
if len(ranked_entries) != 50:
    raise SystemExit(f"marketplace does not expose exactly 50 ranked skills.sh entries: {len(ranked_entries)}")
for expected, plugin in zip(skills_catalog.get("skills", []), ranked_entries):
    metadata = skills_metadata.get(expected.get("skill"), {"capability_type": "开发与工程"})
    if not plugin.get("category") or not metadata.get("capability_type"):
        raise SystemExit(f"skills.sh entry is missing capability type: {plugin.get('name')}")
    expected_prefix = (
        f"能力类型：{metadata['capability_type']}；"
        f"下载次数：{expected.get('installs'):,}；"
        f"skills.sh 排名：第 {expected.get('rank')} 名。"
    )
    if not plugin.get("description", "").startswith(expected_prefix):
        raise SystemExit(f"skills.sh entry description metadata is inconsistent: {plugin.get('name')}")
        raise SystemExit(f"skills.sh entry does not display downloads: {plugin.get('name')}")
    skill_paths = plugin.get("skills")
    if not isinstance(skill_paths, list) or len(skill_paths) != 1:
        raise SystemExit(f"skills.sh entry must select exactly one skill: {plugin.get('name')}")
    source_root = (root / plugin["source"].removeprefix("./")).resolve()
    skill_root = (source_root / skill_paths[0].removeprefix("./")).resolve()
    if source_root not in skill_root.parents or not skill_root.is_dir():
        raise SystemExit(f"skills.sh entry points to a missing skill: {plugin.get('name')}")
missing_hashes = [item.get("name") for item in provenance if item.get("status") == "mirrored" and not re.fullmatch(r"[0-9a-f]{64}", item.get("content_sha256", ""))]
if missing_hashes:
    raise SystemExit(f"provenance records are missing content hashes: {missing_hashes[:5]}")
license_report = json.loads(license_report_path.read_text(encoding="utf-8"))
if len(license_report.get("packages", [])) != len([item for item in provenance if item.get("status") == "mirrored"]):
    raise SystemExit("license report does not cover every mirrored package")
print(f"local marketplace validation passed: {len(plugins)} entries, {anthropic_actual} Anthropic plugins, {skills_actual} ranked skills.sh skills")
PY

if command -v claude >/dev/null 2>&1 && claude plugin validate --help >/dev/null 2>&1; then
  claude plugin validate "${MARKETPLACE_ROOT}"
else
  echo "warning: Claude Code marketplace validation is unavailable; local validation passed" >&2
fi
