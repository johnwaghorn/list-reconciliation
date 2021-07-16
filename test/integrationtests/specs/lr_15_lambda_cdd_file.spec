# Tests for LR-15 to generate consolidated csv file with the respective gppractive comparision records 
-------------------------------------------------------------------------------------------------------
* setup steps: clear all files in LR_01 bucket folders and dynamodb Inflight table
* setup steps: clear all files in mock pds data and lr_22 buckets

## test to ensure consolidated demographic differences file is generated succesfully
------------------------------------------------------------------------------------

* prep step : connect to s3 buckets mock pds, lr-22 and upload data files for "LR_15/" lambda
* connect to s3 and upload gpfile file "A82023_GPR4LNA1.EIA" for successful file validation
* connect and trigger lr-10 state function for registration differences and assert status succeeded
* connect to "LR_13/" s3 bucket and ensure "-CDD-" produced contains the expected consolidated records as in "expected_cdd_file.txt"
 

## test to ensure empty consolidated demographic differences file is generated succesfully when comparision is not completed
----------------------------------------------------------------------------------------------------------------------------
* prep step : connect to s3 buckets mock pds, lr-22 and upload data files for "LR_15/emptycdd/" lambda
* connect to s3 and upload gpfile file "A82023_GPR4LNA1.EIA" for successful file validation
* connect and trigger lr-10 state function for registration differences and assert status succeeded
* connect to "LR_13/" s3 bucket and ensure "-CDD-" produced contains the expected consolidated records as in "expected_empty_cdd_file.txt"