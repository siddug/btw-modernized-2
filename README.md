# publisher — FastAPI port scaffold (node-express__python-fastapi)

Empty target skeleton for the behaviour-preserving modernisation of the
Express 4 `publisher` service into Python FastAPI, generated from the approved
design (`system_design.json`), mapping plan, feature queue and risk
assessment. It contains **no migrated business behaviour**: every module
package is a documentation-only stub that grows in the design's linear build
order.

## Layout

| Path | Purpose |
| --- | --- |
| `publisher/` | Python package with the nine target module packages |
| `publisher/module_graph.json` | Machine-readable module graph: build order 0-8, `depends_on`, source modules, hyphen-to-underscore package mapping |
| `publisher/config/` … `publisher/server/` | The nine target modules (build order 0-8): `config`, `db`, `notes_cache`, `memories`, `templates`, `tenancy`, `public_routes`, `internal_routes`, `server` |
| `pyproject.toml` / `requirements.txt` | Dependency manifests (kept in sync; asserted by the smoke check) |
| `.env.example` | Configuration surface: every env var with the source defaults; `GHOST_API_KEY` is a secret-store placeholder only (ADR-003) |
| `docker-compose.yml` + `db/init/01-btw-schema.sql` | Local stack: Postgres with the read-only `btw` schema the service reads |
| `.github/workflows/ci.yml` | CI: install deps, syntax check, JSON validation, smoke check |
| `scripts/smoke.py` | The one smoke check (stdlib-only, runs on a clean checkout) |
| `scaffold_manifest.json` | Intentional file list + argv-form validation commands |

Hyphenated design module names map to Python packages with underscores:
`notes-cache` -> `notes_cache`, `public-routes` -> `public_routes`,
`internal-routes` -> `internal_routes`.

## Validate (from this directory, no dependencies or network needed)

```sh
python3 -B -c "import ast, pathlib
files = sorted(pathlib.Path('publisher').rglob('*.py')) + sorted(pathlib.Path('scripts').rglob('*.py'))
for p in files:
    ast.parse(p.read_text(encoding='utf-8'), filename=str(p))
print('syntax OK:', len(files), 'python files')"   # syntax check, writes no bytecode
python3 -m json.tool scaffold_manifest.json     # manifest is valid JSON
python3 -m json.tool publisher/module_graph.json
python3 -B scripts/smoke.py                     # smoke check
```

The same commands are listed as argv arrays in `scaffold_manifest.json`.

## Local stack

```sh
docker compose up -d db   # Postgres on localhost:55432, db `btw`
# TASKS_DATABASE_URL=postgres://postgres:postgres@localhost:55432/btw
```

## Rules for growing this scaffold

* Implement modules in build order 0-8; a module may only import modules
  with a strictly smaller `build_order` (enforced by `scripts/smoke.py`).
* Behaviour preservation first: the observable contract is the 7 HTTP
  operations in the recorded api contract; all six recorded scenarios stay
  behavioural oracles (ADR-004).
* Dead code stays dead: `routes/sitemap.js` `genSitemap()` and
  `utils/utils.js` are dropped, recorded in the module docstrings (ADR-010).
* Never write the leaked `GHOST_API_KEY` literal into this repository
  (ADR-003); the smoke check scans every file for it.
