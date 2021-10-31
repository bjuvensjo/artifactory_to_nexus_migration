#!/usr/bin/env python3

from version import get_latest_snapshot, get_latest_rc, get_latest_fixed


def not_index(repo_files):
    return {k: v for k, v in repo_files.items() if not k.endswith('.index')}


def not_maven_metadata(repo_files):
    return {k: v for k, v in repo_files.items() if not k.endswith('maven-metadata.xml')}


def not_tar(repo_files):
    return {k: v for k, v in repo_files.items() if not k.endswith('.tar')}


def not_war(repo_files):
    return {k: v for k, v in repo_files.items() if not k.endswith('.war')}


def not_zip(repo_files):
    return {k: v for k, v in repo_files.items() if not k.endswith('.zip')}


def latest_version(repo_files):
    version_map = {}
    for f in repo_files:
        group_and_artifact_id = '/'.join(f.split('/')[:-2])
        version = f.split('/')[-2]
        if group_and_artifact_id not in version_map:
            version_map[group_and_artifact_id] = []
        version_map[group_and_artifact_id].append(version)

    latest_version_map = {}
    for k, v in version_map.items():
        try:
            latest_versions = [get_latest_snapshot(v), get_latest_rc(v), get_latest_fixed(v)]
            flat_latest_versions = [item for sublist in latest_versions for item in sublist if item]
            # latest_version_map[k] = [get_latest_snapshot(v), get_latest_rc(v), get_latest_fixed(v)]
            latest_version_map[k] = flat_latest_versions
        except ValueError:
            latest_version_map[k] = v

    latest_repo_files = {}
    for uri, repo_file in repo_files.items():
        group_and_artifact_id = '/'.join(uri.split('/')[:-2])
        version = uri.split('/')[-2]
        # latest_version_map may contain list for not semver versions, thus the or below
        current_versions = latest_version_map[group_and_artifact_id]
        if version in latest_version_map[group_and_artifact_id]:
            latest_repo_files[uri] = repo_file

    return latest_repo_files
