# Yamasabha 🜂  ·  यमसभा

> **The court of Yama, where threats are judged.** One platform and one dashboard over seven security engines.

[![CI](https://github.com/YAMRAJ13y/yamasabha/actions/workflows/ci.yml/badge.svg)](https://github.com/YAMRAJ13y/yamasabha/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Yamasabha unifies **seven independent open-source security tools** behind a single
FastAPI backend and a themed web dashboard — run any of them from one place, in the
browser, with one click. Each engine stays its own tested, CI-green package; Yamasabha
is the thin **integration + UI** layer that turns a toolbox into a *product*.

```bash
git clone https://github.com/YAMRAJ13y/yamasabha && cd yamasabha
pip install -e .          # pulls the 7 engines from GitHub
yamasabha                 # serve at http://127.0.0.1:8000
```

Open the URL and you get a dashboard with a card per engine — each pre-loaded with a
demo input so it runs instantly.

---

## 🜂 The seven engines

| | Engine | What it judges |
|--|--------|----------------|
| 🪤 | [EchoTrap](https://github.com/YAMRAJ13y/echotrap) | zero-click prompt injection (attack + defense) |
| 🛡️ | [SkillSentry](https://github.com/YAMRAJ13y/skillsentry) | malicious MCP servers / agent skills |
| 🛠️ | [PatchPilot](https://github.com/YAMRAJ13y/patchpilot) | CVE remediation priority (KEV + EPSS) |
| ⚒️ | [IOCForge](https://github.com/YAMRAJ13y/iocforge) | IOC enrichment & triage |
| 🛂 | [IdentityWatch](https://github.com/YAMRAJ13y/identitywatch) | identity-attack detection |
| 🥒 | [PickleGuard](https://github.com/YAMRAJ13y/pickleguard) | malicious ML-model pickles |
| 🔦 | [LeakLens](https://github.com/YAMRAJ13y/leaklens) | ransomware leak-site trends |

---

## 🏛️ Architecture

```mermaid
flowchart LR
    UI["Dashboard (one themed page,<br/>a card per engine)"] -->|"POST /api/&lt;tool&gt;"| API[FastAPI backend]
    API -->|imports & calls| E["7 engine packages<br/>(installed as deps)"]
    E -->|each tool's to_dict() JSON| API --> UI
```

- **Thin orchestration:** `tools.py` wraps each engine's public API (`scan`, `prioritize`, `lookup`, `report`, …) and returns its existing JSON. No logic is duplicated — the engines remain the source of truth.
- **No auth / no database / no billing** (by design for v1) — it's a product *demo*, not a SaaS. That keeps the focus on security, not plumbing.
- **One-click demos:** every endpoint falls back to a built-in sample input, so the dashboard is live the moment it loads.

---

## 🔌 API

| Method | Endpoint | Body | Returns |
|--------|----------|------|---------|
| GET | `/` | — | the dashboard |
| GET | `/api/health` · `/api/tools` | — | status / card metadata |
| POST | `/api/echotrap` | — | exfil-then-blocked result |
| POST | `/api/iocforge` | `{input}` (IOC) | unified verdict |
| POST | `/api/skillsentry` | `{input}` (tool/skill text) | risk report |
| POST | `/api/patchpilot` | `{input}` (inventory CSV) | prioritized CVEs |
| POST | `/api/identitywatch` | `{input}` (auth-log JSONL) | ATT&CK alerts |
| POST | `/api/pickleguard` | file upload *or* none → demo | model scan |
| POST | `/api/leaklens` | `{live}` | ransomware trends |

(Empty `{input}` uses each engine's built-in demo sample.)

---

## 🚀 Deploy (free)

**Docker:**
```bash
docker build -t yamasabha . && docker run -p 8000:8000 yamasabha
```

**Render** (one-click): connect this repo — `render.yaml` is included (free web service, `/api/health` healthcheck). Works on any host that injects `$PORT` (Railway, Fly.io, etc.).

---

## ✅ Testing & CI

```bash
pip install -e ".[dev]"
ruff check . && pytest -q   # API tests exercise every engine through the platform
```

GitHub Actions installs the 7 engines from GitHub, lints, and runs the full API test-suite on Python 3.10–3.13.

---

## 🚧 Roadmap

- [ ] Add **Yamlok** (tamper-evident decommission sign-off) as the 8th engine once it ships
- [ ] Per-run history (opt-in, local SQLite) and shareable result links
- [ ] File upload for SkillSentry/PatchPilot/IdentityWatch (not just paste)
- [ ] A hosted live demo URL + screenshot/GIF in this README
- [ ] Optional API key + rate limiting if ever exposed publicly

---

## ⚠️ Disclaimer

Yamasabha is a defensive, educational platform that orchestrates other defensive
tools. It runs the engines in their safe/offline modes by default. Don't expose it
publicly without adding auth and rate limiting.

---

## 📄 License

[MIT](LICENSE) © 2026 Yamraj ([@YAMRAJ13y](https://github.com/YAMRAJ13y)) — see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
