# Test on LR-12 Lambda & LR-13 bucket for PDS not on practice file
------------------------------------------------------------------

* setup: empty table "jobs_table"
* setup: empty bucket "lr_22_bucket"
* setup: empty bucket "lr_13_bucket"

## test to ensure the data on mismatch records on onlyonPDS csv file in the output bucket is as expected
--------------------------------------------------------------------------------------------------------
* setup step: upload MESH data "OnlyOnPDS/dps_data.csv" on LR-20 and check output in LR-22 for expected file "Y12345.csv"
* upload gpfile file "LR_13/Y12345_GPR4LNA1.EIA" to LR-01
* wait for "15" seconds to allow other jobs to process
* execute step function lr-10 and assert status succeeded
* ensure produced "OnlyOnPDS" file contains the expected consolidated records as in "LR_13/expected_onlyonPDS.txt"
