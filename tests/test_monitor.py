

from lnu.monitor import get_snapshot

def test_snapshot_returns_dict():
    snap = get_snapshot()
    assert isinstance(snap, dict)

def test_snapshot_has_required_keys():
    snap = get_snapshot()
    required_keys = ["ts", "cpu_percent", "virtual_memory", "disk", "net"]
    
    for key in required_keys:
        assert key in snap

def test_snapshot_memory_and_disk_are_dicts():
    snap = get_snapshot()
    assert isinstance(snap["virtual_memory"], dict)
    assert isinstance(snap["disk"], dict)
    assert "percent" in snap["virtual_memory"]
    assert "percent" in snap["disk"]
