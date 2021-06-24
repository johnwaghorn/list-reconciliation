# Positive Scenarios for LR-02 lambda to validate and parse the GP file
----------------------------------------------------------------------

## test to ensure when lambda LR-02 is triggered and check cloud watch log for positive scenario
------------------------------------------------------------------------------------------------
* connect to s3 and upload file "GPR4LNA1.EIA" into inbound folder for LR-02 to pick and validate the file
* connect to cloudwatch log and get the request id by JobId created