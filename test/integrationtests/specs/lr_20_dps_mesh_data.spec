# DPS Mesh data related tests
-----------------------------
* setup: empty bucket "lr_20_bucket"
* setup: empty bucket "lr_22_bucket"

## test to ensure that dsa mesh data loaded on LR-20 is split correctly and loaded on the lr-22 by GP_Code Successfully
-----------------------------------------------------------------------------------------------------------------------
* setup step: upload MESH data "OnlyOnPDS/dps_data.csv" on LR-20 and check output in LR-22 for expected file "Y12345.csv"
