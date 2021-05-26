# Tests for LR-06 sqs to Load validated flat file records
----------------------------------------------------------


## test to ensure when sqs LR-06 is active and when triggered response status code 202 is recieved
--------------------------------------------------------------------------------------------------
* connect and trigger sqs LR-06 and verify the queue url is correct
* assert response HTTPStatusCode is "200" to check sqs LR-06 is active
