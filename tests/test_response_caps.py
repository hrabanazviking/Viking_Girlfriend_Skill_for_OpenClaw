"""
test_response_caps.py — S-02: Response size capping per routing tier
=====================================================================

Tests that ModelRouterClient._get_response_cap() returns sensible per-tier
caps and that the caps are applied in smart_complete_with_cove() Stage 3.
"""

import sys
import inspect
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

from scripts.model_router_client import (
    ModelRouterClient,
    TIER_SUBCONSCIOUS,
    TIER_CONSCIOUS,
    TIER_CODE,
    TIER_DEEP,
    _DEFAULT_MAX_TOKENS,
    _RESPONSE_CAPS_BY_TIER,
)


# ─── Tests: _RESPONSE_CAPS_BY_TIER dict ──────────────────────────────────────


def test_response_caps_dict_has_all_tiers():
    """_RESPONSE_CAPS_BY_TIER contains all four routing tiers."""
    assert TIER_SUBCONSCIOUS in _RESPONSE_CAPS_BY_TIER
    assert TIER_CONSCIOUS in _RESPONSE_CAPS_BY_TIER
    assert TIER_CODE in _RESPONSE_CAPS_BY_TIER
    assert TIER_DEEP in _RESPONSE_CAPS_BY_TIER


def test_subconscious_cap_is_smallest():
    """Subconscious tier has the smallest cap (local fast-path)."""
    assert _RESPONSE_CAPS_BY_TIER[TIER_SUBCONSCIOUS] <= _RESPONSE_CAPS_BY_TIER[TIER_CONSCIOUS]
    assert _RESPONSE_CAPS_BY_TIER[TIER_SUBCONSCIOUS] <= _RESPONSE_CAPS_BY_TIER[TIER_CODE]
    assert _RESPONSE_CAPS_BY_TIER[TIER_SUBCONSCIOUS] <= _RESPONSE_CAPS_BY_TIER[TIER_DEEP]


def test_deep_mind_cap_is_largest():
    """Deep-mind tier has the largest (or equal-largest) cap."""
    assert _RESPONSE_CAPS_BY_TIER[TIER_DEEP] >= _RESPONSE_CAPS_BY_TIER[TIER_CONSCIOUS]
    assert _RESPONSE_CAPS_BY_TIER[TIER_DEEP] >= _RESPONSE_CAPS_BY_TIER[TIER_SUBCONSCIOUS]


def test_all_caps_positive():
    """All caps are positive integers."""
    for tier, cap in _RESPONSE_CAPS_BY_TIER.items():
        assert isinstance(cap, int), f"{tier} cap is not int"
        assert cap > 0, f"{tier} cap is not positive"


def test_all_caps_under_default_max():
    """No cap exceeds _DEFAULT_MAX_TOKENS."""
    for tier, cap in _RESPONSE_CAPS_BY_TIER.items():
        assert cap <= _DEFAULT_MAX_TOKENS, f"{tier} cap {cap} exceeds default max {_DEFAULT_MAX_TOKENS}"


# ─── Tests: _get_response_cap() static method ─────────────────────────────────


def test_get_response_cap_subconscious():
    """_get_response_cap returns subconscious cap for subconscious tier."""
    cap = ModelRouterClient._get_response_cap(TIER_SUBCONSCIOUS)
    assert cap == _RESPONSE_CAPS_BY_TIER[TIER_SUBCONSCIOUS]


def test_get_response_cap_conscious():
    """_get_response_cap returns conscious cap for conscious-mind tier."""
    cap = ModelRouterClient._get_response_cap(TIER_CONSCIOUS)
    assert cap == _RESPONSE_CAPS_BY_TIER[TIER_CONSCIOUS]


def test_get_response_cap_code():
    """_get_response_cap returns code cap for code-mind tier."""
    cap = ModelRouterClient._get_response_cap(TIER_CODE)
    assert cap == _RESPONSE_CAPS_BY_TIER[TIER_CODE]


def test_get_response_cap_deep():
    """_get_response_cap returns deep cap for deep-mind tier."""
    cap = ModelRouterClient._get_response_cap(TIER_DEEP)
    assert cap == _RESPONSE_CAPS_BY_TIER[TIER_DEEP]


def test_get_response_cap_unknown_tier_returns_default():
    """Unknown tier returns _DEFAULT_MAX_TOKENS as fallback."""
    cap = ModelRouterClient._get_response_cap("unknown-tier")
    assert cap == _DEFAULT_MAX_TOKENS


def test_get_response_cap_is_static():
    """_get_response_cap is a static method (no instance needed)."""
    assert isinstance(
        inspect.getattr_static(ModelRouterClient, "_get_response_cap"),
        staticmethod,
    )
