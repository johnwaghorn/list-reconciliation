# LR-15 generates consolidated csv file with the respective GP Practice comparision records

* setup: empty table "demographics_table"
* setup: empty table "demographics_differences_table"
* setup: empty table "in_flight_table"
* setup: empty bucket "lr_01_bucket"
* setup: empty bucket "lr_13_bucket"
* setup: empty bucket "lr_22_bucket"

## Consolidated Demographic Differences file is empty when comparison is not completed

* upload gpfile file "lr_15/emptycdd/A82023_GPR4LNA1.EIA" to LR-01
* wait for "15" seconds to allow other jobs to process
* execute step function lr-10 and assert status succeeded
* ensure produced "CDD" file contains the expected consolidated records as in "lr_13/expected_empty_cdd_file.txt"
