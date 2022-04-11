#!/usr/bin/env python3
import logging
from os import makedirs, remove
from os.path import dirname
from time import time

import config
from artifactory import get_latest_repo_files as get_artifactory_files, download, upload
from util import get_complement, pmap_unordered


def get_repo_keys(repo_key):
    if type(repo_key) is str:
        return repo_key, repo_key
    return repo_key


def migrate(artifactory_complement, work_dir, from_repo_key, to_repo_key, from_artifactory_spec, to_artifactory_spec):
    success_count = 0
    failure_count = 0
    total_count = len(artifactory_complement)

    def migrate_file(path_and_asset):
        file_path, file_asset = path_and_asset
        result = False
        try:
            output_file = f'{work_dir}/{file_path}'
            makedirs(dirname(output_file), exist_ok=True)
            download(output_file, from_artifactory_spec, from_repo_key, file_asset['uri'], file_asset['sha1'])
            upload(output_file, to_artifactory_spec, to_repo_key, file_path)
            remove(output_file)
            result = True
        except OSError as e:
            logging.exception('Can not migrate: %s', file_asset)
        return file_path, file_asset, result

    # The two following lines can replace the following line (the one with "pmap_unordered") to run in only one thread
    # for path, asset in artifactory_complement.items():
    #     _, _, success = migrate_file([path, asset])

    for path, asset, success in pmap_unordered(migrate_file, artifactory_complement.items(), processes=5):
        if success:
            success_count += 1
        else:
            failure_count += 1
        logging.info('%s of %s', success_count + failure_count, total_count)
    return failure_count, success_count


def filter_repo_files(repo_files, filters=[]):
    for f in filters:
        filtered_repo_files = f(repo_files)
        filtered_out = set(repo_files) - set(filtered_repo_files)
        logging.info('%s filtered out %s', f.__name__, len(filtered_out))
        logging.debug('%s filtered out %s', f.__name__, filtered_out)
        repo_files = filtered_repo_files
    return repo_files


def main(cfg):
    for repo_key in cfg.repositories:
        start = time()
        from_repo_key, to_repo_key = get_repo_keys(repo_key)
        logging.info('From repo key: %s, To repo key: %s', from_repo_key, to_repo_key)

        from_artifactory_files = get_artifactory_files(cfg.from_artifactory_spec, from_repo_key)
        logging.debug('From Artifactory %s files: %s', from_repo_key, from_artifactory_files)
        logging.info('From Artifactory %s number of files: %s', from_repo_key, len(from_artifactory_files))

        filtered_from_artifactory_files = filter_repo_files(from_artifactory_files, cfg.filters)
        logging.debug('Filtered from Artifactory %s files: %s', from_repo_key, filtered_from_artifactory_files)
        logging.info('Artifactory %s number of files after filters: %s', from_repo_key,
                     len(filtered_from_artifactory_files))

        to_artifactory_files = get_artifactory_files(cfg.to_artifactory_spec, to_repo_key)
        logging.debug('To Artifactory  %s files: %s', to_repo_key, to_artifactory_files)
        logging.info('To Artifactory %s number of files: %s', to_repo_key, len(to_artifactory_files))

        artifactory_complement = get_complement(filtered_from_artifactory_files, to_artifactory_files)
        logging.debug('Files only in From Artifactory %s: %s', from_repo_key, artifactory_complement)
        logging.info('Number of files only in From Artifactory %s: %s', from_repo_key, len(artifactory_complement))

        if cfg.dry:
            logging.info('Configured to run dry so not performing migration')
        else:
            failure_count, success_count = migrate(artifactory_complement, cfg.work_dir, from_repo_key, to_repo_key,
                                                   cfg.from_artifactory_spec, cfg.to_artifactory_spec)
            logging.info('%s -> %s, Success: %s, Failure: %s', from_repo_key, to_repo_key, success_count, failure_count)

        end = time()
        logging.info('%s migration time: %s s', repo_key, time() - start)


if __name__ == '__main__':
    main(config)
