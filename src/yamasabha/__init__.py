"""Yamasabha - the court of Yama: one platform over seven security engines.

Yamasabha orchestrates seven independent security tools (EchoTrap, SkillSentry,
PatchPilot, IOCForge, IdentityWatch, PickleGuard, LeakLens) behind a single
FastAPI backend and a themed web dashboard. Each engine stays its own package;
Yamasabha is the thin integration + UI layer where threats are judged.
"""
from __future__ import annotations

__version__ = "0.1.0"
