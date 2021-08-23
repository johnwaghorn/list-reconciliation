# LR-07 LR-08 lambda for file comparision

* setup steps to empty all buckets
* setup steps to empty all database tables

## Ensure expected comparision is done for the non sensitive patient matching the PDS record

* upload gpfile file "lr_07/Y12345_GPR4LNA1.EIA" to LR-01
* upload test data file "Y12345.csv" in "lr_07" to lr-22
* check expected sensitivity as "U" on demographics table for nhsnumber "9000000017"
* check demographic difference "MN-BR-DB-01" on demographics difference table for nhsnumber "9000000017"
* check demographic difference "MN-BR-AD-02" on demographics difference table for nhsnumber "9000000017"
* check demographic difference "MN-BR-FN-01" on demographics difference table for nhsnumber "9000000017"
* check demographic difference "MN-BR-SN-01" on demographics difference table for nhsnumber "9000000017"
* check demographic difference "MN-BR-AD-01" on demographics difference table for nhsnumber "9000000017"
* check demographic difference "MN-BR-TL-01" on demographics difference table for nhsnumber "9000000017"

## Ensure sensitive patient records are processed as expectd

* upload gpfile file "lr_07/Y12345_GPR4LNA1.EIA" to LR-01
* upload test data file "Y12345.csv" in "lr_07" to lr-22
* check expected sensitivity as "R" on demographics table for nhsnumber "9000000025"
* execute step function lr-10 and assert status succeeded
* ensure produced "CDD" file contains the expected consolidated records as in "lr_13/sensitive/expected_cdd_file_sensitive.txt"

## Ensure when no pds record is not found on the PDS API the records are processed as expected

* upload gpfile file "lr_07/notfoundondata/Y12345_GPR4LNA1.EIA" to LR-01
* upload test data file "Y12345.csv" in "lr_07" to lr-22
check expected sensitivity as "null" on demographics table for nhsnumber "9111231130"
