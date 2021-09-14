#!/usr/bin/env python3
import datetime
import logging
import re
from os.path import basename, dirname, exists

from requests import get

from util import get_checksums, read_file


def get_repo_content(artifactory_spec, repo_key):
    url = f'{artifactory_spec["url"]}/api/storage/{repo_key}?list&deep=1&listFolders=1'
    response = get(url, auth=(artifactory_spec['username'], artifactory_spec['password']))
    if response.status_code != 200:
        raise OSError(f'{response.status_code}, {response.content}')
    return response.json()


def get_date_time(file_name):
    time_stamp = re.search(r'[0-9]{8}.[0-9]+-[0-9]+', file_name)
    return datetime.datetime.strptime(time_stamp.group(0), '%Y%m%d.%H%M%S-%f')


def is_later(current, candidate):
    result = get_date_time(candidate) > get_date_time(current)
    logging.debug('%s: %s > %s', result, candidate, current)
    return result


def get_latest_repo_files(artifactory_spec, repo_key, excluded_uri_patterns=(r'.*maven-metadata.xml',)):
    file_content = [m for m in get_repo_content(artifactory_spec, repo_key)['files'] if not m['folder']]
    latest_dict = {}
    for m in file_content:
        group_artifact_version = dirname(m['uri'])
        file_name = basename(m['uri'])
        normalized_file_name = re.sub(r'-[0-9]{8}.[0-9]+-[0-9]+', '-SNAPSHOT', file_name)
        if not any([re.fullmatch(p, normalized_file_name) for p in excluded_uri_patterns]):
            key = '/'.join([group_artifact_version, normalized_file_name])[1:]
            if key in latest_dict:
                if is_later(basename(latest_dict[key]['uri']), file_name):
                    logging.debug('Excluding %s for %s', latest_dict[key]['uri'], file_name)
                    latest_dict[key] = m
            else:
                latest_dict[key] = m
    return latest_dict


def sha1sum(file_path):
    return get_checksums(read_file(file_path))[1]


def download(output_file, artifactory_spec, repo_key, repo_path, sha1):
    if exists(output_file) and sha1sum(output_file) == sha1:
        return
    url = f'{artifactory_spec["url"]}/{repo_key}/{repo_path}'
    logging.info('Downloading %s to %s', url, output_file)
    with open(output_file, 'wb') as f:
        response = get(url, auth=(artifactory_spec['username'], artifactory_spec['password']))
        if response.status_code != 200:
            raise OSError(f'{response.status_code}, {response.content}')
        f.write(response.content)
