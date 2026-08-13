#!/usr/bin/env python3
"""Build a pinned, local-only Claude Code marketplace mirror."""

from __future__ import annotations

import argparse
import concurrent.futures
import contextlib
import datetime as dt
import hashlib
import html
import json
import os
import pathlib
import re
import shutil
import subprocess
import tarfile
import tempfile
import threading
import time
import urllib.parse
import urllib.request
import zipfile
from typing import Any, Dict, Iterable, List, Optional, Tuple


ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / ".sync-cache"
WORK = ROOT / ".sync-work"
CATALOG = ROOT / "catalog"
PLUGINS = ROOT / "plugins"
MARKETPLACE_PATH = ROOT / ".claude-plugin" / "marketplace.json"

ANTHROPIC_REPOSITORY = "https://github.com/anthropics/claude-plugins-official"
ANTHROPIC_API = "https://api.github.com/repos/anthropics/claude-plugins-official"
SKILLS_SH_HOME = "https://www.skills.sh/"

PRINT_LOCK = threading.Lock()


def log(message: str) -> None:
    with PRINT_LOCK:
        print(message, flush=True)


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def write_json(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(data)
        os.replace(temporary, path)
    except BaseException:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(temporary)
        raise


def request_bytes(url: str, accept: str = "application/octet-stream") -> bytes:
    headers = {"Accept": accept, "User-Agent": "jlbank-plugin-marketplace-sync"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token and "github" in urllib.parse.urlsplit(url).netloc:
        headers["Authorization"] = f"Bearer {token}"
    last_error: Optional[BaseException] = None
    for attempt in range(4):
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=120) as response:
                return response.read()
        except BaseException as error:
            last_error = error
            if attempt < 3:
                time.sleep(2**attempt)
    assert last_error is not None
    raise last_error


def request_json(url: str) -> Any:
    return json.loads(request_bytes(url, "application/vnd.github+json"))


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_sha256(root: pathlib.Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        if path.is_symlink():
            digest.update(b"L\0" + relative + b"\0" + os.readlink(path).encode("utf-8") + b"\0")
        elif path.is_file():
            digest.update(b"F\0" + relative + b"\0")
            with path.open("rb") as source:
                for chunk in iter(lambda: source.read(1024 * 1024), b""):
                    digest.update(chunk)
    return digest.hexdigest()


def trust_boundaries(destination: pathlib.Path) -> Dict[str, Any]:
    result: Dict[str, Any] = {"hooks": [], "mcp": [], "lsp": [], "executables": []}
    for path in destination.rglob("*"):
        if path.is_symlink() or not path.is_file():
            continue
        relative = path.relative_to(destination).as_posix()
        name = path.name.lower()
        if name == "hooks.json" or "/hooks/" in f"/{relative.lower()}/":
            result["hooks"].append(relative)
        if name == ".mcp.json" or name.endswith("mcp.json"):
            result["mcp"].append(relative)
        if name == ".lsp.json" or name.endswith("lsp.json"):
            result["lsp"].append(relative)
        if os.access(path, os.X_OK):
            result["executables"].append(relative)
    return {key: value for key, value in result.items() if value}


def safe_name(value: str, maximum: int = 80) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "item"
    if len(normalized) <= maximum:
        return normalized
    suffix = hashlib.sha256(value.encode()).hexdigest()[:10]
    return f"{normalized[: maximum - 11].rstrip('-')}-{suffix}"


def github_coordinates(url: str) -> Optional[Tuple[str, str]]:
    value = url.removesuffix(".git")
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value.split(":", 1)[1]
    parsed = urllib.parse.urlsplit(value)
    if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
        return None
    parts = [part for part in parsed.path.split("/") if part]
    return (parts[0], parts[1]) if len(parts) >= 2 else None


def download_github_archive(owner: str, repo: str, commit: str) -> pathlib.Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    archive = CACHE / f"{safe_name(owner)}--{safe_name(repo)}--{commit}.tar.gz"
    if archive.is_file() and archive.stat().st_size > 0:
        return archive
    url = f"https://codeload.github.com/{owner}/{repo}/tar.gz/{commit}"
    data = request_bytes(url)
    temporary = archive.with_suffix(".tmp")
    temporary.write_bytes(data)
    if not tarfile.is_tarfile(temporary):
        temporary.unlink(missing_ok=True)
        raise RuntimeError(f"invalid GitHub archive for {owner}/{repo}@{commit}")
    os.replace(temporary, archive)
    return archive


def safe_extract(archive: pathlib.Path, destination: pathlib.Path) -> pathlib.Path:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    resolved = destination.resolve()
    with tarfile.open(archive, "r:gz") as bundle:
        for member in bundle.getmembers():
            target = (destination / member.name).resolve()
            if target != resolved and resolved not in target.parents:
                raise RuntimeError(f"archive path traversal: {member.name}")
            if member.issym() or member.islnk():
                link = pathlib.PurePosixPath(member.linkname)
                link_target = (target.parent / member.linkname).resolve()
                if link.is_absolute() or (link_target != resolved and resolved not in link_target.parents):
                    raise RuntimeError(f"unsafe archive link: {member.name} -> {member.linkname}")
        bundle.extractall(destination)
    roots = [item for item in destination.iterdir() if item.is_dir()]
    if len(roots) != 1:
        raise RuntimeError(f"archive has {len(roots)} roots: {archive}")
    return roots[0]


def copy_mirror(source: pathlib.Path, destination: pathlib.Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, symlinks=True, ignore=shutil.ignore_patterns(".git"))


def copy_license_files(source_root: pathlib.Path, destination: pathlib.Path) -> List[str]:
    copied: List[str] = []
    license_root = destination / "THIRD_PARTY_LICENSES"
    for item in source_root.iterdir():
        if not item.is_file():
            continue
        if not re.match(r"^(?:licen[cs]e|notice|copying|copyright)(?:[._-].*)?$", item.name, re.IGNORECASE):
            continue
        license_root.mkdir(parents=True, exist_ok=True)
        target = license_root / item.name
        shutil.copy2(item, target)
        copied.append(target.relative_to(ROOT).as_posix())
    return copied


def git_head(owner: str, repo: str) -> str:
    command = ["gh", "api", f"repos/{owner}/{repo}/commits/HEAD", "--jq", ".sha"]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=45)
        commit = result.stdout.strip()
    except (FileNotFoundError, subprocess.SubprocessError):
        command = ["git", "ls-remote", f"https://github.com/{owner}/{repo}.git", "HEAD"]
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=90)
        commit = result.stdout.split()[0]
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise RuntimeError(f"cannot resolve {owner}/{repo} HEAD")
    return commit


def source_repository(entry: Dict[str, Any]) -> Tuple[str, Optional[str], Optional[str]]:
    source = entry["source"]
    if isinstance(source, str):
        return ANTHROPIC_REPOSITORY, source.removeprefix("./"), None
    kind = source.get("source")
    if kind == "github":
        repository = source.get("repo") or source.get("repository")
        return f"https://github.com/{repository}", source.get("path"), source.get("sha") or source.get("commit") or source.get("ref")
    return source["url"], source.get("path"), source.get("sha") or source.get("ref")


def load_anthropic_catalog() -> Tuple[Dict[str, Any], str, str]:
    commit_data = request_json(f"{ANTHROPIC_API}/commits/main")
    commit = commit_data["sha"]
    commit_date = commit_data["commit"]["committer"]["date"]
    raw = request_bytes(
        f"https://raw.githubusercontent.com/anthropics/claude-plugins-official/{commit}/.claude-plugin/marketplace.json"
    )
    catalog = json.loads(raw)
    if catalog.get("name") != "claude-plugins-official":
        raise RuntimeError("unexpected Anthropic marketplace name")
    write_json(CATALOG / "anthropic-upstream.json", catalog)
    return catalog, commit, commit_date


def mirror_anthropic_entry(
    entry: Dict[str, Any], official_root: pathlib.Path, official_commit: str
) -> Dict[str, Any]:
    name = entry["name"]
    destination = PLUGINS / "anthropic" / name
    repository, subpath, revision = source_repository(entry)
    if repository == ANTHROPIC_REPOSITORY:
        source_root = official_root
        pinned = official_commit
    else:
        coordinates = github_coordinates(repository)
        if not coordinates:
            raise RuntimeError(f"unsupported non-GitHub source: {repository}")
        owner, repo = coordinates
        pinned = revision if revision and re.fullmatch(r"[0-9a-f]{40}", revision) else git_head(owner, repo)
        archive = download_github_archive(owner, repo, pinned)
        extraction = WORK / "anthropic" / f"{safe_name(owner)}--{safe_name(repo)}--{pinned}"
        source_root = safe_extract(archive, extraction)
    source_path = source_root / (subpath or "")
    if not source_path.exists():
        raise RuntimeError(f"source path not found: {repository}@{pinned}:{subpath or '.'}")
    copy_mirror(source_path, destination)
    licenses = copy_license_files(source_root, destination)
    return {
        "kind": "anthropic-marketplace",
        "name": name,
        "upstream_repository": repository,
        "upstream_path": subpath,
        "upstream_revision": pinned,
        "local_path": destination.relative_to(ROOT).as_posix(),
        "license_files": licenses,
        "content_sha256": tree_sha256(destination),
        "trust_boundaries": trust_boundaries(destination),
        "status": "mirrored",
    }


SKILL_PATTERN = re.compile(
    r'\\"source\\":\\"(?P<source>[^"\\]+)\\",'
    r'\\"skillId\\":\\"(?P<skill>[^"\\]+)\\",'
    r'\\"name\\":\\"(?P<name>[^"\\]+)\\",'
    r'\\"installs\\":(?P<installs>\d+)'
)


def load_skills_leaderboard(limit: int) -> List[Dict[str, Any]]:
    page = request_bytes(SKILLS_SH_HOME, "text/html").decode("utf-8")
    results: List[Dict[str, Any]] = []
    seen = set()
    for match in SKILL_PATTERN.finditer(page):
        source = html.unescape(match.group("source"))
        skill = html.unescape(match.group("skill"))
        key = (source, skill)
        if key in seen:
            continue
        seen.add(key)
        results.append(
            {
                "rank": len(results) + 1,
                "source": source,
                "skill": skill,
                "name": html.unescape(match.group("name")),
                "installs": int(match.group("installs")),
                "url": f"https://www.skills.sh/{source}/{urllib.parse.quote(skill, safe='')}",
            }
        )
        if len(results) == limit:
            break
    if len(results) != limit:
        raise RuntimeError(f"skills.sh exposed {len(results)} entries, expected Top {limit}")
    write_json(
        CATALOG / f"skills-sh-top-{limit}.json",
        {"source": SKILLS_SH_HOME, "collected_at": now(), "limit": limit, "skills": results},
    )
    return results


def frontmatter_name(skill_file: pathlib.Path) -> Optional[str]:
    try:
        prefix = skill_file.read_text(encoding="utf-8", errors="replace")[:12000]
    except OSError:
        return None
    if not prefix.startswith("---"):
        return None
    match = re.search(r"^name:\s*['\"]?([^'\"\n]+)", prefix, re.MULTILINE)
    return match.group(1).strip() if match else None


def find_skill(root: pathlib.Path, skill: str, name: str) -> pathlib.Path:
    candidates = list(root.rglob("SKILL.md"))
    exact_directory = [item.parent for item in candidates if item.parent.name == skill]
    if exact_directory:
        exact_directory.sort(key=lambda item: (len(item.parts), item.as_posix()))
        return exact_directory[0]
    exact_name = [item.parent for item in candidates if frontmatter_name(item) in {skill, name}]
    if exact_name:
        exact_name.sort(key=lambda item: (len(item.parts), item.as_posix()))
        return exact_name[0]
    suffix = [item.parent for item in candidates if item.parent.as_posix().endswith("/" + skill)]
    if len(suffix) == 1:
        return suffix[0]
    raise RuntimeError(
        f"cannot uniquely locate skill {skill!r}: dir={len(exact_directory)} frontmatter={len(exact_name)}"
    )


def decode_html_text(value: str) -> str:
    value = re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE)
    value = re.sub(r"</(?:p|li|h[1-6]|pre|blockquote)>", "\n", value, flags=re.IGNORECASE)
    value = re.sub(r"<[^>]+>", "", value)
    return html.unescape(value).strip()


def decode_next_string(value: str) -> str:
    return json.loads('"' + value + '"')


def mirror_skill_from_page(entry: Dict[str, Any], target: pathlib.Path) -> None:
    page = request_bytes(entry["url"], "text/html").decode("utf-8", errors="replace")
    marker = '<span>SKILL.md</span>'
    start = page.find(marker)
    if start < 0:
        raise RuntimeError(f"skills.sh page has no SKILL.md section: {entry['url']}")
    section = page[start:]
    end = section.find('class=" lg:col-span-3"')
    if end > 0:
        section = section[:end]
    prose = re.search(r'<div class="prose[^>]*>(.*?)</div></div></div>', section, re.DOTALL)
    if prose:
        rendered = prose.group(1)
    else:
        chunks = re.search(
            r'\\"previewHtml\\":\\"((?:[^"\\]|\\.)*)\\",\\"restHtml\\":\\"((?:[^"\\]|\\.)*)\\"',
            page,
            re.DOTALL,
        )
        if not chunks:
            raise RuntimeError(f"cannot extract SKILL.md preview from {entry['url']}")
        rendered = decode_next_string(chunks.group(1)) + decode_next_string(chunks.group(2))
    body = decode_html_text(rendered)
    if not body:
        raise RuntimeError(f"empty SKILL.md preview from {entry['url']}")
    target.mkdir(parents=True, exist_ok=True)
    content = (
        "---\n"
        f"name: {safe_name(entry['name'])}\n"
        f"description: Popular skill mirrored from {entry['url']}.\n"
        "---\n\n"
        f"{body}\n"
    )
    (target / "SKILL.md").write_text(content, encoding="utf-8")


def mirror_well_known_skill(source: str, entry: Dict[str, Any], target: pathlib.Path) -> None:
    index_url = f"https://{source}/.well-known/skills/index.json"
    index = request_json(index_url)
    definition = next((item for item in index.get("skills", []) if item.get("name") == entry["skill"]), None)
    if not definition:
        raise RuntimeError(f"well-known index does not contain {entry['skill']}: {index_url}")
    target.mkdir(parents=True, exist_ok=True)
    if definition.get("type") == "archive" and definition.get("url"):
        archive_url = urllib.parse.urljoin(index_url, definition["url"])
        archive_data = request_bytes(archive_url)
        expected = str(definition.get("digest", "")).removeprefix("sha256:")
        if expected and hashlib.sha256(archive_data).hexdigest() != expected:
            raise RuntimeError(f"well-known archive digest mismatch: {archive_url}")
        archive_path = WORK / "well-known" / f"{safe_name(source)}--{safe_name(entry['skill'])}.zip"
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        archive_path.write_bytes(archive_data)
        with zipfile.ZipFile(archive_path) as bundle:
            resolved = target.resolve()
            for member in bundle.infolist():
                destination = (target / member.filename).resolve()
                if destination != resolved and resolved not in destination.parents:
                    raise RuntimeError(f"well-known archive path traversal: {member.filename}")
            bundle.extractall(target)
        nested_skill = list(target.rglob("SKILL.md"))
        if not (target / "SKILL.md").is_file() and len(nested_skill) == 1:
            nested_root = nested_skill[0].parent
            temporary = target.with_name(target.name + ".nested")
            if temporary.exists():
                shutil.rmtree(temporary)
            os.replace(nested_root, temporary)
            shutil.rmtree(target)
            os.replace(temporary, target)
    elif definition.get("url"):
        file_url = urllib.parse.urljoin(index_url, definition["url"])
        file_data = request_bytes(file_url)
        expected = str(definition.get("digest", "")).removeprefix("sha256:")
        if expected and hashlib.sha256(file_data).hexdigest() != expected:
            raise RuntimeError(f"well-known file digest mismatch: {file_url}")
        (target / "SKILL.md").write_bytes(file_data)
    else:
        files = definition.get("files") or ["SKILL.md"]
        for relative in files:
            parts = pathlib.PurePosixPath(relative).parts
            if not parts or ".." in parts:
                raise RuntimeError(f"unsafe well-known file path: {relative}")
            url = f"https://{source}/.well-known/skills/{urllib.parse.quote(entry['skill'], safe='')}/{urllib.parse.quote(relative, safe='/')}"
            destination = target.joinpath(*parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(request_bytes(url))
    if not (target / "SKILL.md").is_file():
        raise RuntimeError(f"well-known skill has no SKILL.md: {source}/{entry['skill']}")


def ensure_plugin_manifest(destination: pathlib.Path, plugin_name: str, source: str) -> None:
    manifest = destination / ".claude-plugin" / "plugin.json"
    if manifest.exists():
        return
    write_json(
        manifest,
        {
            "name": plugin_name,
            "version": "0.0.0-mirror",
            "description": f"JLBank mirror of popular skills from {source}.",
            "author": {"name": source},
        },
    )


def mirror_skill_source(source: str, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    source_overrides = {"sentry/dev": "cli.sentry.dev"}
    github_overrides = {"skills.volces.com": "bytedance/agentkit-samples"}
    well_known_source = source_overrides.get(source)
    github_source = github_overrides.get(source, source)
    is_github = well_known_source is None and "/" in github_source and "." not in github_source.split("/", 1)[0]
    plugin_name = safe_name(f"skillsh-{source}", 64)
    destination = PLUGINS / "skills-sh" / plugin_name
    if destination.exists():
        shutil.rmtree(destination)
    (destination / "skills").mkdir(parents=True)
    mirrored = []
    commit: Optional[str] = None
    source_root: Optional[pathlib.Path] = None
    repository = source
    source_error: Optional[str] = None
    if is_github:
        owner, repo = github_source.split("/", 1)
        repository = f"https://github.com/{github_source}"
        try:
            commit = git_head(owner, repo)
            archive = download_github_archive(owner, repo, commit)
            extraction = WORK / "skills-sh" / f"{safe_name(owner)}--{safe_name(repo)}--{commit}"
            source_root = safe_extract(archive, extraction)
        except Exception as error:
            source_error = str(error)
    for entry in entries:
        target_name = safe_name(entry["skill"])
        target = destination / "skills" / target_name
        if target.exists():
            target_name = f"{target_name}-{hashlib.sha256(entry['skill'].encode()).hexdigest()[:8]}"
            target = destination / "skills" / target_name
        mirror_mode = "page-snapshot"
        if source_root is not None:
            try:
                skill_source = find_skill(source_root, entry["skill"], entry["name"])
                copy_mirror(skill_source, target)
                mirror_mode = "repository"
            except RuntimeError:
                mirror_skill_from_page(entry, target)
        else:
            mirror_well_known_skill(well_known_source or source, entry, target)
            mirror_mode = "well-known"
        mirrored.append({**entry, "mirror_mode": mirror_mode, "local_skill_path": target.relative_to(ROOT).as_posix()})
    ensure_plugin_manifest(destination, plugin_name, source)
    licenses = copy_license_files(source_root, destination) if source_root is not None else []
    return {
        "kind": "skills.sh",
        "name": plugin_name,
        "upstream_repository": repository,
        "upstream_revision": commit,
        "repository_error": source_error,
        "local_path": destination.relative_to(ROOT).as_posix(),
        "license_files": licenses,
        "content_sha256": tree_sha256(destination),
        "trust_boundaries": trust_boundaries(destination),
        "skills": mirrored,
        "status": "mirrored",
    }


def marketplace_entry(original: Dict[str, Any], local_path: str) -> Dict[str, Any]:
    result = {key: value for key, value in original.items() if key not in {"source", "displayName"}}
    result["source"] = f"./{local_path}"
    return result


def build_marketplace(
    anthropic_catalog: Optional[Dict[str, Any]], provenance: List[Dict[str, Any]]
) -> None:
    by_name = {item["name"]: item for item in provenance if item.get("status") == "mirrored"}
    plugins: List[Dict[str, Any]] = []
    if anthropic_catalog:
        for entry in anthropic_catalog["plugins"]:
            record = by_name.get(entry["name"])
            if record:
                plugins.append(marketplace_entry(entry, record["local_path"]))
    for record in sorted(provenance, key=lambda item: item.get("name", "")):
        if record.get("kind") == "skills.sh" and record.get("status") == "mirrored":
            skills_entry = {
                    "name": record["name"],
                    "description": f"Popular skills mirrored from {record['upstream_repository']}.",
                    "source": f"./{record['local_path']}",
                    "category": "development",
                }
            homepage = record.get("upstream_repository")
            if isinstance(homepage, str) and homepage.startswith(("http://", "https://")):
                skills_entry["homepage"] = homepage
            plugins.append(skills_entry)
    names = [entry["name"] for entry in plugins]
    if len(names) != len(set(names)):
        raise RuntimeError("generated marketplace contains duplicate plugin names")
    write_json(
        MARKETPLACE_PATH,
        {
            "name": "jlbank-plugin-marketplace",
            "owner": {"name": "JLBank"},
            "metadata": {
                "description": "JLBank internal mirror of public Claude Code plugins and popular Agent Skills."
            },
            "plugins": plugins,
        },
    )


def build_inventory_reports(provenance: List[Dict[str, Any]]) -> None:
    mirrored = [item for item in provenance if item.get("status") == "mirrored"]
    write_json(
        CATALOG / "license-report.json",
        {
            "generated_at": now(),
            "note": "Detected files are evidence only; UNKNOWN means no root license file was detected, not that the work has no license.",
            "packages": [
                {
                    "name": item["name"],
                    "kind": item["kind"],
                    "upstream_repository": item.get("upstream_repository"),
                    "status": "FILES_DETECTED" if item.get("license_files") else "UNKNOWN",
                    "license_files": item.get("license_files", []),
                }
                for item in mirrored
            ],
        },
    )
    write_json(
        CATALOG / "trust-boundaries.json",
        {
            "generated_at": now(),
            "note": "Static path and executable-bit inventory; review content before approval or execution.",
            "packages": [
                {
                    "name": item["name"],
                    "kind": item["kind"],
                    "local_path": item["local_path"],
                    "trust_boundaries": item.get("trust_boundaries", {}),
                }
                for item in mirrored
                if item.get("trust_boundaries")
            ],
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="Synchronize every configured source.")
    parser.add_argument("--anthropic", action="store_true", help="Mirror Anthropic's official marketplace.")
    parser.add_argument("--skills-sh", action="store_true", help="Mirror the skills.sh all-time leaderboard.")
    parser.add_argument("--skills-limit", type=int, default=600)
    parser.add_argument(
        "--skills-source",
        action="append",
        default=[],
        help="Only refresh this skills.sh source; repeat for multiple sources.",
    )
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    if not (args.all or args.anthropic or args.skills_sh):
        parser.error("choose --all, --anthropic, or --skills-sh")
    CATALOG.mkdir(parents=True, exist_ok=True)
    PLUGINS.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)

    provenance_path = CATALOG / "provenance.json"
    previous_provenance: List[Dict[str, Any]] = []
    if provenance_path.is_file():
        previous_provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    replaced_kinds = set()
    if args.all or args.anthropic:
        replaced_kinds.add("anthropic-marketplace")
    if (args.all or args.skills_sh) and not args.skills_source:
        replaced_kinds.add("skills.sh")
    selected_skill_sources = set(args.skills_source)
    provenance: List[Dict[str, Any]] = [
        item for item in previous_provenance
        if item.get("kind") not in replaced_kinds
        and not (item.get("kind") == "skills.sh" and item.get("name") in selected_skill_sources)
    ]
    report_path = CATALOG / "sync-report.json"
    previous_report: Dict[str, Any] = {}
    if report_path.is_file():
        previous_report = json.loads(report_path.read_text(encoding="utf-8"))
    report: Dict[str, Any] = {
        key: value for key, value in previous_report.items()
        if key in {"anthropic", "skills_sh"} and (
            (key == "anthropic" and "anthropic-marketplace" not in replaced_kinds)
            or (key == "skills_sh" and "skills.sh" not in replaced_kinds)
        )
    }
    report.update({"started_at": now(), "failures": []})
    anthropic_catalog: Optional[Dict[str, Any]] = None
    previous_anthropic = CATALOG / "anthropic-upstream.json"
    if previous_anthropic.is_file():
        anthropic_catalog = json.loads(previous_anthropic.read_text(encoding="utf-8"))

    if args.all or args.anthropic:
        anthropic_catalog, official_commit, official_date = load_anthropic_catalog()
        owner, repo = "anthropics", "claude-plugins-official"
        archive = download_github_archive(owner, repo, official_commit)
        official_root = safe_extract(archive, WORK / "anthropic" / f"official--{official_commit}")
        report["anthropic"] = {
            "expected": len(anthropic_catalog["plugins"]),
            "source_commit": official_commit,
            "source_date": official_date,
        }
        for index, entry in enumerate(anthropic_catalog["plugins"], 1):
            try:
                record = mirror_anthropic_entry(entry, official_root, official_commit)
                provenance.append(record)
                log(f"[anthropic {index}/{len(anthropic_catalog['plugins'])}] {entry['name']}")
            except Exception as error:
                failure = {"kind": "anthropic-marketplace", "name": entry["name"], "error": str(error)}
                provenance.append({**failure, "status": "failed"})
                report["failures"].append(failure)
                log(f"FAILED {entry['name']}: {error}")

    if args.all or args.skills_sh:
        skills = load_skills_leaderboard(args.skills_limit)
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for entry in skills:
            grouped.setdefault(entry["source"], []).append(entry)
        all_grouped = grouped
        if selected_skill_sources:
            unknown = selected_skill_sources - set(grouped)
            if unknown:
                raise SystemExit(f"unknown skills.sh source(s): {sorted(unknown)}")
            grouped = {source: entries for source, entries in grouped.items() if source in selected_skill_sources}
        report["skills_sh"] = {"expected_skills": len(skills), "expected_sources": len(all_grouped)}

        def work(item: Tuple[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
            return mirror_skill_source(*item)

        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {executor.submit(work, item): item[0] for item in grouped.items()}
            for index, future in enumerate(concurrent.futures.as_completed(futures), 1):
                source = futures[future]
                try:
                    record = future.result()
                    provenance.append(record)
                    log(f"[skills.sh {index}/{len(grouped)}] {source} ({len(record['skills'])} skills)")
                except Exception as error:
                    failure = {"kind": "skills.sh", "name": source, "error": str(error)}
                    provenance.append({**failure, "status": "failed"})
                    report["failures"].append(failure)
                    log(f"FAILED {source}: {error}")

    write_json(provenance_path, sorted(provenance, key=lambda item: (item["kind"], item["name"])))
    report["finished_at"] = now()
    report["mirrored_records"] = sum(item.get("status") == "mirrored" for item in provenance)
    all_failed = [item for item in provenance if item.get("status") == "failed"]
    report["failures"] = all_failed
    report["failed_records"] = len(all_failed)
    write_json(report_path, report)
    build_marketplace(anthropic_catalog, provenance)
    build_inventory_reports(provenance)
    if report["failures"]:
        raise SystemExit(f"sync incomplete: {len(report['failures'])} source(s) failed; see catalog/sync-report.json")


if __name__ == "__main__":
    main()
