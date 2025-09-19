# tests/test_monitor.py
# This is a basic "smoke test" to ensure the get_snapshot function
# runs without errors and returns a dictionary with the expected top-level keys.

# To run this test:
# 1. Make sure your venv is active.
# 2. pip install pytest
# 3. Run 'pytest' from the root of your project directory.

from lnu.monitor import get_snapshot

def test_snapshot_returns_dict():
    """Tests that get_snapshot returns a dictionary."""
    snap = get_snapshot()
    assert isinstance(snap, dict)

def test_snapshot_has_required_keys():
    """Tests that the snapshot contains all the essential keys."""
    snap = get_snapshot()
    required_keys = ["ts", "cpu_percent", "virtual_memory", "disk", "net"]
    
    for key in required_keys:
        assert key in snap

def test_snapshot_memory_and_disk_are_dicts():
    """Tests that nested keys also have the expected structure."""
    snap = get_snapshot()
    assert isinstance(snap["virtual_memory"], dict)
    assert isinstance(snap["disk"], dict)
    assert "percent" in snap["virtual_memory"]
    assert "percent" in snap["disk"]
