"""Yamasabha — a unified security platform exposing all 7 engines over one API + UI."""
from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from . import __version__, samples, tools

app = FastAPI(
    title="Yamasabha",
    version=__version__,
    description="The court of Yama — one platform, seven security engines.",
)

_INDEX = (Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")

# Drives /api/tools, the home grid, and each module's landing page.
TOOLS_META = [
    {
        "id": "echotrap", "emoji": "🪤", "name": "EchoTrap", "accent": "#ff2d6b",
        "tagline": "Zero-click prompt-injection: stolen vs blocked", "input": "run",
        "blurb": "A self-contained lab that reproduces an EchoLeak-style zero-click "
                 "prompt-injection attack against an AI assistant — then defends it. Watch a "
                 "secret get exfiltrated, then watch the defense block it.",
        "threat": "Indirect / zero-click prompt injection — OWASP LLM01 (the #1 LLM risk).",
        "features": [
            "Reproduces EchoLeak (CVE-2025-32711), the first zero-click AI exploit",
            "3-layer defense: input sanitization → output-channel filtering → egress allowlist",
            "Deterministic offline engine (no API key) + optional real-Claude backend",
            "Maps to OWASP LLM01 / LLM02 / LLM05",
        ],
    },
    {
        "id": "skillsentry", "emoji": "🛡️", "name": "SkillSentry", "accent": "#00eaff",
        "tagline": "Scan an MCP tool / agent skill for poisoning", "input": "text",
        "sample": samples.SKILLSENTRY,
        "blurb": "A semantic scanner for malicious MCP servers and agent skills — the brand-new "
                 "AI-agent supply chain. Catches what keyword scanners miss.",
        "threat": "AI-agent supply chain — Snyk's ToxicSkills found ~37% of skills are flawed.",
        "features": [
            "14 detection rules (SS001–SS014) over every model-visible field",
            "Tool-poisoning, prompt injection, rug-pulls, excessive agency",
            "Layer-0 de-obfuscation: invisible Unicode, ANSI, HTML comments, base64",
            "Findings mapped to OWASP Agentic Top 10 / MITRE ATLAS",
        ],
    },
    {
        "id": "patchpilot", "emoji": "🛠️", "name": "PatchPilot", "accent": "#ffc24b",
        "tagline": "Prioritize CVEs by real-world exploitation", "input": "text",
        "sample": samples.PATCHPILOT,
        "blurb": "Stop patching by CVSS. PatchPilot ranks your CVEs by what attackers are actually "
                 "exploiting — CISA KEV + FIRST EPSS — so you fix what matters first.",
        "threat": "Mean-time-to-exploit is collapsing — KEV-first remediation (CISA BOD 22-01).",
        "features": [
            "Transparent 0–100 score → ACT_NOW / SCHEDULE / DEFER tiers",
            "KEV + ransomware overrides; EPSS weighted above CVSS",
            "Live keyless feeds (CISA KEV + FIRST EPSS) or a bundled snapshot",
            "Shows why a CVSS 7.7 on KEV outranks a 9.8 nobody exploits",
        ],
    },
    {
        "id": "iocforge", "emoji": "⚒️", "name": "IOCForge", "accent": "#3dff9a",
        "tagline": "Enrich an IP / domain / URL / hash", "input": "ioc",
        "sample": samples.IOCFORGE,
        "blurb": "Paste one indicator, get one verdict. IOCForge fans an IOC out to many free "
                 "threat-intel feeds in parallel and returns a single, analyst-ready answer.",
        "threat": "SOC alert-enrichment overload — the daily triage grind.",
        "features": [
            "GreyNoise, AbuseIPDB, VirusTotal, abuse.ch, AlienVault OTX",
            "Unified weighted verdict + GreyNoise scanner-noise suppression",
            "De-fangs input (hxxp://evil[.]com) and auto-detects IOC type",
            "STIX typing + inferred MITRE ATT&CK techniques",
        ],
    },
    {
        "id": "identitywatch", "emoji": "🛂", "name": "IdentityWatch", "accent": "#9b6bff",
        "tagline": "Detect identity attacks in an auth log", "input": "text",
        "sample": samples.IDENTITYWATCH,
        "blurb": "Detection-as-code for the way attackers actually break in now: they log in. "
                 "Scans auth logs for identity-first attacks, mapped to MITRE ATT&CK.",
        "threat": "Identity-first intrusion — 'attackers log in, they don't break in.'",
        "features": [
            "6 rules: impossible travel, MFA fatigue, spraying, brute force, new-country, session theft",
            "Mapped to MITRE ATT&CK (T1078 / T1110 / T1621 / T1539)",
            "Reads JSONL / JSON / CSV sign-in logs",
            "Detection-as-code: every rule has positive + no-false-positive tests",
        ],
    },
    {
        "id": "pickleguard", "emoji": "🥒", "name": "PickleGuard", "accent": "#00eaff",
        "tagline": "Scan an ML model for malicious pickle opcodes", "input": "file",
        "blurb": "ML models can run code the instant you load them. PickleGuard statically "
                 "inspects pickle opcodes to flag malicious models — without ever unpickling them.",
        "threat": "Weaponized models on public hubs — pickle is RCE-on-load.",
        "features": [
            "Static opcode scan (pickletools) — never executes the file",
            "Flags dangerous GLOBAL/REDUCE imports (os / subprocess / eval / getattr)",
            "Handles raw pickle and torch .pt/.pth; safetensors = safe by design",
            "Catches denylist-bypass tricks (e.g. posix.system); emits a model SBOM",
        ],
    },
    {
        "id": "leaklens", "emoji": "🔦", "name": "LeakLens", "accent": "#ff2d6b",
        "tagline": "Ransomware leak-site trend dashboard", "input": "toggle",
        "blurb": "Turn ransomware leak-site noise into intelligence — who's most active, which "
                 "sectors and countries are hit, and when a crew surges.",
        "threat": "Ransomware's elevated 'new normal' and leak-site consolidation.",
        "features": [
            "Group / sector / country trend dashboards + a monthly timeline",
            "Live ransomware.live feed (keyless) or a bundled snapshot",
            "Optional Claude-written weekly intel brief",
            "Surfaces surges and the leading crews at a glance",
        ],
    },
]


class RunInput(BaseModel):
    input: str = ""
    live: bool = False


def _safe(fn, *args, **kwargs) -> dict:
    try:
        return fn(*args, **kwargs)
    except Exception as exc:  # surface engine errors as data, never 500 the page
        return {"error": f"{type(exc).__name__}: {exc}"}


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return _INDEX


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "version": __version__, "tools": [t["id"] for t in TOOLS_META]}


@app.get("/api/tools")
def list_tools() -> dict:
    return {"tools": TOOLS_META}


@app.post("/api/echotrap")
def echotrap() -> dict:
    return _safe(tools.run_echotrap)


@app.post("/api/iocforge")
def iocforge(body: RunInput) -> dict:
    return _safe(tools.run_iocforge, body.input)


@app.post("/api/skillsentry")
def skillsentry(body: RunInput) -> dict:
    return _safe(tools.run_skillsentry, body.input)


@app.post("/api/patchpilot")
def patchpilot(body: RunInput) -> dict:
    return _safe(tools.run_patchpilot, body.input)


@app.post("/api/identitywatch")
def identitywatch(body: RunInput) -> dict:
    return _safe(tools.run_identitywatch, body.input)


@app.post("/api/pickleguard")
async def pickleguard(file: Annotated[UploadFile | None, File()] = None) -> dict:
    if file is None:
        return _safe(tools.run_pickleguard_demo)
    data = await file.read()
    return _safe(tools.run_pickleguard_bytes, data, file.filename or "uploaded.pkl")


@app.post("/api/leaklens")
def leaklens(body: RunInput) -> dict:
    return _safe(tools.run_leaklens, body.live)
