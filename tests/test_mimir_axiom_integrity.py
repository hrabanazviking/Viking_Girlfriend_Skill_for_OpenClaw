"""
test_mimir_axiom_integrity.py — E-27: Axiom Integrity Sentinel
==============================================================

Tests for MimirWell._compute_axiom_hashes(), _save/_load_axiom_hashes(),
and check_axiom_integrity(). Also covers MimirHealthState.axiom_integrity field.
No ChromaDB required.
"""

import hashlib
import json
import sys
import os
import uuid
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

from scripts.mimir_well import (
    MimirWell,
    MimirHealthState,
    KnowledgeChunk,
    DataRealm,
    TruthTier,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _make_axiom_chunk(text: str) -> KnowledgeChunk:
    """DEEP_ROOT + ASGARD chunk — the only kind tracked by axiom integrity."""
    return KnowledgeChunk(
        chunk_id=str(uuid.uuid4()),
        text=text,
        source_file="core_identity.md",
        domain="character",
        realm=DataRealm.ASGARD,
        tier=TruthTier.DEEP_ROOT,
        level=3,
        metadata={},
    )


def _make_non_axiom_chunk(text: str) -> KnowledgeChunk:
    """TRUNK + MIDGARD chunk — not tracked by axiom integrity."""
    return KnowledgeChunk(
        chunk_id=str(uuid.uuid4()),
        text=text,
        source_file="history.md",
        domain="norse_culture",
        realm=DataRealm.MIDGARD,
        tier=TruthTier.TRUNK,
        level=1,
        metadata={},
    )


def _fresh_well(tmp_path) -> MimirWell:
    return MimirWell(
        persist_dir=str(tmp_path / "chromadb"),
        session_dir=str(tmp_path / "session"),
    )


# ─── Tests ────────────────────────────────────────────────────────────────────


def test_compute_axiom_hashes_only_axiom_chunks(tmp_path):
    """_compute_axiom_hashes includes only DEEP_ROOT+ASGARD chunks."""
    well = _fresh_well(tmp_path)
    axiom = _make_axiom_chunk("Sigrid is a völva of the Heathen Third Path.")
    non_axiom = _make_non_axiom_chunk("Vikings sailed longships across the North Sea.")

    well._chunks_by_id[axiom.chunk_id] = axiom
    well._chunks_by_id[non_axiom.chunk_id] = non_axiom

    hashes = well._compute_axiom_hashes()
    assert axiom.chunk_id in hashes
    assert non_axiom.chunk_id not in hashes


def test_compute_axiom_hashes_sha256_correctness(tmp_path):
    """Hash value matches sha256(text.encode('utf-8')).hexdigest()."""
    well = _fresh_well(tmp_path)
    text = "Honour above all — frith and wyrd bind us."
    chunk = _make_axiom_chunk(text)
    well._chunks_by_id[chunk.chunk_id] = chunk

    hashes = well._compute_axiom_hashes()
    expected = hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert hashes[chunk.chunk_id] == expected


def test_save_and_load_axiom_hashes(tmp_path):
    """Save then load produces the same hash dict."""
    well = _fresh_well(tmp_path)
    chunk = _make_axiom_chunk("The world tree Yggdrasil binds all nine realms.")
    well._chunks_by_id[chunk.chunk_id] = chunk

    well._axiom_hashes = well._compute_axiom_hashes()
    well._save_axiom_hashes()

    # Fresh well reads the saved file
    well2 = _fresh_well(tmp_path)
    well2._load_axiom_hashes()
    assert well2._axiom_hashes == well._axiom_hashes


def test_check_integrity_true_when_no_hashes_stored(tmp_path):
    """If no hashes have been saved yet, integrity is trivially True."""
    well = _fresh_well(tmp_path)
    chunk = _make_axiom_chunk("Soul anchor text.")
    well._chunks_by_id[chunk.chunk_id] = chunk
    # No _axiom_hashes loaded → empty dict
    assert well.check_axiom_integrity() is True


def test_check_integrity_true_after_save(tmp_path):
    """After computing + saving hashes, integrity check passes."""
    well = _fresh_well(tmp_path)
    chunk = _make_axiom_chunk("I am Sigrid, völva and skald of Heathen ways.")
    well._chunks_by_id[chunk.chunk_id] = chunk

    well._axiom_hashes = well._compute_axiom_hashes()
    assert well.check_axiom_integrity() is True


def test_check_integrity_false_on_text_mutation(tmp_path):
    """Mutating a chunk's text after hashing triggers a mismatch."""
    well = _fresh_well(tmp_path)
    text = "Original sacred identity text, unchanged."
    chunk = _make_axiom_chunk(text)
    well._chunks_by_id[chunk.chunk_id] = chunk

    # Save hash of original text
    well._axiom_hashes = well._compute_axiom_hashes()

    # Now replace with a modified chunk (simulating corruption)
    from dataclasses import replace as dc_replace
    corrupted = dc_replace(chunk, text="Tampered identity text, definitely changed!")
    well._chunks_by_id[chunk.chunk_id] = corrupted

    assert well.check_axiom_integrity() is False


def test_mimir_health_state_axiom_integrity_field():
    """MimirHealthState has axiom_integrity: bool defaulting to True."""
    from datetime import datetime, timezone
    state = MimirHealthState(
        overall="healthy",
        components={},
        dead_letters_total=0,
        last_reindex_at=None,
        reindex_count=0,
        checked_at=datetime.now(timezone.utc).isoformat(),
    )
    assert state.axiom_integrity is True


def test_axiom_hashes_file_location(tmp_path):
    """Axiom hashes file is saved under session_dir/axiom_hashes.json."""
    well = _fresh_well(tmp_path)
    chunk = _make_axiom_chunk("Bound to Freyja's golden light.")
    well._chunks_by_id[chunk.chunk_id] = chunk
    well._axiom_hashes = well._compute_axiom_hashes()
    well._save_axiom_hashes()

    expected = tmp_path / "session" / "axiom_hashes.json"
    assert expected.exists()
    data = json.loads(expected.read_text())
    assert chunk.chunk_id in data
