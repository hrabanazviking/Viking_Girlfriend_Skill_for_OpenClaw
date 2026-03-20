"""Unified timeline authority for turn-time and travel-time progression."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml


TIME_SEGMENTS = ["dawn", "morning", "midday", "afternoon", "evening", "night"]
SEASONS = ["spring", "summer", "autumn", "winter"]


@dataclass
class TimelineState:
    """Normalized simulation-time state."""

    year: int
    season: str
    time_of_day: str
    timeline_minutes: int


class TimelineService:
    """Single authority for clock advancement and travel duration rules."""

    def __init__(self, data_path: str = "data") -> None:
        self.data_path = Path(data_path)
        self.timeline_rules = self._load_yaml("world/timeline_rules.yaml", {})
        self.travel_tables = self._load_yaml("charts/travel_time_tables.yaml", {})

    def advance_turn(self, state: TimelineState) -> TimelineState:
        """Huginn advances world-clock by one narrative turn."""
        turn_minutes = int(self.timeline_rules.get("clock", {}).get("default_turn_minutes", 15))
        return self._apply_minutes(state, turn_minutes)

    def apply_local_move(self, state: TimelineState) -> TimelineState:
        """Small sub-location movement consumes short time."""
        return self._apply_minutes(state, 5)

    def apply_travel_journey(self, state: TimelineState, terrain: str = "road", distance_km: float = 8.0) -> TimelineState:
        """Longer city-to-city movement consumes weighted travel time."""
        multipliers = self.travel_tables.get("terrain_multipliers", {})
        base = self.travel_tables.get("base_speeds", {})
        speed = float(base.get("foot_km_per_hour", 4.5))
        multiplier = float(multipliers.get(terrain, 1.0))
        hours = max(0.1, (distance_km * multiplier) / max(0.1, speed))
        minutes = int(hours * 60)
        return self._apply_minutes(state, minutes)

    def event_timestamp(self, state: TimelineState, turn_id: int) -> str:
        """Return deterministic event timestamp for ordering confidence."""
        return f"Y{state.year}-{state.season}-{state.time_of_day}-T{turn_id}-M{state.timeline_minutes}"

    def _apply_minutes(self, state: TimelineState, minutes: int) -> TimelineState:
        timeline_minutes = max(0, int(state.timeline_minutes) + int(minutes))
        day_index = (timeline_minutes // 240) % len(TIME_SEGMENTS)
        time_of_day = TIME_SEGMENTS[day_index]

        season_index = SEASONS.index(state.season) if state.season in SEASONS else 0
        days_elapsed = timeline_minutes // (24 * 60)
        season_advance = days_elapsed // 90
        year_advance = season_advance // 4
        normalized_season = SEASONS[(season_index + season_advance) % 4]

        return TimelineState(
            year=int(state.year) + int(year_advance),
            season=normalized_season,
            time_of_day=time_of_day,
            timeline_minutes=timeline_minutes,
        )

    def _load_yaml(self, relative_path: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
        file_path = self.data_path / relative_path
        if not file_path.exists():
            return fallback
        with file_path.open("r", encoding="utf-8") as handle:
            loaded = yaml.safe_load(handle) or fallback
        return loaded if isinstance(loaded, dict) else fallback
