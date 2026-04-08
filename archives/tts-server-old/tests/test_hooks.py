"""Tests for hook-to-state mapping, sentiment scaling, decay, and persistence."""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vibe_tts.state_manager import StateManager, STATE_BASELINE, STATE_NAMES


class TestHookAdjustments:
    def test_post_tool_use(self):
        mgr = StateManager()
        adj = mgr.get_hook_adjustments("PostToolUse", "Bash")
        assert ("confidence", 3) in adj
        assert ("momentum", 5) in adj
        assert ("contextSaturation", 3) in adj

    def test_pre_tool_use_bash(self):
        adj = StateManager().get_hook_adjustments("PreToolUse", "Bash")
        assert ("momentum", 2) in adj

    def test_pre_tool_use_edit(self):
        adj = StateManager().get_hook_adjustments("PreToolUse", "Edit")
        assert ("confidence", 2) in adj
        assert ("momentum", 2) in adj

    def test_pre_tool_use_read(self):
        adj = StateManager().get_hook_adjustments("PreToolUse", "Read")
        assert ("contextSaturation", 2) in adj

    def test_pre_tool_use_unknown_tool(self):
        adj = StateManager().get_hook_adjustments("PreToolUse", "Agent")
        assert adj == []

    def test_post_tool_use_failure(self):
        adj = StateManager().get_hook_adjustments("PostToolUseFailure")
        assert ("confidence", -5) in adj
        assert ("momentum", -8) in adj
        assert ("alignment", -2) in adj

    def test_session_start(self):
        adj = StateManager().get_hook_adjustments("SessionStart")
        assert ("confidence", 10) in adj
        assert ("contextSaturation", -20) in adj

    def test_unknown_event(self):
        adj = StateManager().get_hook_adjustments("UnknownEvent")
        assert adj == []


class TestScaleAdjustments:
    def test_low_intensity(self):
        mgr = StateManager()
        scaled = mgr.scale_adjustments([("confidence", 10)], intensity=20)
        assert scaled == [("confidence", 5.0)]

    def test_moderate_intensity(self):
        mgr = StateManager()
        scaled = mgr.scale_adjustments([("confidence", 10)], intensity=50)
        assert scaled == [("confidence", 10.0)]

    def test_high_intensity(self):
        mgr = StateManager()
        scaled = mgr.scale_adjustments([("confidence", 10)], intensity=85)
        assert scaled == [("confidence", 15.0)]

    def test_boundary_30(self):
        mgr = StateManager()
        scaled = mgr.scale_adjustments([("confidence", 10)], intensity=30)
        assert scaled == [("confidence", 10.0)]  # 30 is moderate

    def test_boundary_70(self):
        mgr = StateManager()
        scaled = mgr.scale_adjustments([("confidence", 10)], intensity=70)
        assert scaled == [("confidence", 10.0)]  # 70 is moderate


class TestApplySentiment:
    def test_proud_high_intensity(self):
        mgr = StateManager()
        result = mgr.apply_sentiment("proud", 85)
        # Base: confidence +8, alignment +5, momentum +5
        # Scale: x1.5 → confidence +12, alignment +7.5, momentum +7.5
        assert mgr.states["confidence"] == 62  # 50 + 12
        assert mgr.states["alignment"] == 58   # 50 + round(7.5)
        assert mgr.states["momentum"] == 58    # 50 + round(7.5)

    def test_calm_no_changes(self):
        mgr = StateManager()
        original = dict(mgr.states)
        mgr.apply_sentiment("calm", 50)
        assert mgr.states == original


class TestDecay:
    def test_zero_hours(self):
        mgr = StateManager()
        mgr.states["confidence"] = 80
        mgr.apply_decay(0)
        assert mgr.states["confidence"] == 80

    def test_one_hour(self):
        mgr = StateManager()
        mgr.states["confidence"] = 80
        mgr.apply_decay(1)
        # 50 + (80-50) * 0.5^1 = 50 + 15 = 65
        assert mgr.states["confidence"] == 65

    def test_four_hours(self):
        mgr = StateManager()
        mgr.states["confidence"] = 80
        mgr.apply_decay(4)
        # 50 + (80-50) * 0.5^4 = 50 + 1.875 ≈ 52
        assert mgr.states["confidence"] == 52

    def test_baseline_unchanged(self):
        mgr = StateManager()
        mgr.apply_decay(10)
        for name in STATE_NAMES:
            assert mgr.states[name] == STATE_BASELINE

    def test_below_baseline_decays_up(self):
        mgr = StateManager()
        mgr.states["confidence"] = 20
        mgr.apply_decay(1)
        # 50 + (20-50) * 0.5 = 50 - 15 = 35
        assert mgr.states["confidence"] == 35


class TestPersistence:
    def test_save_and_load(self):
        mgr = StateManager()
        mgr.states["confidence"] = 75
        mgr.states["momentum"] = 30
        mgr._session_id = "test-session"

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        try:
            mgr.save_state(path)

            mgr2 = StateManager()
            data = mgr2.load_state(path)

            assert data is not None
            assert mgr2.states["confidence"] == 75
            assert mgr2.states["momentum"] == 30
            assert mgr2._session_id == "test-session"
            assert "timestamp" in data
        finally:
            os.unlink(path)

    def test_load_missing_file(self):
        mgr = StateManager()
        result = mgr.load_state("/nonexistent/path.json")
        assert result is None

    def test_save_creates_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "sub", "dir", "state.json")
            mgr = StateManager()
            mgr.save_state(path)
            assert os.path.exists(path)
            with open(path) as f:
                data = json.load(f)
            assert "states" in data
            assert "feelings" in data
            assert "timestamp" in data

    def test_adjust_auto_saves(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        try:
            # Monkey-patch the default path
            import vibe_tts.state_manager as sm
            original = sm.ENTITY_STATE_PATH
            sm.ENTITY_STATE_PATH = path

            mgr = StateManager()
            mgr.adjust([("confidence", 10)])

            with open(path) as f:
                data = json.load(f)
            assert data["states"]["confidence"] == 60

            sm.ENTITY_STATE_PATH = original
        finally:
            os.unlink(path)
