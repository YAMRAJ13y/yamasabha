"""Thin wrappers that call each of the 7 security engines and return plain dicts.

Each engine stays an independent package (installed as a dependency); Yamasabha
only orchestrates. Text inputs an engine expects as a file are written to a temp
file and cleaned up.
"""
from __future__ import annotations

import os
import pickle
import tempfile

from . import samples


def _tmp(text: str, suffix: str) -> str:
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def run_echotrap() -> dict:
    from echotrap import Assistant, Defense

    assistant = Assistant()
    query = "Summarize my latest emails."
    exposed = assistant.answer(query, defense=None)
    defended = assistant.answer(query, defense=Defense())
    return {
        "query": query,
        "without_defense": {
            "leaked": exposed.leaked,
            "exfiltrated": exposed.sink.captured_values(),
            "answer": exposed.answer,
        },
        "with_defense": {
            "leaked": defended.leaked,
            "input_findings": [f.reason for f in defended.input_findings],
            "blocked": [b.reason for b in defended.blocked],
            "answer": defended.answer,
        },
    }


def run_iocforge(ioc: str) -> dict:
    from iocforge import scan, to_dict

    return to_dict(scan(ioc.strip() or samples.IOCFORGE, use_llm=False))


def run_skillsentry(text: str) -> dict:
    from skillsentry import scan, to_dict

    text = text.strip() or samples.SKILLSENTRY
    suffix = ".md" if text.lstrip().startswith("---") else ".json"
    path = _tmp(text, suffix)
    try:
        return to_dict(scan(path))
    finally:
        os.unlink(path)


def run_patchpilot(csv_text: str) -> dict:
    from patchpilot import prioritize, to_dict

    path = _tmp(csv_text.strip() or samples.PATCHPILOT, ".csv")
    try:
        return to_dict(prioritize(path))
    finally:
        os.unlink(path)


def run_identitywatch(jsonl_text: str) -> dict:
    from identitywatch import scan, to_dict

    path = _tmp(jsonl_text.strip() or samples.IDENTITYWATCH, ".jsonl")
    try:
        return to_dict(scan(path))
    finally:
        os.unlink(path)


def run_pickleguard_bytes(data: bytes, filename: str = "uploaded.pkl") -> dict:
    from pickleguard import scan_file, to_dict

    suffix = os.path.splitext(filename)[1] or ".pkl"
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "wb") as fh:
        fh.write(data)
    try:
        return to_dict([scan_file(path)])
    finally:
        os.unlink(path)


def run_pickleguard_demo() -> dict:
    from pickleguard import scan_file, to_dict

    class _Evil:
        def __reduce__(self):
            import os as _os

            return (_os.system, ("echo demo",))

    blobs = {
        "malicious_demo.pkl": pickle.dumps(_Evil(), protocol=4),
        "benign_demo.pkl": pickle.dumps({"weights": [0.1, 0.2, 0.3]}, protocol=4),
    }
    reports = []
    for name, data in blobs.items():
        fd, path = tempfile.mkstemp(suffix=".pkl")
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        try:
            rep = scan_file(path)
            rep.path = name
            reports.append(rep)
        finally:
            os.unlink(path)
    return to_dict(reports)


def run_leaklens(live: bool = False) -> dict:
    from leaklens import analyze, fetch_live, load_offline, to_dict

    if live:
        try:
            return to_dict(analyze(fetch_live(), source="live: ransomware.live"))
        except Exception:
            pass
    victims, snap = load_offline()
    return to_dict(analyze(victims, source=f"offline sample {snap}"))
