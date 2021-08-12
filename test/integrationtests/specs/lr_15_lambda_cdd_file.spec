# LR-15 generates consolidated csv file with the respective GP Practice comparision records

* setup steps to empty related tables and buckets for LR-15 tests

## Consolidated Demographic Differences file is empty when comparison is not completed

* upload gpfile file "LR_15/emptycdd/A82023_GPR4LNA1.EIA" to LR-01
* wait for "15" seconds to allow other jobs to process
* execute step function lr-10 and assert status succeeded
* ensure produced "CDD" file contains the expected consolidated records as in "expected_empty_cdd_file.txt"

## Consolidated Demographic Differences file is generated succesfully when comparison is complete
* setup step: upload MESH data on LR-20 and check output in LR-22 for expected file "Y12345.csv"
* upload test data files in "LR_15" to lr-22
* upload gpfile file "LR_13/Y12345_GPR4LNA1.EIA" to LR-01
* wait for "15" seconds to allow other jobs to process
* execute step function lr-10 and assert status succeeded
* ensure produced "CDD" file contains the expected consolidated records as in "expected_cdd_file.txt"
