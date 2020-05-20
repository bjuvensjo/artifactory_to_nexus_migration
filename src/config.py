work_dir = './work_dir'

artifactory_spec = {
    'url': '<artifactory_url, e.g. http://artifactory_host:9001>',
    'username': '<username>',
    'password': '<password>'
}

nexus_spec = {
    'url': '<nexus url, e.g. http://nexus_host:9002>',
    'username': '<username>',
    'password': '<password>'
}

# Specify a pair (tuple) if the repo key to mirror to is not the same as the repo key to mirror from
repositories = [
    ('from_repo_key', 'to_repo_key'),
    'from_and_to_repo_key',
]
