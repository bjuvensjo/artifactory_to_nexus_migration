#!/usr/bin/env python3
import logging
from os import makedirs, remove
from os.path import dirname
from sys import stdout

import config
from artifactory import get_latest_repo_files as get_artifactory_files, download
from nexus import get_latest_repo_files as get_nexus_files, upload
from util import get_complement

logging.basicConfig(stream=stdout, level=logging.INFO)


def get_repo_keys(repo_key):
    if type(repo_key) is str:
        return repo_key, repo_key
    return repo_key


def migrate(artifactory_complement, work_dir, from_repo_key, to_repo_key, artifactory_spec, nexus_spec):
    success_count = 0
    failure_count = 0
    total_count = len(artifactory_complement)
    for path, asset in artifactory_complement.items():
        logging.info('%s of %s', success_count + failure_count + 1, total_count)
        try:
            output_file = f'{work_dir}/{path}'
            makedirs(dirname(output_file), exist_ok=True)
            download(output_file, artifactory_spec, from_repo_key, asset['uri'], asset['sha1'])
            upload(output_file, nexus_spec, to_repo_key, path)
            remove(output_file)
            success_count += 1
        except OSError as e:
            failure_count += 1
            logging.exception('Can not migrate: %s', asset)
    return failure_count, success_count


def main(cfg):
    for repo_key in cfg.repositories:
        from_repo_key, to_repo_key = get_repo_keys(repo_key)
        logging.info('From repo key: %s, To repo key: %s', from_repo_key, to_repo_key)

        artifactory_files = get_artifactory_files(cfg.artifactory_spec, from_repo_key)
        logging.debug('Artifactory %s files: %s', from_repo_key, artifactory_files)
        logging.info('Artifactory %s number of files: %s', from_repo_key, len(artifactory_files))

        nexus_files = get_nexus_files(cfg.nexus_spec, to_repo_key)
        logging.debug('Nexus %s files: %s', to_repo_key, nexus_files)
        logging.info('Nexus %s number of files: %s', to_repo_key, len(nexus_files))

        artifactory_complement = get_complement(artifactory_files, nexus_files)
        logging.debug('Files only in Artifactory %s: %s', from_repo_key, artifactory_complement)
        logging.info('Number of files only in Artifactory %s: %s', from_repo_key, len(artifactory_complement))

        if cfg.dry:
            logging.info("Configured to run dry so not performing migration")
        else:
            failure_count, success_count = migrate(artifactory_complement, cfg.work_dir, from_repo_key, to_repo_key,
                                                   cfg.artifactory_spec, cfg.nexus_spec)
            logging.info('%s -> %s, Success: %s, Failure: %s', from_repo_key, to_repo_key, success_count, failure_count)


if __name__ == '__main__':
    main(config)
