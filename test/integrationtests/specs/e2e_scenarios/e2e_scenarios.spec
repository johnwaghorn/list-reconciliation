# ListRecon_E2E Scenarios
-------------------------
* setup steps to empty all buckets
* setup steps to empty all database tables

## test to ensure that gponly, pdsonly, cdd files and MESH DSA payload are produced as expected
-----------------------------------------------------------------------------------------------
* setup step: upload MESH data "OnlyOnPDS/dps_data.csv" on LR-20 and check output in LR-22 for expected file "Y12345.csv"
* connect to s3 and upload gpfile file "LR_13/Y12345_GPR4LNA1.EIA" for successful file validation
* connect to lr-03 dynamodb and get the latest JobId for a gppractice file
* check expected sensitivity as "U" on demographics table for nhsnumber "9000000017"
* check expected sensitivity as "R" on demographics table for nhsnumber "9000000025"
* trigger lr09 and ensure scheduled checked successfully completed
* ensure the status of the LR-10 has succeeded for the respective jobid
* ensure produced "OnlyOnGP" file contains the expected consolidated records as in "LR_13/expected_onlyongp.txt"
* ensure produced "OnlyOnPDS" file contains the expected consolidated records as in "LR_13/expected_onlyonPDS.txt"
* ensure produced "CDD" file contains the expected consolidated records as in "LR_13/expected_cdd_file.txt"
* connect to "LR_23/" s3 bucket and ensure patient payload record file with patientid "9000000017" is generated as expected "9000000017.json"
* connect to "LR_23/" s3 bucket and ensure patient payload record file with patientid "9000000025" is generated as expected "9000000025.json"


## test to ensure the data on mismatch records on onlyongp csv file  in the output bucket is as expected
--------------------------------------------------------------------------------------------------------
* setup step: upload MESH data "OnlyOnPDS/dps_data.csv" on LR-20 and check output in LR-22 for expected file "Y12345.csv"
* connect to s3 and upload gpfile file "LR_13/Y12345_GPR4LNA1.EIA" for successful file validation
* connect to lr-03 dynamodb and get the latest JobId for a gppractice file
* check expected sensitivity as "U" on demographics table for nhsnumber "9000000017"
* check expected sensitivity as "R" on demographics table for nhsnumber "9000000025"
* trigger lr09 and ensure scheduled checked successfully completed
* ensure the status of the LR-10 has succeeded for the respective jobid
* ensure produced "OnlyOnGP" file contains the expected consolidated records as in "LR_13/expected_onlyongp.txt"


## test to ensure the data on mismatch records on onlyonPDS csv file in the output bucket is as expected
--------------------------------------------------------------------------------------------------------
* setup step: upload MESH data "OnlyOnPDS/dps_data.csv" on LR-20 and check output in LR-22 for expected file "Y12345.csv"
* upload gpfile file "LR_13/Y12345_GPR4LNA1.EIA" to LR-01
* wait for "15" seconds to allow other jobs to process
* execute step function lr-10 and assert status succeeded
* ensure produced "OnlyOnPDS" file contains the expected consolidated records as in "LR_13/expected_onlyonPDS.txt"


## Consolidated Demographic Differences file is generated succesfully when comparison is complete
* setup step: upload MESH data "OnlyOnPDS/dps_data.csv" on LR-20 and check output in LR-22 for expected file "Y12345.csv"
* upload test data files in "LR_15" to lr-22
* upload gpfile file "LR_13/Y12345_GPR4LNA1.EIA" to LR-01
* wait for "15" seconds to allow other jobs to process
* execute step function lr-10 and assert status succeeded
* ensure produced "CDD" file contains the expected consolidated records as in "LR_13/expected_cdd_file.txt"


## test to ensure expected comparision is done for the non sensitive patient matching the PDS record
-----------------------------------------------------------------------------------------------------
* upload gpfile file "LR_07/Y12345_GPR4LNA1.EIA" to LR-01
* upload test data file "Y12345.csv" in "LR_07" to lr-22
* check expected sensitivity as "U" on demographics table for nhsnumber "9000000017"
* check demographic difference "MN-BR-DB-01" on demographics difference table for nhsnumber "9000000017"
* check demographic difference "MN-BR-AD-02" on demographics difference table for nhsnumber "9000000017"
* check demographic difference "MN-BR-FN-01" on demographics difference table for nhsnumber "9000000017"
* check demographic difference "MN-BR-SN-01" on demographics difference table for nhsnumber "9000000017"
* check demographic difference "MN-BR-AD-01" on demographics difference table for nhsnumber "9000000017"
* check demographic difference "MN-BR-TL-01" on demographics difference table for nhsnumber "9000000017"


## test to ensure individual payload json file is produced sucessfully
* setup step: upload MESH data "OnlyOnPDS/dps_data.csv" on LR-20 and check output in LR-22 for expected file "Y12345.csv"
* upload test data files in "LR_15" to lr-22
* upload gpfile file "LR_13/Y12345_GPR4LNA1.EIA" to LR-01
* wait for "15" seconds to allow other jobs to process
* execute step function lr-10 and assert status succeeded
* connect to "LR_23/" s3 bucket and ensure patient payload record file with patientid "9000000017" is generated as expected "9000000017.json"
* connect to "LR_23/" s3 bucket and ensure patient payload record file with patientid "9000000025" is generated as expected "9000000025.json"
