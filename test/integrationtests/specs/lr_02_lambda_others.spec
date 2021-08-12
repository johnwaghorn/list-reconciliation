# Scenarios for LR-02 lambda to validate and parse the GP file
--------------------------------------------------------------


## test to ensure when lambda LR-02 is triggered and check file is validated and passed sucessfully
---------------------------------------------------------------------------------------------------
* setup steps to empty all buckets
* setup steps to empty all database tables
* connect to s3 and upload gpfile file "LR_02/A82023_GPR4LNA1.EIA" for successful file validation
* connect to pass folder and check if it has loaded the test file


## test to ensure when lambda LR-02 is triggered and response status code 202 is recieved
------------------------------------------------------------------------------------------
* trigger lambda LR-02 and assert response status code is "202"
* trigger lambda LR-02  and assert responsemetadata HTTPStatusCode response is "202"

## test to ensure when lambda LR-02 is triggered with invalid payload should throw key error
--------------------------------------------------------------------------------------------
* connect and trigger lambda LR-02 with invalid payload
