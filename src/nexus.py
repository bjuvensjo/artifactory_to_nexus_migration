#!/usr/bin/env python3
import logging

from requests import put, get

from util import read_file


def get_assets_page(nexus_spec, repository, continuation_token=None):
    token_param = f'&continuationToken={continuation_token}' if continuation_token else ''
    url = f'{nexus_spec["url"]}/service/rest/v1/assets?repository={repository}{token_param}'
    response = get(url, auth=(nexus_spec['username'], nexus_spec['password']))
    if response.status_code != 200:
        raise OSError(f'{response.status_code}, {response.content}')
    return response.json()


def get_assets(nexus_spec, repository):
    assets_page = get_assets_page(nexus_spec, repository)
    continuation_token = assets_page['continuationToken']
    items = assets_page['items']
    while continuation_token:
        assets_page = get_assets_page(nexus_spec, repository, continuation_token)
        continuation_token = assets_page['continuationToken']
        items += assets_page['items']
    return items


def get_latest_repo_files(nexus_spec, repo_key):
    return {a['path']: a for a in get_assets(nexus_spec, repo_key)}


def get_publish_data(artifact_base_uri, path, name):
    content = read_file(path)
    return {
        'content': content,
        'uri': f'{artifact_base_uri}/{name}'
    }


def upload(file_path, nexus_spec, repo_key, repo_path):
    url = f'{nexus_spec["url"]}/repository/{repo_key}/{repo_path}'
    logging.info('Uploading %s to %s', file_path, url)
    data = read_file(file_path)
    headers = {'Content-Type': 'application/octet-stream'}
    response = put(url, data=data, headers=headers, auth=(nexus_spec['username'], nexus_spec['password']))
    if response.status_code != 201:
        raise OSError(f'{response.status_code}, {response.content}')
