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

# Drives both /api/tools and the dashboard cards.
TOOLS_META = [
    {"id": "echotrap", "emoji": "🪤", "name": "EchoTrap",
     "tagline": "Zero-click prompt-injection: stolen vs blocked", "input": "run"},
    {"id": "skillsentry", "emoji": "🛡️", "name": "SkillSentry",
     "tagline": "Scan an MCP tool / agent skill for poisoning", "input": "text",
     "sample": samples.SKILLSENTRY},
    {"id": "patchpilot", "emoji": "🛠️", "name": "PatchPilot",
     "tagline": "Prioritize CVEs by real-world exploitation", "input": "text",
     "sample": samples.PATCHPILOT},
    {"id": "iocforge", "emoji": "⚒️", "name": "IOCForge",
     "tagline": "Enrich an IP / domain / URL / hash", "input": "ioc",
     "sample": samples.IOCFORGE},
    {"id": "identitywatch", "emoji": "🛂", "name": "IdentityWatch",
     "tagline": "Detect identity attacks in an auth log", "input": "text",
     "sample": samples.IDENTITYWATCH},
    {"id": "pickleguard", "emoji": "🥒", "name": "PickleGuard",
     "tagline": "Scan an ML model for malicious pickle opcodes", "input": "file"},
    {"id": "leaklens", "emoji": "🔦", "name": "LeakLens",
     "tagline": "Ransomware leak-site trend dashboard", "input": "toggle"},
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
