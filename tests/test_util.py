import util


def test_get_checksums():
    assert len(util.get_checksums("Hello World!".encode("utf-8"))) == 3
