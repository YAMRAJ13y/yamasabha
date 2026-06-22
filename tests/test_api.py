"""API tests via FastAPI TestClient — exercises every engine through the platform."""
from __future__ import annotations

from fastapi.testclient import TestClient

from yamasabha.app import app

client = TestClient(app)


def test_health_lists_seven_tools():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert len(r.json()["tools"]) == 7


def test_tools_metadata():
    tools = client.get("/api/tools").json()["tools"]
    assert {t["id"] for t in tools} >= {"echotrap", "iocforge", "pickleguard", "leaklens"}


def test_dashboard_served():
    r = client.get("/")
    assert r.status_code == 200
    assert "YAMASABHA" in r.text


def test_echotrap_demo():
    d = client.post("/api/echotrap").json()
    assert d["without_defense"]["leaked"] is True
    assert d["with_defense"]["leaked"] is False


def test_iocforge_malicious():
    d = client.post("/api/iocforge", json={"input": "185.220.101.47"}).json()
    assert d["unified"]["verdict"] == "malicious"


def test_skillsentry_sample_blocks():
    d = client.post("/api/skillsentry", json={"input": ""}).json()
    assert d["summary"]["verdict"] == "block"


def test_patchpilot_sample_has_actnow():
    d = client.post("/api/patchpilot", json={"input": ""}).json()
    assert d["tierSummary"]["ACT_NOW"] >= 1


def test_identitywatch_sample_alerts():
    d = client.post("/api/identitywatch", json={"input": ""}).json()
    assert d["alerts_count"] >= 1


def test_pickleguard_demo_flags_malicious():
    d = client.post("/api/pickleguard").json()
    assert d["summary"]["malicious"] >= 1


def test_leaklens_dashboard():
    d = client.post("/api/leaklens", json={"live": False}).json()
    assert d["total_victims"] == 70
