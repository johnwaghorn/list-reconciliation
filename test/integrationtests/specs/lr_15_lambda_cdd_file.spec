# LR-15 generates consolidated csv file with the respective GP Practice comparision records

* setup: empty table "demographic_table"
* setup: empty table "demographics_difference_table"
* setup: empty table "in_flight_table"
* setup: empty bucket "lr_01_bucket"
* setup: empty bucket "lr_13_bucket"
* setup: empty bucket "lr_22_bucket"
* setup: empty bucket "mock_pds_data"

## Consolidated Demographic Differences file is generated succesfully when comparison is complete

* upload mock pds data in "LR_15" to S3
* upload test data files in "LR_15" to lr-22
* upload gpfile file "A82023_GPR4LNA1.EIA" to LR-01
* wait for "15" seconds to allow other jobs to process
* execute step function lr-10 and assert status succeeded
* ensure produced CDD file contains the expected consolidated records as in "expected_cdd_file.txt"

## Consolidated Demographic Differences file is empty when comparison is not completed

* upload mock pds data in "LR_15/emptycdd" to S3
* upload gpfile file "A82023_GPR4LNA1.EIA" to LR-01
* wait for "15" seconds to allow other jobs to process
* execute step function lr-10 and assert status succeeded
* ensure produced CDD file contains the expected consolidated records as in "expected_empty_cdd_file.txt"
