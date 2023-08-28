# Artifactory to Nexus migration

This script is used to migrate/copy artifacts from Artifactory repositories to Nexus 3 repositories.

The script copies only latest files, i.e. if Artifactory stores multiple versions of SNAPSHOT, 
only the SNAPSHOT with the latest timestamp will be copied to Nexus.

Additionaly, it supports filter methods, see config.py, to filter out artifacts. 

The script uses REST services of Artifactory and Nexus to retrieve the content of the repositories.
The response of those services include all files and the sha1 of these files. The sha1 is used to 
decide if a file should be copied. Thus, if the script is executed repeatedly, it will only copy 
files not previously copied. Unfortunately, the Nexus 3 REST Api for retrieving content is slow. 
The script will therefore take quite long time for Nexus repositories with a lot of content.  

The copy is done by downloading from Artifactory and uploading to Nexus. The file is downloaded to
the configured work_dir. After uploading the file is deleted.

Downloading and uploading is done sequentially. The script could rather easily be modified to do 
it concurrently. 

The script supports running dry, i.e. only log information about what needs to be migrated without 
actually downloading and uploading anything.

## Usage

### Update config.py

    * artifactory_spec
    * nexus_spec
    * repositories
    * filters
    
### Execute main.py

Use Poetry 

* to create virtual environment and install dependencies
* to activate the virtual environment

Within the activated virtual environment, execute

    python main.py

