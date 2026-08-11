"""Orchestrator CLI flag smoke tests (pipeline)."""

from __future__ import annotations

import sys
from unittest.mock import patch

import pytest


def test_pipeline_help_lists_provider_and_use_agent(capsys):
    from scripts import pipeline

    with patch.object(sys, "argv", ["pipeline", "--help"]):
        with pytest.raises(SystemExit) as exc:
            pipeline.main()
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "--provider" in out
    assert "--use-agent" in out
    assert "--use-project-web" in out
