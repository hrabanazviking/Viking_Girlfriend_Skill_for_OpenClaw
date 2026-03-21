"""
tests/test_bio_cycle_length.py -- E-12: BioEngine Variable Cycle Length
6 tests covering valid range acceptance, out-of-range fallback, and
config loading via from_config().
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

import pytest
from scripts.bio_engine import BioEngine

class TestBioCycleLength:

    def _eng(self, cycle_length: int = 28) -> BioEngine:
        return BioEngine(birth_date=None, cycle_start_date=None, cycle_length=cycle_length)

    def test_default_cycle_length_is_28(self):
        eng = BioEngine(birth_date=None, cycle_start_date=None)
        assert eng._cycle_length == 28

    def test_valid_lower_boundary_21_accepted(self):
        assert self._eng(21)._cycle_length == 21

    def test_valid_upper_boundary_35_accepted(self):
        assert self._eng(35)._cycle_length == 35

    def test_below_range_falls_back_to_28(self):
        assert self._eng(15)._cycle_length == 28

    def test_above_range_falls_back_to_28(self):
        assert self._eng(40)._cycle_length == 28

    def test_from_config_reads_cycle_length_days_key(self):
        config = {
            "bio": {
                "cycle_length_days": 30,
                "chaos_factor": 0.0,
                "session_seed": 0,
            }
        }
        eng = BioEngine.from_config(config)
        assert eng._cycle_length == 30
