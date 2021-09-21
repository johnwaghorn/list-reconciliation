# List Reconciliation E2E PreProd Scenarios

tags: preprod, disabled

* Empty all buckets
* Empty all database tables

## Ensure that gponly, pdsonly, cdd files and MESH DSA payload are produced as expected

* setup step: upload PDS supplementary data "OnlyOnPDS/dps_data.csv" to LR-20 and check output in LR-22 for expected file "H81109.csv"
* connect to s3 and upload gpfile file "lr_13/H81109_GPR4LNA1.EIA" for successful file validation
* connect to lr-03 dynamodb and get the latest JobId for a gppractice file
* wait for "15" seconds to allow other jobs to process
* check expected sensitivity as "U" on demographics table for nhsnumber "9449306621"
* check expected sensitivity as "U" on demographics table for nhsnumber "9449305552"
* trigger lr09 and ensure scheduled checked successfully completed
* ensure the status of the LR-10 has succeeded for the respective jobid
* ensure produced "OnlyOnGP" file contains the expected consolidated records as in "lr_13/expected_onlyongp.txt"
* ensure produced "OnlyOnPDS" file contains the expected consolidated records as in "lr_13/expected_onlyonPDS.txt"
* ensure produced "CDD" file contains the expected consolidated records as in "lr_13/expected_cdd_file.txt"
* connect to MESH bucket and ensure patient payload record file with patientid "9449306621" is generated as expected "9449306621.json"
* connect to MESH bucket and ensure patient payload record file with patientid "9449305552" is generated as expected "9449305552.json"

## Ensure the data on mismatch records on onlyongp csv file  in the output bucket is as expected

* setup step: upload PDS supplementary data "OnlyOnPDS/dps_data.csv" to LR-20 and check output in LR-22 for expected file "H81109.csv"
* connect to s3 and upload gpfile file "lr_13/H81109_GPR4LNA1.EIA" for successful file validation
* connect to lr-03 dynamodb and get the latest JobId for a gppractice file
* wait for "15" seconds to allow other jobs to process
* check expected sensitivity as "U" on demographics table for nhsnumber "9449306621"
* check expected sensitivity as "U" on demographics table for nhsnumber "9449305552"
* trigger lr09 and ensure scheduled checked successfully completed
* ensure the status of the LR-10 has succeeded for the respective jobid
* ensure produced "OnlyOnGP" file contains the expected consolidated records as in "lr_13/expected_onlyongp.txt"

## Ensure the data on mismatch records on onlyonPDS csv file in the output bucket is as expected

* setup step: upload PDS supplementary data "OnlyOnPDS/dps_data.csv" to LR-20 and check output in LR-22 for expected file "H81109.csv"
* connect to s3 and upload gpfile file "lr_13/H81109_GPR4LNA1.EIA" for successful file validation
* connect to lr-03 dynamodb and get the latest JobId for a gppractice file
* wait for "15" seconds to allow other jobs to process
* check expected sensitivity as "U" on demographics table for nhsnumber "9449306621"
* check expected sensitivity as "U" on demographics table for nhsnumber "9449305552"
* trigger lr09 and ensure scheduled checked successfully completed
* ensure the status of the LR-10 has succeeded for the respective jobid
* ensure produced "OnlyOnPDS" file contains the expected consolidated records as in "lr_13/expected_onlyonPDS.txt"

## Consolidated Demographic Differences file is generated succesfully when comparison is complete

* setup step: upload PDS supplementary data "OnlyOnPDS/dps_data.csv" to LR-20 and check output in LR-22 for expected file "H81109.csv"
* connect to s3 and upload gpfile file "lr_13/H81109_GPR4LNA1.EIA" for successful file validation
* connect to lr-03 dynamodb and get the latest JobId for a gppractice file
* wait for "15" seconds to allow other jobs to process
* check expected sensitivity as "U" on demographics table for nhsnumber "9449306621"
* check expected sensitivity as "U" on demographics table for nhsnumber "9449305552"
* trigger lr09 and ensure scheduled checked successfully completed
* ensure the status of the LR-10 has succeeded for the respective jobid
* ensure produced "CDD" file contains the expected consolidated records as in "lr_13/expected_cdd_file.txt"

## Ensure expected comparision is done for the non sensitive patient matching the PDS record

* setup step: upload PDS supplementary data "OnlyOnPDS/dps_data.csv" to LR-20 and check output in LR-22 for expected file "H81109.csv"
* connect to s3 and upload gpfile file "lr_13/H81109_GPR4LNA1.EIA" for successful file validation
* wait for "15" seconds to allow other jobs to process
* check expected sensitivity as "U" on demographics table for nhsnumber "9449306621"
* check demographic difference "MN-BR-DB-01" on demographics difference table for nhsnumber "9449306621"
* check demographic difference "MN-BR-AD-02" on demographics difference table for nhsnumber "9449306621"
* check demographic difference "MN-BR-FN-01" on demographics difference table for nhsnumber "9449306621"
* check demographic difference "MN-BR-SN-01" on demographics difference table for nhsnumber "9449306621"
* check demographic difference "MN-BR-AD-01" on demographics difference table for nhsnumber "9449306621"
* check demographic difference "MN-BR-TL-01" on demographics difference table for nhsnumber "9449306621"

## Ensure individual payload json file is produced sucessfully

* setup step: upload PDS supplementary data "OnlyOnPDS/dps_data.csv" to LR-20 and check output in LR-22 for expected file "H81109.csv"
* connect to s3 and upload gpfile file "lr_13/H81109_GPR4LNA1.EIA" for successful file validation
* connect to lr-03 dynamodb and get the latest JobId for a gppractice file
* wait for "15" seconds to allow other jobs to process
* check expected sensitivity as "U" on demographics table for nhsnumber "9449306621"
* check expected sensitivity as "U" on demographics table for nhsnumber "9449305552"
* trigger lr09 and ensure scheduled checked successfully completed
* ensure the status of the LR-10 has succeeded for the respective jobid
* connect to MESH bucket and ensure patient payload record file with patientid "9449306621" is generated as expected "9449306621.json"
* connect to MESH bucket and ensure patient payload record file with patientid "9449305552" is generated as expected "9449305552.json"
