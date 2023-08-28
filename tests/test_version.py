import pytest

import version


@pytest.fixture
def versions():
    return [
        "1.0.0-SNAPSHOT",
        "2.0.0-SNAPSHOT",
        "100.0.0-SNAPSHOT",
        "1.0.0-rc100",
        "2.0.0-rc100",
        "100.0.0-rc1",
        "100.0.0-rc2",
        "1.0.0",
        "1.0.2",
        "1.0.1",
    ]


def test_get_latest_snapshot(versions):
    assert version.get_latest_snapshot(versions=versions) == ["100.0.0-SNAPSHOT"]


def test_get_latest_rc(versions):
    assert version.get_latest_rc(versions=versions) == ["100.0.0-rc2"]


def test_get_latest_fixed(versions):
    assert version.get_latest_fixed(versions=versions) == ["1.0.2"]
