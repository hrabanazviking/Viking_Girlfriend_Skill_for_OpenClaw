"""
tests/test_scheduler_seasonal.py -- E-14: Seasonal Awareness
10 tests covering SeasonalState, _get_seasonal_state(), hemisphere flip,
solstice proximity, modifier values, and integration with get_seasonal_state().
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

import pytest
from scripts.scheduler import SchedulerService, SeasonalState, _get_seasonal_state

class TestSeasonalState:

    def test_seasonal_state_has_required_fields(self):
        ss = _get_seasonal_state("north", date(2026, 1, 15))
        assert hasattr(ss, "season_name")
        assert hasattr(ss, "energy_modifier")
        assert hasattr(ss, "light_quality")
        assert hasattr(ss, "solstice_days_away")

    def test_january_north_is_winter(self):
        ss = _get_seasonal_state("north", date(2026, 1, 15))
        assert "winter" in ss.season_name.lower()

    def test_july_north_is_summer(self):
        ss = _get_seasonal_state("north", date(2026, 7, 15))
        assert "summer" in ss.season_name.lower()

    def test_south_hemisphere_january_is_summer(self):
        """In the southern hemisphere, January should be a summer band."""
        ss = _get_seasonal_state("south", date(2026, 1, 15))
        assert "summer" in ss.season_name.lower()

    def test_south_hemisphere_july_is_winter(self):
        ss = _get_seasonal_state("south", date(2026, 7, 15))
        assert "winter" in ss.season_name.lower()

    def test_energy_modifier_is_float(self):
        ss = _get_seasonal_state("north", date(2026, 4, 1))
        assert isinstance(ss.energy_modifier, float)

    def test_energy_modifier_in_valid_range(self):
        for month in range(1, 13):
            ss = _get_seasonal_state("north", date(2026, month, 15))
            assert 0.5 <= ss.energy_modifier <= 1.5

    def test_solstice_days_away_non_negative(self):
        ss = _get_seasonal_state("north", date(2026, 6, 21))
        assert ss.solstice_days_away >= 0

    def test_solstice_days_away_near_zero_at_summer_solstice(self):
        ss = _get_seasonal_state("north", date(2026, 6, 21))
        assert ss.solstice_days_away <= 7  # within a week of solstice

    def test_get_seasonal_state_method_returns_seasonal_state(self):
        svc = SchedulerService(hemisphere="north")
        result = svc.get_seasonal_state(today=date(2026, 3, 21))
        assert isinstance(result, SeasonalState)
