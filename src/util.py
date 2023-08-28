import hashlib
import logging


def get_complement(artifactory_files, nexus_files):
    complement = {}
    for path, asset in artifactory_files.items():
        if path not in nexus_files:
            logging.debug("%s not at all in Nexus", path)
            complement[path] = asset
        else:
            artifactory_sha1 = asset["sha1"]
            nexus_sha1 = nexus_files[path]["checksum"]["sha1"]
            if artifactory_sha1 != nexus_sha1:
                logging.debug("%s with sha1 %s not in Nexus", path, artifactory_sha1)
                complement[path] = asset
    return complement


def read_file(file_path):  # pragma: no cover
    with open(file_path, "rb") as f:
        return f.read()


def get_checksums(the_bytes):
    return (
        hashlib.md5(the_bytes).hexdigest(),
        hashlib.sha1(the_bytes).hexdigest(),
        hashlib.sha256(the_bytes).hexdigest(),
    )
