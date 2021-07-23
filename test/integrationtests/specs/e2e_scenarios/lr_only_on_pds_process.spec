# Test OnlyOnPDS.csv process
----------------------------
Tags : wip

## Test to ensure if any outstanding records that are on PDS API data but are not on GP flat file can be added to OnlyOnPDS.csv output file
* setup step: connect to s3 buckets LR-20 and upload MESH data
* setup step: connect to s3 bucket mock pds api and upload csv file that contains the missing records
* upload a GP flat file that has missing PDS data
* connect to lr-03 dynamodb and get the latest JobId for a gppractice file
* trigger lr09 and ensure scheduled checked successfully completed
* connect to lr-13 and check for latest output csv file for OnlyOnPDS

## Test to ensure that if the MESH data is late in the process OnlyOnPDS.csv is created successfully after a GP flat file has been processed again and MESH has been split
* setup step: connect to s3 bucket mock pds api and upload csv file that contains the missing records
* upload a GP flat file that has missing PDS data
* connect to lr-03 dynamodb and get the latest JobId for a gppractice file
* trigger lr09 and ensure scheduled checked successfully completed
* check LR-13 does not contain OnlyOnPDS data
* setup step: connect to s3 buckets LR-20 and upload MESH data
* get InFlight table item count
* upload a GP flat file that has missing PDS data
* connect to lr-03 dynamodb and get the latest JobId for a gppractice file
* trigger lr09 and ensure scheduled checked successfully completed
* connect to lr-13 and check for latest output csv file for OnlyOnPDS

____________________________
Teardown S3 bucket data
* delete all csv files in LR13
* delete all s3 files in LR22
