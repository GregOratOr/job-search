"""Tests for scripts/find_contacts.py (merge-by-email Contacts section)."""

from __future__ import annotations

from scripts.find_contacts import (
    build_queries,
    gather_public_contacts,
    render_markdown,
    write_contacts_to_networking,
)


def test_build_queries_includes_role_and_alumni():
    q = build_queries("Acme", "ML Engineer", ["Example University"])
    linkedin = q["LinkedIn (paste into LinkedIn search)"]
    assert any("ML Engineer" in s for s in linkedin)
    assert any("Example University" in s for s in linkedin)


def test_gather_requires_use_project_web():
    import pytest

    with pytest.raises(RuntimeError, match="use_project_web"):
        gather_public_contacts("Acme", use_project_web=False)


def test_write_contacts_first_run(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "scripts.find_contacts.data_path",
        lambda *parts: tmp_path.joinpath(*parts),
    )
    queries = build_queries("Acme", "SWE", None)
    public = [
        {"email": "a@acme.com", "source": "https://acme.com/team", "title": "Team"},
    ]
    path = write_contacts_to_networking(
        "acme_swe_2026", "Acme", "SWE", queries, public, [],
    )
    text = path.read_text(encoding="utf-8")
    assert "## Contacts — Acme" in text
    assert "a@acme.com" in text
    assert "①" not in text  # outreach content untouched (none yet)


def test_write_contacts_same_emails_replaces(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "scripts.find_contacts.data_path",
        lambda *parts: tmp_path.joinpath(*parts),
    )
    job_id = "acme_swe_2026"
    queries = build_queries("Acme", "SWE", None)
    public = [
        {"email": "a@acme.com", "source": "https://acme.com/team", "title": "Team"},
    ]
    write_contacts_to_networking(job_id, "Acme", "SWE", queries, public, [])

    # Same email, different source title → full replace
    public2 = [
        {"email": "a@acme.com", "source": "https://acme.com/about", "title": "About"},
    ]
    path = write_contacts_to_networking(
        job_id, "Acme", "SWE", queries, public2, [],
    )
    text = path.read_text(encoding="utf-8")
    assert text.count("a@acme.com") == 1
    assert "About" in text
    assert "Team" not in text


def test_write_contacts_new_email_merges(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "scripts.find_contacts.data_path",
        lambda *parts: tmp_path.joinpath(*parts),
    )
    job_id = "acme_swe_2026"
    queries = build_queries("Acme", "SWE", None)
    # Seed outreach above Contacts so we verify it survives
    net = tmp_path / "applications" / "jobs" / job_id / "networking.md"
    net.parent.mkdir(parents=True)
    net.write_text("# Outreach\n\nhello draft\n", encoding="utf-8")

    write_contacts_to_networking(
        job_id,
        "Acme",
        "SWE",
        queries,
        [{"email": "a@acme.com", "source": "https://a", "title": "A"}],
        [],
    )
    write_contacts_to_networking(
        job_id,
        "Acme",
        "SWE",
        queries,
        [
            {"email": "a@acme.com", "source": "https://a", "title": "A"},
            {"email": "b@acme.com", "source": "https://b", "title": "B"},
        ],
        [],
    )
    text = net.read_text(encoding="utf-8")
    assert "hello draft" in text
    assert "a@acme.com" in text
    assert "b@acme.com" in text
    assert text.count("## Contacts") == 1


def test_gather_records_fetch_failures(monkeypatch):
    monkeypatch.setattr(
        "scripts.find_contacts.web.search",
        lambda q, max_results=5, **kwargs: [
            {"title": "Bad", "url": "https://bad.example", "snippet": ""},
            {"title": "Good", "url": "https://good.example", "snippet": ""},
        ],
    )

    def fake_fetch(url, max_chars=6000, **kwargs):
        if "bad" in url:
            raise ConnectionError("timeout")
        return "reach us at hire@good.example for jobs"

    monkeypatch.setattr("scripts.find_contacts.web.fetch", fake_fetch)
    contacts, failures = gather_public_contacts("Acme", max_pages=2, use_project_web=True)
    assert any(c["email"] == "hire@good.example" for c in contacts)
    assert failures == [
        {"title": "Bad", "url": "https://bad.example", "error": "timeout"}
    ]


def test_append_without_web_writes_queries_only(tmp_path, monkeypatch):
    from scripts.find_contacts import append_contacts_for_job

    monkeypatch.setattr(
        "scripts.find_contacts.data_path",
        lambda *parts: tmp_path.joinpath(*parts),
    )
    called = {"gather": 0}

    def boom(*a, **k):
        called["gather"] += 1
        raise AssertionError("gather should not run without use_project_web")

    monkeypatch.setattr("scripts.find_contacts.gather_public_contacts", boom)
    path = append_contacts_for_job(
        "acme_swe_2026", "Acme", "SWE", use_project_web=False,
    )
    text = path.read_text(encoding="utf-8")
    assert called["gather"] == 0
    assert "### Search queries" in text
    assert "None extracted" in text


def test_render_includes_failed_fetches():
    md = render_markdown(
        "Acme",
        None,
        build_queries("Acme", None, None),
        [],
        [],
        [{"title": "X", "url": "https://x.example", "error": "404"}],
    )
    assert "### Failed fetches" in md
    assert "https://x.example" in md
    assert "404" in md
