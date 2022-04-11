#!/usr/bin/env python3
import hashlib
import logging

from multiprocessing.dummy import Pool


def get_complement(from_artifactory_files, to_artifactory_files):
    complement = {}
    for path, asset in from_artifactory_files.items():
        if path not in to_artifactory_files:
            logging.debug('%s not at all in To Artifactory', path)
            complement[path] = asset
        else:
            from_artifactory_sha1 = asset['sha1']
            to_artifactory_sha1 = to_artifactory_files[path]['sha1']
            if from_artifactory_sha1 != to_artifactory_sha1:
                logging.debug('%s with sha1 %s not in To Artifactory', path, from_artifactory_sha1)
                complement[path] = asset
    return complement


def read_file(file_path):  # pragma: no cover
    with open(file_path, 'rb') as f:
        return f.read()


def get_checksums(the_bytes):
    return (
        hashlib.md5(the_bytes).hexdigest(),
        hashlib.sha1(the_bytes).hexdigest(),
        hashlib.sha256(the_bytes).hexdigest()
    )


def sha1sum(file_path):
    return get_checksums(read_file(file_path))[1]


def pmap_unordered(f, iterable, chunksize=1, processes=10):
    with Pool(processes=processes) as pool:
        completed_processes = pool.imap_unordered(f, iterable, chunksize=chunksize)
        for cp in completed_processes:
            yield cp
