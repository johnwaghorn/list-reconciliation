# Tests for LR-10 state function registration differences and LR-11 to produce GP only data
--------------------------------------------------------------------------------------------
* setup steps: clear all files in bucket folders
* connect to s3 lr-22 bucket and upload pds data

## test to ensure the data on mismatch records on onlyongp csv file  in the output bucket is as expected
--------------------------------------------------------------------------------------------------------
* connect to s3 and upload gpfile file "GPR4LNA1.EIA" for successful file validation
* connect and trigger lr-10 state function for registration differences and assert status succeeded
* connect to s3 bucket and ensure the csv file produced contains the expected gponly record