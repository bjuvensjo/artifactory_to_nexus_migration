import util


def test_get_checksums():
    assert len(util.get_checksums(b"Hello World!")) == 3
