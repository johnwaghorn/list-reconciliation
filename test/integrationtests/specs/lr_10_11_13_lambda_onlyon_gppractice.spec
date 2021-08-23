# LR-10 state function registration differences and LR-11 to produce GP only data

* setup steps to empty all buckets
* setup steps to empty all database tables

## Ensure that when the nhs_number and gp_code matches with the pds record then empty onlyonGP file should be produced

* setup step: upload MESH data "lr_11/dps_data.csv" on LR-20 and check output in LR-22 for expected file "Y12345.csv"
* connect to s3 and upload gpfile file "lr_11/Y12345_GPR4LNA1.EIA" for successful file validation
* wait for "15" seconds to allow other jobs to process
* execute step function lr-10 and assert status succeeded
* ensure produced "OnlyOnGP" file contains the expected consolidated records as in "lr_11/expected_empty_gponly_file.txt"
