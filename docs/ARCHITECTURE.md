# Yamasabha architecture

Yamasabha is deliberately a **thin layer**. All security logic lives in the seven
engine packages; Yamasabha only routes requests to them and renders results.

## Layers

```
┌──────────────────────────────────────────────────────────┐
│  static/index.html  — one themed page, a card per engine  │  (vanilla JS, no build)
└───────────────┬──────────────────────────────────────────┘
                │  fetch POST /api/<tool>
┌───────────────▼──────────────────────────────────────────┐
│  app.py        — FastAPI: 1 route per engine + /api/tools │
│  _safe()       — engine errors become {"error": ...} data │
└───────────────┬──────────────────────────────────────────┘
                │  function call
┌───────────────▼──────────────────────────────────────────┐
│  tools.py      — wraps each engine's public API, returns  │
│                  its existing to_dict() JSON              │
│  samples.py    — built-in demo input per engine           │
└───────────────┬──────────────────────────────────────────┘
                │  import
┌───────────────▼──────────────────────────────────────────┐
│  7 engine packages (deps): echotrap, skillsentry,         │
│  patchpilot, iocforge, identitywatch, pickleguard,        │
│  leaklens — each its own repo, tests, and CI              │
└──────────────────────────────────────────────────────────┘
```

## Why engines stay separate packages

- **Single source of truth:** no logic is copied into the platform; an engine fix
  flows in via a dependency bump.
- **Independent value:** each tool still works standalone (CLI + library) and has
  its own README, tests, and CI badge.
- **Clean blast radius:** the platform can't subtly break an engine's behaviour —
  it only calls public APIs (`scan`, `prioritize`, `lookup`, `report`, …).

Engines are declared as `git+https` dependencies in `pyproject.toml`, so
`pip install .` (or the Docker/Render build) pulls them straight from GitHub.

## Request flow (example: IOCForge)

1. Browser `POST /api/iocforge {"input": "185.220.101.47"}`.
2. `app.iocforge()` → `tools.run_iocforge()` → `iocforge.scan(ioc)` → `iocforge.to_dict(report)`.
3. JSON returns to the card; the UI derives a colored headline (verdict/score) and
   shows the raw JSON on demand.

## Adding an 8th engine

1. `pip`-installable package exposing a `scan`/`report`-style function + `to_dict`.
2. Add a `run_<engine>()` wrapper in `tools.py` and a sample in `samples.py`.
3. Add a route in `app.py` and an entry in `TOOLS_META`.
4. The dashboard renders the new card automatically from `/api/tools`.
