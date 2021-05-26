# Tests for LR-02 lambda to validate and parse the GP file
----------------------------------------------------------


## test to ensure when lambda LR-02 is triggered and response status code 202 is recieved
------------------------------------------------------------------------------------------
* trigger lambda LR-02 and assert response status code is "202"
* trigger lambda LR-02  and assert responsemetadata HTTPStatusCode response is "202"

## test to ensure when lambda LR-02 is triggered with invalid payload should throw key error 
--------------------------------------------------------------------------------------------
* connect and trigger lambda LR-02 with invalid payload
* connect to cloudwatch log and assert the response for the key error for the key S3 on lambda lr-02
