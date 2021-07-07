# Scenarios for LR-02 lambda to validate and parse the GP file
--------------------------------------------------------------


## test to ensure when lambda LR-02 is triggered and check cloud watch log for positive scenario
------------------------------------------------------------------------------------------------
* connect to s3 and upload gpfile file "GPR4LNA1.EIA" for successful file validation
* connect to cloudwatch log and get the request id by JobId created

## test to ensure when lambda LR-02 is triggered and response status code 202 is recieved
------------------------------------------------------------------------------------------
* trigger lambda LR-02 and assert response status code is "202"
* trigger lambda LR-02  and assert responsemetadata HTTPStatusCode response is "202"

## test to ensure when lambda LR-02 is triggered with invalid payload should throw key error 
--------------------------------------------------------------------------------------------
* connect and trigger lambda LR-02 with invalid payload

## test to validate invalid record type
---------------------------------------
* connect to s3 and upload gp file with invalid item "DOWNLOAD" in row "DOW~1" at position "0"
* connect to s3 failed folder and assert failure message "Row 1 for all records must start with 'DOW~1'"