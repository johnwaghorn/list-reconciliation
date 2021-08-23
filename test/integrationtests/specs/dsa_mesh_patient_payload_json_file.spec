# Payload json files produced per patient in MESH OUTBOUND_INTERNALSPINE

* setup steps to empty all buckets
* setup steps to empty all database tables

## Ensure individual payload json file is produced sucessfully

* setup step: upload MESH data "OnlyOnPDS/dps_data.csv" on LR-20 and check output in LR-22 for expected file "Y12345.csv"
* upload test data files in "lr_15" to lr-22
* upload gpfile file "lr_13/Y12345_GPR4LNA1.EIA" to LR-01
* wait for "15" seconds to allow other jobs to process
* execute step function lr-10 and assert status succeeded
* connect to "lr_23/" s3 bucket and ensure patient payload record file with patientid "9000000017" is generated as expected "9000000017.json"
* connect to "lr_23/" s3 bucket and ensure patient payload record file with patientid "9000000025" is generated as expected "9000000025.json"
