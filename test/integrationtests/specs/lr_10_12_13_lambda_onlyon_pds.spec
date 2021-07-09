# Test on LR-12 Lambda & LR-13 bucket for PDS not on practice file 
------------------------------------------------------------------
* connect to dynamodb and add records
* connect to s3 bucket LR-22 and mock pds and upload data files


## Lambda LR-12 can see mismatch information of PDS data for a record that is on PDS but not on practice
--------------------------------------------------------------------------------------------------------
* check lambda LR-12 has run
* connect to lr-13 and check output csv file content and file format as expected


## Test to ensure Step Functions LR-10 can receive a job id and trigger LR12 to produce an output file
------------------------------------------------------------------------------------------------------
* connect to step function LR-10 and pass in job id and return successful execution response
* connect to lr-13 and check output csv file content and file format as expected

____________________________
Teardown LR13 S3 bucket data

* delete all s3 files in LR13
