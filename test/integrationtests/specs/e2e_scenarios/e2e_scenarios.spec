# ListRecon_E2E Scenarios
-------------------------
* setup: empty bucket "lr_22_bucket"
## test to ensure that gponly, pdsonly and cdd files are produced as expected
-----------------------------------------------------------------------------
* setup step: upload MESH data on LR-20 and check output in LR-22 for expected file "Y12345.csv"
* connect to s3 and upload gpfile file "LR_13/Y12345_GPR4LNA1.EIA" for successful file validation
* wait for "15" seconds to allow other jobs to process
* execute step function lr-10 and assert status succeeded
* ensure produced "OnlyOnGP" file contains the expected consolidated records as in "expected_onlyongp.txt"
* ensure produced "OnlyOnPDS" file contains the expected consolidated records as in "expected_onlyonPDS.txt"
* ensure produced "CDD" file contains the expected consolidated records as in "expected_cdd_file.txt"