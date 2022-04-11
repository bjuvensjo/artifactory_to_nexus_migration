# Artifactory to Artifactory migration

This script is used to migrate/copy artifacts from repositories of one Artifactory instance to repositories of another
Artifactory instance.

The script copies only latest files, i.e. if multiple versions of SNAPSHOT, only the SNAPSHOT with the latest timestamp
will be copied.

Additionally, it supports filter methods, see config.py, to filter out artifacts.

The script uses REST services of Artifactory to retrieve the content of the repositories. The response of those services
include all files and the sha1 of these files. The sha1 is used to decide if a file should be copied. Thus, if the
script is executed repeatedly, it will only copy files not previously copied.

The copy is done by downloading and uploading each included file. The file is downloaded to the configured work_dir.
After uploading the file is deleted.

The script supports running dry, i.e. only log information about what needs to be migrated without actually downloading
and uploading anything.

## Usage

### Update config.py

    * from_artifactory_spec
    * to_artifactory_spec
    * repositories
    * filters

### Execute main.py

    ./main.py

