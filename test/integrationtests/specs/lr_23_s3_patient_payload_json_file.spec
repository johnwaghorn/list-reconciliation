# Tests for payload json files produced per patient in LR-23 bucket

tags: wip

* setup steps: clear all files in LR_01 bucket folders and dynamodb Inflight table
* setup steps: clear all files in mock pds data and lr_22 buckets
* setup steps: clear all files lr_23 bucket

## test to ensure individual payload json file is produced sucessfully

* upload mock pds data in "LR_15" to S3
* upload test data files in "LR_15" to lr-22
* connect to s3 and upload gpfile file "A82023_GPR4LNA1.EIA" for successful file validation
* connect and trigger lr-10 state function for registration differences and assert status succeeded
* connect to "LR_23/" s3 bucket and ensure patient payload record file with patientid "8000000008" is generated as expected "8000000008.json"
* connect to "LR_23/" s3 bucket and ensure patient payload record file with patientid "9000000009" is generated as expected "9000000009.json"
