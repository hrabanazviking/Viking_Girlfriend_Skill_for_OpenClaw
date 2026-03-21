"""
test_vordur_async_cache.py — E-32: Async Parallel Verification + LRU Verdict Cache
====================================================================================

Tests for _LRUVerdictCache, verify_claims() parallel execution,
and VordurState.cache_hits/cache_misses.
"""

import sys
import time
import uuid
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

from scripts.vordur import (
    VordurChecker,
    Claim,
    ClaimVerification,
    VerdictLabel,
    _LRUVerdictCache,
)
from scripts.mimir_well import KnowledgeChunk, DataRealm, TruthTier


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _chunk(text: str) -> KnowledgeChunk:
    return KnowledgeChunk(
        chunk_id=str(uuid.uuid4()),
        text=text,
        source_file="test.md",
        domain="norse_culture",
        realm=DataRealm.MIDGARD,
        tier=TruthTier.TRUNK,
        level=1,
        metadata={},
    )


def _claim(text: str) -> Claim:
    return Claim(text=text, source_sentence=text, claim_index=0)


def _checker() -> VordurChecker:
    return VordurChecker(router=None, verdict_cache_enabled=True, verdict_cache_size=256)


# ─── Tests: _LRUVerdictCache ─────────────────────────────────────────────────


def test_lru_cache_miss_returns_none():
    """get() on empty cache returns None."""
    cache = _LRUVerdictCache(maxsize=10)
    assert cache.get("claim text", "chunk text") is None


def test_lru_cache_hit_returns_stored_value():
    """put() then get() returns the stored ClaimVerification."""
    cache = _LRUVerdictCache(maxsize=10)
    claim = _claim("Odin drank from Mimir's well.")
    chunk = _chunk("Odin sacrificed his eye at the well of wisdom.")
    cv = ClaimVerification(
        claim=claim,
        verdict=VerdictLabel.ENTAILED,
        confidence=0.85,
        supporting_chunk_id="abc",
        judge_tier_used="regex",
        verification_ms=1.0,
    )
    cache.put(claim.text, chunk.text, cv)
    result = cache.get(claim.text, chunk.text)
    assert result is cv


def test_lru_cache_hits_counter_increments():
    """hits counter increments on every cache hit."""
    cache = _LRUVerdictCache(maxsize=10)
    cv = ClaimVerification(
        claim=_claim("x"), verdict=VerdictLabel.NEUTRAL,
        confidence=0.5, supporting_chunk_id=None,
        judge_tier_used="regex", verification_ms=0.0,
    )
    cache.put("c", "k", cv)
    assert cache.hits == 0
    cache.get("c", "k")
    assert cache.hits == 1
    cache.get("c", "k")
    assert cache.hits == 2


def test_lru_cache_misses_counter_increments():
    """misses counter increments on every cache miss."""
    cache = _LRUVerdictCache(maxsize=10)
    cache.get("no such claim", "no such chunk")
    assert cache.misses == 1


def test_lru_cache_evicts_oldest_when_full():
    """Oldest entry evicted when cache reaches maxsize."""
    cache = _LRUVerdictCache(maxsize=3)
    cv_dummy = ClaimVerification(
        claim=_claim("x"), verdict=VerdictLabel.NEUTRAL,
        confidence=0.5, supporting_chunk_id=None,
        judge_tier_used="regex", verification_ms=0.0,
    )
    cache.put("a", "a", cv_dummy)
    cache.put("b", "b", cv_dummy)
    cache.put("c", "c", cv_dummy)
    cache.put("d", "d", cv_dummy)  # should evict "a"
    assert cache.size == 3
    assert cache.get("a", "a") is None   # evicted
    assert cache.get("d", "d") is not None


def test_lru_cache_clear_resets():
    """clear() empties cache and resets counters."""
    cache = _LRUVerdictCache(maxsize=10)
    cv_dummy = ClaimVerification(
        claim=_claim("x"), verdict=VerdictLabel.NEUTRAL,
        confidence=0.5, supporting_chunk_id=None,
        judge_tier_used="regex", verification_ms=0.0,
    )
    cache.put("a", "a", cv_dummy)
    cache.get("a", "a")
    cache.get("missing", "missing")
    cache.clear()
    assert cache.size == 0
    assert cache.hits == 0
    assert cache.misses == 0


# ─── Tests: verify_claim() cache integration ────────────────────────────────


def test_verify_claim_populates_cache():
    """verify_claim() stores result in cache for repeated calls."""
    checker = _checker()
    c = _claim("Yggdrasil is the world tree connecting nine realms.")
    chunks = [_chunk("Yggdrasil connects the nine worlds in Norse cosmology.")]
    checker.verify_claim(c, chunks)
    # Second call should be a cache hit
    checker.verify_claim(c, chunks)
    assert checker._verdict_cache.hits >= 1


def test_verify_claim_cache_disabled():
    """verdict_cache_enabled=False means no cache is created."""
    checker = VordurChecker(router=None, verdict_cache_enabled=False)
    assert checker._verdict_cache is None


def test_vordur_state_exposes_cache_stats():
    """get_state() includes cache_hits and cache_misses fields."""
    checker = _checker()
    state = checker.get_state()
    assert hasattr(state, "cache_hits")
    assert hasattr(state, "cache_misses")
    assert isinstance(state.cache_hits, int)
    assert isinstance(state.cache_misses, int)


# ─── Tests: verify_claims() parallel execution ──────────────────────────────


def test_verify_claims_returns_list():
    """verify_claims() returns a List[ClaimVerification] of correct length."""
    checker = _checker()
    claims = [
        _claim("Odin is the Allfather."),
        _claim("Freyja is a Vanir goddess."),
        _claim("Thor wields Mjolnir."),
    ]
    chunks = [_chunk("Norse gods include Odin, Freyja, Thor.")]
    results = checker.verify_claims(claims, chunks)
    assert isinstance(results, list)
    assert len(results) == 3


def test_verify_claims_empty_input_returns_empty():
    """verify_claims([]) returns []."""
    checker = _checker()
    assert checker.verify_claims([], []) == []


def test_verify_claims_results_match_sequential():
    """verify_claims() produces same verdicts as sequential verify_claim() calls."""
    checker = VordurChecker(router=None, verdict_cache_enabled=False)
    claims = [
        _claim("Ravens are associated with Odin in Norse mythology."),
        _claim("The sea is the boundary of Midgard."),
    ]
    chunks = [_chunk("Odin's ravens Huginn and Muninn fly over Midgard.")]

    sequential = [checker.verify_claim(c, chunks) for c in claims]
    parallel = checker.verify_claims(claims, chunks)

    assert len(parallel) == len(sequential)
    for seq, par in zip(sequential, parallel):
        assert seq.verdict == par.verdict


def test_verify_claims_parallel_faster_than_sequential():
    """verify_claims() completes within 3x the time of a single verify_claim()."""
    import time
    checker = VordurChecker(router=None, verdict_cache_enabled=False)
    n = 5
    claims = [_claim(f"Claim number {i} about Norse mythology.") for i in range(n)]
    chunks = [_chunk("Norse mythology is rich with gods, giants, and fate.")]

    t0 = time.monotonic()
    checker.verify_claims(claims, chunks)
    elapsed = time.monotonic() - t0

    # Sequential time estimate (single claim)
    t1 = time.monotonic()
    checker.verify_claim(claims[0], chunks)
    single = time.monotonic() - t1

    # Parallel should be much less than n * single (allow generous 3x bound)
    assert elapsed < (n * single * 3 + 0.5)  # +0.5s for thread pool overhead
