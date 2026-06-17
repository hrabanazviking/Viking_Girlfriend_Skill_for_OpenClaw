"""
test_synthesizer_hotreload.py — E-31: Hot-Reload Identity
==========================================================

Tests for PromptSynthesizer.reload_identity(), start_watcher(),
stop_watcher(), and _IdentityFileWatcher. Uses tmp_path for real
file writes to verify polling-based change detection.
"""

import sys
import os
import time
import threading
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

from scripts.prompt_synthesizer import PromptSynthesizer
from scripts.state_bus import StateBus


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _synth(tmp_path, identity_text: str = "", soul_text: str = "") -> PromptSynthesizer:
    """Synthesizer with real identity/soul files in tmp_path."""
    (tmp_path / "core_identity.md").write_text(identity_text, encoding="utf-8")
    (tmp_path / "SOUL.md").write_text(soul_text, encoding="utf-8")
    return PromptSynthesizer(
        data_root=str(tmp_path),
        skaldic_injection=False,
    )


# ─── Tests: reload_identity ──────────────────────────────────────────────────


def test_reload_identity_updates_identity_text(tmp_path):
    """reload_identity() picks up changes written to core_identity.md."""
    synth = _synth(tmp_path, identity_text="Original identity text.")
    assert "Original" in synth._identity_text

    (tmp_path / "core_identity.md").write_text("Updated identity content!", encoding="utf-8")
    synth.reload_identity()

    assert "Updated" in synth._identity_text
    assert "Original" not in synth._identity_text


def test_reload_identity_updates_soul_text(tmp_path):
    """reload_identity() picks up changes written to SOUL.md."""
    synth = _synth(tmp_path, soul_text="Original soul text.")
    (tmp_path / "SOUL.md").write_text("Renewed soul content.", encoding="utf-8")
    synth.reload_identity()
    assert "Renewed" in synth._soul_text


def test_reload_identity_is_thread_safe(tmp_path):
    """Concurrent reload_identity() calls don't crash or corrupt state."""
    synth = _synth(tmp_path, identity_text="Base identity.")
    errors = []

    def reload_loop():
        for _ in range(20):
            try:
                synth.reload_identity()
            except Exception as exc:
                errors.append(exc)

    threads = [threading.Thread(target=reload_loop) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5.0)

    assert not errors


def test_reload_identity_survives_missing_file(tmp_path):
    """reload_identity() does not raise when a file is missing — logs warning."""
    synth = _synth(tmp_path, identity_text="Safe identity.")
    os.remove(tmp_path / "core_identity.md")
    # Must not raise
    synth.reload_identity()


def test_reload_identity_does_not_set_degraded_on_success(tmp_path):
    """Successful reload keeps _degraded False."""
    synth = _synth(tmp_path, identity_text="Good identity.", soul_text="Good soul.")
    (tmp_path / "core_identity.md").write_text("New identity.", encoding="utf-8")
    synth._degraded = False
    synth.reload_identity()
    # _degraded should not be flipped True by a successful reload
    assert synth._degraded is False


# ─── Tests: start_watcher / stop_watcher ────────────────────────────────────


def test_start_watcher_creates_watcher_thread(tmp_path):
    """start_watcher() creates a running watcher thread."""
    synth = _synth(tmp_path)
    synth.start_watcher()
    try:
        assert synth._watcher is not None
        assert synth._watcher._thread.is_alive()
    finally:
        synth.stop_watcher()


def test_stop_watcher_kills_thread(tmp_path):
    """stop_watcher() stops the background thread and sets _watcher to None."""
    synth = _synth(tmp_path)
    synth.start_watcher()
    thread = synth._watcher._thread
    synth.stop_watcher()
    thread.join(timeout=3.0)
    assert not thread.is_alive()
    assert synth._watcher is None


def test_start_watcher_idempotent(tmp_path):
    """Calling start_watcher() twice does not create a second watcher."""
    synth = _synth(tmp_path)
    synth.start_watcher()
    first_watcher = synth._watcher
    synth.start_watcher()   # second call — should be no-op
    assert synth._watcher is first_watcher
    synth.stop_watcher()


def test_watcher_detects_file_change_and_reloads(tmp_path):
    """Watcher polls file changes and calls reload_identity() automatically."""
    synth = _synth(tmp_path, identity_text="Before change.")

    # Patch reload_identity to capture calls
    reload_called = threading.Event()
    original_reload = synth.reload_identity

    def patched_reload():
        original_reload()
        reload_called.set()

    synth.reload_identity = patched_reload

    # Use very short poll interval for the test
    from scripts.prompt_synthesizer import _IdentityFileWatcher
    # _snapshot_mtimes() runs in __init__ — write the new file AFTER construction
    synth._watcher = _IdentityFileWatcher(synth, bus=None, poll_interval_s=0.1)
    synth._watcher.start()

    try:
        # Modify the file to trigger detection on the next poll cycle
        time.sleep(0.1) # Brief delay before modification to ensure mtime detects change
        (tmp_path / "core_identity.md").write_text("After change!", encoding="utf-8")
        # Wait up to 2s for the watcher to detect and reload
        triggered = reload_called.wait(timeout=2.0)
        assert triggered, "Watcher did not detect file change within 2 seconds"
        assert "After change!" in synth._identity_text
    finally:
        synth._watcher.stop()
        synth._watcher = None


def test_watcher_publishes_state_event_on_reload(tmp_path):
    """Watcher calls _publish_reload on file change — mocked bus receives it."""
    from unittest import mock
    from scripts.state_bus import StateEvent
    from scripts.prompt_synthesizer import _IdentityFileWatcher

    synth = _synth(tmp_path, identity_text="Initial content.")

    mock_bus = mock.MagicMock()
    # publish_state is async; make it return a coroutine-like object
    mock_bus.publish_state = mock.MagicMock(return_value=None)

    reload_called = threading.Event()
    original_reload = synth.reload_identity

    def patched_reload():
        original_reload()
        reload_called.set()

    synth.reload_identity = patched_reload

    synth._watcher = _IdentityFileWatcher(synth, bus=mock_bus, poll_interval_s=0.1)
    synth._watcher.start()

    try:
        time.sleep(0.1) # Brief delay before modification to ensure mtime detects change
        (tmp_path / "core_identity.md").write_text("Changed content!", encoding="utf-8")
        reload_called.wait(timeout=2.0)
        time.sleep(0.1)  # brief wait for _publish_reload to be called
        assert mock_bus.publish_state.called
        # First call's first positional arg should be a StateEvent
        event_arg = mock_bus.publish_state.call_args[0][0]
        assert isinstance(event_arg, StateEvent)
        assert event_arg.event_type == "persona.identity_reloaded"
    finally:
        synth._watcher.stop()
        synth._watcher = None
