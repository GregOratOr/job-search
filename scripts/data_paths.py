"""
scripts/data_paths.py
---------------------
Resolve paths for user-specific data.

Layout
------
The repo ships with public template directories (resume/, coverletter/,
applications/, config/, networking/, profile/) that demonstrate the structure
but contain no personal information.

When a ``private/`` git submodule is checked out it mirrors that same
structure with the real data:

    private/
      profile/          ← Python package; imported as ``profile``
      resume/           ← templates in tailoring/; per-job .py/.tex/.pdf in outputs/
      coverletter/      ← templates in tailoring/; per-job .py/.tex/.pdf in outputs/
      applications/     ← per-job bundles, tracker.csv
      config/           ← job_search_config.yaml, etc.
      networking/       ← global networking notes
      .env              ← secrets (API keys, etc.)

Detection / override
--------------------
``uses_private_data()`` returns True when ``private/profile/`` is a directory,
unless CLI/code has forced a mode via ``configure_overlay(private=…)`` or the
shared ``--private`` / ``--public`` flags (see ``add_overlay_cli_flags``).

Routing
-------
``data_path(*parts)``   — read **and write** path; always in ``private/``
                          when the overlay is active.
``resolve_path(*parts)``— read-only; prefers ``private/`` when the file
                          exists there, otherwise falls back to the public
                          template in the repo root.  Useful for template
                          files (e.g. ``{resume,coverletter}/tailoring/_template.py``)
                          that may live only in the public tree.

Private directories covered
---------------------------
    profile/, resume/, coverletter/, applications/, config/, networking/
    .env
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT    = Path(__file__).resolve().parent.parent
PRIVATE = ROOT / "private"

_overlay_applied = False
# None = auto-detect; True/False = forced by configure_overlay / CLI.
_force_private: bool | None = None


def uses_private_data() -> bool:
    """Return True when path writes should go under ``private/``."""
    if _force_private is not None:
        return _force_private
    return (PRIVATE / "profile").is_dir()


def configure_overlay(*, private: bool | None = None) -> bool:
    """Set overlay mode and (re)apply ``sys.path`` routing.

    Parameters
    ----------
    private:
        ``True``  — force ``private/`` paths (error if submodule missing)
        ``False`` — force public repo-root paths (ignore ``private/``)
        ``None``  — auto-detect from ``private/profile/``

    Returns
    -------
    bool
        Whether the private overlay is active after configuration.
    """
    global _force_private, _overlay_applied

    if private is True and not (PRIVATE / "profile").is_dir():
        print("[x] --private / configure_overlay(private=True) requires private/profile/")
        sys.exit(1)

    _force_private = private

    # Allow re-configuration when CLI forces a different mode mid-process.
    private_str = str(PRIVATE)
    while private_str in sys.path:
        sys.path.remove(private_str)
    _overlay_applied = False
    return apply_private_overlay()


def apply_private_overlay() -> bool:
    """Insert ``private/`` at the front of sys.path so ``import profile`` (and
    any other package that lives only in the private submodule) resolves there.

    Safe to call multiple times — the insertion happens only once per process
    unless ``configure_overlay`` resets the state. Returns True when the
    overlay is active.
    """
    global _overlay_applied
    if _overlay_applied:
        return uses_private_data()
    _overlay_applied = True
    if uses_private_data():
        private_str = str(PRIVATE)
        if private_str not in sys.path:
            sys.path.insert(0, private_str)
        return True
    return False


def add_overlay_cli_flags(parser: argparse.ArgumentParser) -> None:
    """Attach mutually exclusive ``--private`` / ``--public`` path-mode flags.

    After parse, call ``configure_overlay(private=args.overlay)`` (or
    ``bootstrap_paths(args)``).
    """
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--private",
        dest="overlay",
        action="store_const",
        const=True,
        help="Force paths under private/ (requires private/profile/)",
    )
    group.add_argument(
        "--public",
        dest="overlay",
        action="store_const",
        const=False,
        help="Force paths under the public repo root (ignore private/)",
    )
    parser.set_defaults(overlay=None)


def bootstrap_paths(args: argparse.Namespace | None = None) -> bool:
    """Apply overlay from parsed CLI args (or auto-detect when *args* is None)."""
    private = None if args is None else getattr(args, "overlay", None)
    return configure_overlay(private=private)


def data_path(*parts: str) -> Path:
    """Return the canonical read/write path for user data.

    When the private overlay is active this is always under ``private/``.
    Otherwise it falls back to the repo root (useful during development with
    the public template layout).

    Examples
    --------
    >>> data_path("applications", "tracker.csv")
    PosixPath('/repo/private/applications/tracker.csv')  # with submodule
    PosixPath('/repo/applications/tracker.csv')          # without submodule
    """
    if uses_private_data():
        return PRIVATE.joinpath(*parts)
    return ROOT.joinpath(*parts)


def resolve_path(*parts: str) -> Path:
    """Return the best available path for a read-only lookup.

    Preference order:
      1. ``private/<parts>``  — exists in the private submodule
      2. ``<root>/<parts>``   — falls back to the public template

    When ``--public`` is forced, only the root candidate is considered.
    When ``--private`` is forced, only the private candidate is considered
    (returned even if missing, so callers get a clear FileNotFoundError).
    """
    private_candidate = PRIVATE.joinpath(*parts)
    root_candidate = ROOT.joinpath(*parts)
    if _force_private is True:
        return private_candidate
    if _force_private is False:
        return root_candidate
    if private_candidate.exists():
        return private_candidate
    return root_candidate


def resolve_env_file() -> Path | None:
    """Return the first .env file found, preferring private/ over root."""
    if _force_private is False:
        candidate = ROOT / ".env"
        return candidate if candidate.is_file() else None
    if _force_private is True:
        candidate = PRIVATE / ".env"
        return candidate if candidate.is_file() else None
    for candidate in (PRIVATE / ".env", ROOT / ".env"):
        if candidate.is_file():
            return candidate
    return None


def rel_to_root(path: Path) -> str:
    """Return *path* relative to ROOT (forward slashes), or absolute if outside ROOT.

    Used when embedding filesystem paths into generated .py files so they respect
    the private overlay (e.g. ``private/resume/outputs/id.tex`` vs ``resume/outputs/id.tex``).
    """
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def document_stem(kind: str, job_id: str) -> str:
    """Basename stem for a per-job document under ``{kind}/outputs/``.

    Resume: ``{id}``. Cover letter: ``{id}_cl`` so the two kinds stay distinct
    when both live under similarly named output trees.
    """
    if kind == "coverletter":
        return f"{job_id}_cl"
    if kind == "resume":
        return job_id
    raise ValueError(f"Unknown document kind: {kind!r} (expected 'resume' or 'coverletter')")


def job_id_from_document_stem(kind: str, stem: str) -> str:
    """Inverse of ``document_stem`` — strip the ``_cl`` suffix for cover letters."""
    if kind == "coverletter" and stem.endswith("_cl"):
        return stem[:-3]
    return stem


def document_py(kind: str, job_id: str) -> Path:
    """Per-job resume/cover-letter source ``.py`` (lives under ``outputs/``).

    *kind* is ``"resume"`` or ``"coverletter"``. Templates remain in
    ``{kind}/tailoring/_template.py``; generated application files go next to
    their ``.tex`` / ``.pdf`` siblings in ``{kind}/outputs/``.
    Cover letters use ``{id}_cl.py``; resumes use ``{id}.py``.
    """
    return data_path(kind, "outputs", f"{document_stem(kind, job_id)}.py")


def document_tex(kind: str, job_id: str) -> Path:
    """Per-job rendered ``.tex`` path under ``{kind}/outputs/`` (overlay-aware)."""
    return data_path(kind, "outputs", f"{document_stem(kind, job_id)}.tex")


def document_pdf(kind: str, job_id: str) -> Path:
    """Per-job compiled ``.pdf`` path under ``{kind}/outputs/`` (overlay-aware)."""
    return data_path(kind, "outputs", f"{document_stem(kind, job_id)}.pdf")


def template_path(kind: str) -> Path:
    """Scaffold template: ``{kind}/tailoring/_template.py`` (private preferred)."""
    return resolve_path(kind, "tailoring", "_template.py")


def resolve_document_py(kind: str, job_id: str) -> Path | None:
    """Locate a per-job source ``.py``: ``outputs/`` first, then legacy names.

    Preference:
      1. ``outputs/{stem}.py`` (resume ``{id}.py``, cover letter ``{id}_cl.py``)
      2. Cover letter only: pre-``_cl`` ``outputs/{id}.py``
      3. Legacy ``tailoring/{id}.py``

    Returns ``None`` when none of those exist.
    """
    primary = document_py(kind, job_id)
    if primary.exists():
        return primary
    if kind == "coverletter":
        pre_cl = data_path(kind, "outputs", f"{job_id}.py")
        if pre_cl.exists():
            return pre_cl
    legacy = data_path(kind, "tailoring", f"{job_id}.py")
    if legacy.exists():
        return legacy
    return None


def resolve_document_paths(kind: str, job_id: str) -> tuple[Path, Path]:
    """Return ``(source_py, tex_out)`` for *job_id* using overlay-aware helpers.

    Raises ``FileNotFoundError`` if the source ``.py`` cannot be found.
    """
    src = resolve_document_py(kind, job_id)
    if src is None:
        expected = document_py(kind, job_id)
        raise FileNotFoundError(
            f"{kind} source not found: {rel_to_root(expected)} "
            f"(also checked legacy {kind}/tailoring/{job_id}.py)"
        )
    return src, document_tex(kind, job_id)
