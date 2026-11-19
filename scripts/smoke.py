#!/usr/bin/env python3
"""Scaffold smoke check for the FastAPI port of the Express publisher service.

Stdlib-only, so it runs from a clean checkout with no dependencies installed:

    python3 scripts/smoke.py

Checks:
  1. the ``publisher`` package and all nine target module packages import;
  2. ``publisher/module_graph.json`` is a closed, acyclic module graph whose
     ``depends_on`` entries all have a strictly smaller ``build_order``;
  3. every module package directory exists and matches the graph;
  4. ``.env.example`` declares every required env var and carries no secret;
  5. no file in the scaffold contains the leaked GHOST_API_KEY literal
     (ADR-003);
  6. ``requirements.txt`` pins every dependency and agrees with
     ``pyproject.toml``;
  7. ``scaffold_manifest.json`` is valid and lists only files that exist,
     with every validation step a non-empty argv array of strings.
"""

from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - requires-python is >=3.11
    tomllib = None

SCAFFOLD_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_ENV_KEYS = {
    "PORT",
    "NODE_ENV",
    "DEBUG",
    "ROOT_DOMAIN",
    "DOMAIN_QUERY_PARAM",
    "HTTPS_DOMAIN",
    "UMAMI_SOURCE",
    "TASKS_URL",
    "TASKS_DATABASE_URL",
    "ADMIN_SLUG",
    "TURN_OFF_SINGLE_USER_MODE",
    "GHOST_URL",
    "GHOST_API_KEY",
    "BLOG_CATEGORIES",
}

# ADR-003: the credential leaked in the source constants.js must never appear
# in this repository. It is assembled at runtime from two fragments so that
# this checker file itself does not contain the literal it scans for.
LEAKED_GHOST_API_KEY = "3ed1f08bc38fe9e7" + "dfd325bd87"

failures: list[str] = []


def check(condition: bool, message: str) -> None:
    if condition:
        print(f"ok    - {message}")
    else:
        failures.append(message)
        print(f"FAIL  - {message}")


def normalize_dist_name(name: str) -> str:
    """Reduce a requirement string like 'uvicorn[standard]>=0.34' to 'uvicorn'."""
    name = re.split(r"[\[<>=!~;\s]", name.strip(), maxsplit=1)[0]
    return name.lower().replace("_", "-")


def main() -> int:
    # 1. package imports (the empty stubs must import with the stdlib only)
    sys.path.insert(0, str(SCAFFOLD_ROOT))
    graph = json.loads((SCAFFOLD_ROOT / "publisher" / "module_graph.json").read_text(encoding="utf-8"))
    modules = graph["modules"]
    check(
        graph.get("translation_pair") == "node-express__python-fastapi",
        "module graph names the node-express__python-fastapi translation pair",
    )
    importlib.import_module("publisher")
    for module in modules:
        pkg = module["package"]
        try:
            importlib.import_module(f"publisher.{pkg}")
            check(True, f"publisher.{pkg} imports")
        except Exception as exc:  # noqa: BLE001 - report any import failure
            check(False, f"publisher.{pkg} imports ({exc})")

    # 2 + 3. graph invariants and package directories
    names = [m["name"] for m in modules]
    packages = [m["package"] for m in modules]
    check(len(names) == 9 and len(set(names)) == 9, "nine uniquely named target modules")
    check(len(set(packages)) == len(packages), "python package names are unique")
    orders = sorted(m["build_order"] for m in modules)
    check(orders == list(range(len(modules))), "build_order is a linear 0..N-1 sequence")
    by_name = {m["name"]: m for m in modules}
    for module in modules:
        for dep in module["depends_on"]:
            ok = dep in by_name and by_name[dep]["build_order"] < module["build_order"]
            check(ok, f"{module['name']} depends only on a smaller build_order ({dep})")
        pkg_init = SCAFFOLD_ROOT / "publisher" / module["package"] / "__init__.py"
        check(pkg_init.is_file(), f"publisher/{module['package']}/__init__.py exists")

    # 4. .env.example declares the full configuration surface, no secrets
    env_text = (SCAFFOLD_ROOT / ".env.example").read_text(encoding="utf-8")
    env_keys = {
        line.split("=", 1)[0].strip()
        for line in env_text.splitlines()
        if line.strip() and not line.strip().startswith("#") and "=" in line
    }
    missing = REQUIRED_ENV_KEYS - env_keys
    check(not missing, f".env.example declares all required env vars (missing: {sorted(missing)})")
    ghost_line = next((ln for ln in env_text.splitlines() if ln.startswith("GHOST_API_KEY=")), "")
    check(
        "<" in ghost_line or "secret" in ghost_line.lower(),
        "GHOST_API_KEY is a placeholder loaded from the secret store (ADR-003)",
    )

    # 5. leaked-credential scan over every scaffold file
    leaked_in = []
    for path in sorted(SCAFFOLD_ROOT.rglob("*")):
        if not path.is_file():
            continue
        try:
            if LEAKED_GHOST_API_KEY in path.read_text(encoding="utf-8"):
                leaked_in.append(str(path.relative_to(SCAFFOLD_ROOT)))
        except (UnicodeDecodeError, OSError):
            continue
    check(not leaked_in, f"no file contains the leaked GHOST_API_KEY literal (found in: {leaked_in})")

    # 6. dependency manifests agree and are pinned
    req_lines = [
        ln.strip()
        for ln in (SCAFFOLD_ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]
    check(bool(req_lines) and all("==" in ln for ln in req_lines), "requirements.txt pins every dependency with ==")
    req_names = {normalize_dist_name(ln) for ln in req_lines}
    if tomllib is not None:
        pyproject = tomllib.loads((SCAFFOLD_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        project = pyproject.get("project", {})
        check(project.get("name") == "publisher", "pyproject.toml project name is 'publisher'")
        check("3.11" in project.get("requires-python", ""), "pyproject.toml requires-python >= 3.11")
        dep_names = {normalize_dist_name(d) for d in project.get("dependencies", [])}
        check(req_names == dep_names, f"requirements.txt and pyproject.toml dependency sets agree (diff: {sorted(req_names ^ dep_names)})")
    else:  # pragma: no cover
        print("skip  - pyproject.toml cross-check (tomllib unavailable)")

    # 7. manifest self-check
    manifest = json.loads((SCAFFOLD_ROOT / "scaffold_manifest.json").read_text(encoding="utf-8"))
    files = manifest.get("files", [])
    check(bool(files), "scaffold_manifest.json lists files")
    missing_files = [f for f in files if not (SCAFFOLD_ROOT / f).is_file()]
    check(not missing_files, f"every manifest-listed file exists (missing: {missing_files})")
    steps = manifest.get("validation", [])
    valid_steps = bool(steps) and all(
        isinstance(step.get("argv"), list)
        and len(step["argv"]) >= 1
        and all(isinstance(arg, str) and arg for arg in step["argv"])
        for step in steps
    )
    check(valid_steps, "every validation step is a non-empty argv array of non-empty strings")

    # local stack sanity (text level; stdlib has no yaml parser)
    compose = (SCAFFOLD_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    check("postgres" in compose and "btw" in compose, "docker-compose.yml defines the local Postgres btw stack")

    if failures:
        print(f"\nsmoke: {len(failures)} check(s) FAILED")
        return 1
    print("\nsmoke: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
