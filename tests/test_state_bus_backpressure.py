"""
tests/test_state_bus_backpressure.py -- E-04: StateBus backpressure counters
8 tests covering inbound/state subscriber drop counting and metric reporting.
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

import pytest
from scripts.state_bus import StateBus, InboundEvent, StateEvent


def _run(coro):
    return asyncio.run(coro)


class TestStateBusBackpressure:

    def _make_bus(self, sub_maxsize=2):
        return StateBus(subscriber_queue_maxsize=sub_maxsize)

    def test_inbound_subscriber_dropped_counter_starts_zero(self):
        bus = self._make_bus()
        assert bus._inbound_subscriber_dropped == 0

    def test_state_subscriber_dropped_counter_starts_zero(self):
        bus = self._make_bus()
        assert bus._state_subscriber_dropped == 0

    def test_inbound_drop_increments_counter(self):
        """Fill a subscriber queue, then verify drop counter increments."""
        bus = self._make_bus(sub_maxsize=1)

        async def scenario():
            # Register a subscriber queue directly (maxsize=1)
            queue = asyncio.Queue(maxsize=1)
            bus._inbound_topics["test_channel"].append(queue)
            # Don't consume — let it fill
            event = InboundEvent(channel="test_channel", session_id="s", user_id="u", text="hi")
            # First publish fills the queue
            await bus.publish_inbound(event)
            # Second publish should trigger drop (queue full)
            await bus.publish_inbound(event)
            # Third publish also drops
            await bus.publish_inbound(event)

        _run(scenario())
        assert bus._inbound_subscriber_dropped >= 1

    def test_state_drop_increments_counter(self):
        """Fill a state subscriber queue, verify drop counter increments."""
        bus = self._make_bus(sub_maxsize=1)

        async def scenario():
            # Register a state subscriber
            queue = asyncio.Queue(maxsize=1)
            bus._state_topics["test_event"].append(queue)

            event = StateEvent(source_module="test", event_type="test_event", payload={})
            # First fills the queue
            await bus.publish_state(event)
            # Second should drop (queue full)
            await bus.publish_state(event)
            await bus.publish_state(event)

        _run(scenario())
        assert bus._state_subscriber_dropped >= 1

    def test_dropped_counters_appear_in_metrics(self):
        bus = self._make_bus(sub_maxsize=1)

        async def scenario():
            queue = asyncio.Queue(maxsize=1)
            bus._state_topics["evt"].append(queue)
            e = StateEvent(source_module="m", event_type="evt", payload={})
            await bus.publish_state(e)
            await bus.publish_state(e)

        _run(scenario())
        metrics = bus.stats()
        assert "state_subscriber_dropped" in metrics
        assert "inbound_subscriber_dropped" in metrics

    def test_no_drop_when_queue_has_space(self):
        bus = self._make_bus(sub_maxsize=100)

        async def scenario():
            event = InboundEvent(channel="ch", session_id="s", user_id="u", text="hi")
            for _ in range(5):
                await bus.publish_inbound(event)

        _run(scenario())
        assert bus._inbound_subscriber_dropped == 0

    def test_main_queue_drop_still_separate_from_subscriber_drop(self):
        """Main queue drop (state_dropped) must not be confused with subscriber drops."""
        bus = self._make_bus()
        # Confirm they are separate counters
        assert bus._state_dropped == 0
        assert bus._state_subscriber_dropped == 0

    def test_wildcard_subscriber_drop_also_counted(self):
        """Drops on wildcard subscriptions are counted in the same counter."""
        bus = self._make_bus(sub_maxsize=1)

        async def scenario():
            queue = asyncio.Queue(maxsize=1)
            bus._inbound_topics["*"].append(queue)
            event = InboundEvent(channel="any_channel", session_id="s", user_id="u", text="hi")
            await bus.publish_inbound(event)
            await bus.publish_inbound(event)
            await bus.publish_inbound(event)

        _run(scenario())
        assert bus._inbound_subscriber_dropped >= 1
