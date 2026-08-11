"""Tests for scripts/bootstrap.py."""

from __future__ import annotations

import scripts.bootstrap as bootstrap


def test_init_script_returns_root_and_is_idempotent(monkeypatch):
    calls = {"overlay": 0, "env": 0}

    def fake_overlay():
        calls["overlay"] += 1
        return True

    def fake_load_env():
        calls["env"] += 1

    monkeypatch.setattr(bootstrap, "_bootstrapped", False)
    monkeypatch.setattr(
        "scripts.data_paths.apply_private_overlay",
        fake_overlay,
    )
    monkeypatch.setattr(
        "scripts.llm_provider.load_env",
        fake_load_env,
    )

    root1 = bootstrap.init_script()
    root2 = bootstrap.init_script()

    assert root1 == bootstrap.ROOT
    assert root2 == bootstrap.ROOT
    assert str(bootstrap.ROOT) in __import__("sys").path
    assert calls["overlay"] == 1
    assert calls["env"] == 1
