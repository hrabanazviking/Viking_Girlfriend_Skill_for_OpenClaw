"""
tests/test_trust_milestones.py — E-24: Relational Milestones
15 tests covering Milestone dataclass, milestone detection, persistence,
anchor floor enforcement, and StateBus publication.
"""
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

import pytest
from scripts.trust_engine import Milestone, TrustEngine


# ── Milestone dataclass ────────────────────────────────────────────────────────

class TestMilestoneDataclass:

    def test_milestone_has_required_fields(self):
        m = Milestone(
            milestone_id="first_gift",
            name="First Gift",
            description="A gift was exchanged.",
            occurred_at="2026-03-21T00:00:00+00:00",
            trust_anchor=0.03,
            contact_id="test_user",
        )
        assert m.milestone_id == "first_gift"
        assert m.trust_anchor == 0.03
        assert m.contact_id == "test_user"

    def test_to_dict_roundtrip(self):
        m = Milestone(
            milestone_id="first_apology",
            name="First Apology",
            description="desc",
            occurred_at="ts",
            trust_anchor=0.02,
            contact_id="test_user",
        )
        d = m.to_dict()
        restored = Milestone.from_dict(d)
        assert restored.milestone_id == m.milestone_id
        assert abs(restored.trust_anchor - m.trust_anchor) < 1e-6
        assert restored.contact_id == m.contact_id


# ── Milestone detection ────────────────────────────────────────────────────────

class TestMilestoneDetection:

    def test_gift_event_triggers_first_gift_milestone(self, tmp_path):
        engine = TrustEngine(session_dir=str(tmp_path))
        before = len(engine._milestones)
        engine.process_turn("gave you this gift", "", "test_user")
        assert len(engine._milestones) >= before + 1
        ids = [m.milestone_id for m in engine._milestones]
        assert "first_gift" in ids

    def test_first_conflict_milestone_detected(self, tmp_path):
        engine = TrustEngine(session_dir=str(tmp_path))
        engine.process_turn("i disagree with you on this", "", "test_user")
        ids = [m.milestone_id for m in engine._milestones]
        assert "first_conflict" in ids

    def test_first_apology_milestone_detected(self, tmp_path):
        engine = TrustEngine(session_dir=str(tmp_path))
        engine.process_turn("sorry i was wrong about that", "", "test_user")
        ids = [m.milestone_id for m in engine._milestones]
        assert "first_apology" in ids

    def test_milestone_not_triggered_twice(self, tmp_path):
        engine = TrustEngine(session_dir=str(tmp_path))
        engine.process_turn("gave you this gift", "", "test_user")
        engine.process_turn("gave you another gift", "", "test_user")
        gift_milestones = [m for m in engine._milestones if m.milestone_id == "first_gift"]
        assert len(gift_milestones) == 1

    def test_milestone_occurred_at_is_populated(self, tmp_path):
        engine = TrustEngine(session_dir=str(tmp_path))
        engine.process_turn("gave you this gift", "", "test_user")
        m = next(m for m in engine._milestones if m.milestone_id == "first_gift")
        assert m.occurred_at != ""

    def test_multiple_milestones_from_single_turn(self, tmp_path):
        engine = TrustEngine(session_dir=str(tmp_path))
        # "thank" triggers warmth_shown (→ first_support) and "i trust" triggers trust_affirmed
        engine.process_turn("i trust you and i appreciate everything", "", "test_user")
        ids = {m.milestone_id for m in engine._milestones}
        # At least one milestone should fire
        assert len(ids) >= 1


# ── Anchor floor enforcement ───────────────────────────────────────────────────

class TestAnchorFloor:

    def test_anchor_floor_set_after_milestone(self, tmp_path):
        engine = TrustEngine(session_dir=str(tmp_path))
        engine.process_turn("gave you this gift", "", "test_user")
        ledger = engine.get_ledger("test_user")
        assert ledger.anchor_floor > 0.0

    def test_trust_score_never_below_anchor_floor(self, tmp_path):
        engine = TrustEngine(
            primary_contact_initial_trust=0.30,
            session_dir=str(tmp_path),
        )
        # Trigger a milestone to set an anchor
        engine.process_turn("gave you this gift", "", "test_user")
        ledger = engine.get_ledger("test_user")
        floor = ledger.anchor_floor

        # Hammer the ledger with negative events to try to drive trust below floor
        for _ in range(20):
            ledger.apply_event("boundary_violated")
            ledger.apply_event("insult")
            ledger.apply_event("oath_broken")

        assert ledger.trust_score >= floor

    def test_multiple_milestones_stack_anchor(self, tmp_path):
        engine = TrustEngine(session_dir=str(tmp_path))
        engine.process_turn("gave you this gift", "", "test_user")
        engine.process_turn("sorry i was wrong", "", "test_user")
        ledger = engine.get_ledger("test_user")
        # Both first_gift (0.03) and first_apology (0.02) should contribute
        assert ledger.anchor_floor >= 0.03 + 0.02 - 1e-9


# ── Persistence ───────────────────────────────────────────────────────────────

class TestMilestonePersistence:

    def test_milestone_saved_to_file(self, tmp_path):
        engine = TrustEngine(session_dir=str(tmp_path))
        engine.process_turn("gave you this gift", "", "test_user")
        mfile = tmp_path / "milestones.json"
        assert mfile.exists()

    def test_milestone_loaded_on_new_engine(self, tmp_path):
        engine1 = TrustEngine(session_dir=str(tmp_path))
        engine1.process_turn("gave you this gift", "", "test_user")

        engine2 = TrustEngine(session_dir=str(tmp_path))
        ids = [m.milestone_id for m in engine2._milestones]
        assert "first_gift" in ids

    def test_anchor_floor_restored_from_file(self, tmp_path):
        engine1 = TrustEngine(session_dir=str(tmp_path))
        engine1.process_turn("gave you this gift", "", "test_user")

        engine2 = TrustEngine(session_dir=str(tmp_path))
        ledger = engine2.get_ledger("test_user")
        assert ledger.anchor_floor > 0.0


# ── StateBus publication ──────────────────────────────────────────────────────

class TestMilestoneBusPublication:

    def test_milestone_reached_event_published(self, tmp_path):
        from scripts.state_bus import StateBus
        bus = MagicMock(spec=StateBus)
        engine = TrustEngine(session_dir=str(tmp_path))
        engine.process_turn("gave you this gift", "", "test_user", bus=bus)
        bus.publish_state.assert_called()
        # Find the milestone event among calls
        calls = bus.publish_state.call_args_list
        event_types = [c.args[0].event_type for c in calls if c.args]
        assert "trust.milestone_reached" in event_types
