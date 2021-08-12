# Tests for LR-10 state function registration differences and LR-11 to produce GP only data
--------------------------------------------------------------------------------------------
* setup steps to empty all buckets
* setup steps to empty all database tables

## test to ensure the data on mismatch records on onlyongp csv file  in the output bucket is as expected
--------------------------------------------------------------------------------------------------------
* setup step: upload MESH data on LR-20 and check output in LR-22 for expected file "Y12345.csv"
* connect to s3 and upload gpfile file "LR_13/Y12345_GPR4LNA1.EIA" for successful file validation
* wait for "15" seconds to allow other jobs to process
* execute step function lr-10 and assert status succeeded
* ensure produced "OnlyOnGP" file contains the expected consolidated records as in "expected_onlyongp.txt"