# Tests for LR-02 lambda to validate and parse the GP file
----------------------------------------------------------

 |DrugDespenserErrorMessage                        |
 |-------------------------------------------------|
 |'DRUGS_DISPENSED_MARKER': "must be 'Y' or blank."|           

## test to ensure when lambda LR-02 is triggered and response status code 202 is recieved
------------------------------------------------------------------------------------------
* trigger lambda LR-02 and assert response status code is "202"
* trigger lambda LR-02  and assert responsemetadata HTTPStatusCode response is "202"

## test to ensure when lambda LR-02 is triggered with invalid payload should throw key error 
--------------------------------------------------------------------------------------------
* connect and trigger lambda LR-02 with invalid payload
* connect to cloudwatch log and assert the response for the key error for the key S3 on lambda lr-02

## test to validate invalid record type
---------------------------------------
* connect to s3 and upload gp file with invalid item "DOWNLOAD" in row "DOW~1" at position "0"
* connect to s3 failed folder and assert failure message "Row 1 for all records must start with 'DOW~1'"

## test to validate invalid _REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE
-----------------------------------------------------------------------------
* connect to s3 and upload gp file with invalid item "12345678,abcdefg" in row "DOW~1" at position "2"
* connect to s3 failed folder and assert failure message "'_INVALID_': {'REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE': 'must be a 7-digit numeric GMC National GP code and 1-6-digit alphanumeric Local GP code separated by a comma.'}"

## test to validate invalid _HA_CIPHER_COL
------------------------------------------
* connect to s3 and upload gp file with invalid item "PNA" in row "DOW~1" at position "3"
* connect to s3 failed folder and assert failure message "'_INVALID_': {'TRADING_PARTNER_NHAIS_CIPHER': 'must be a 3-digit alphanumeric code and match the GP HA cipher'}"

## test to validate invalid _DATE_OF_DOWNLOAD field
---------------------------------------------------
* connect to s3 and upload gp file with invalid item "23230101" in row "DOW~1" at position "4"
* connect to s3 failed folder and assert failure message "'_INVALID_': {'DATE_OF_DOWNLOAD': 'must be a datetime in the format YYYYMMDDHHMM and be less than 14 days old and not in the future.'}"

## test to validate invalid _TRANS_ID
-------------------------------------
* connect to s3 and upload gp file with invalid item "null" in row "DOW~1" at position "6"
* connect to s3 failed folder and assert failure message "'_INVALID_': {'TRANS_ID': 'must be a unique not-null integer greater than 0.'}"

## test to validate invalid _NHS_No
-----------------------------------
* connect to s3 and upload gp file with invalid item "null" in row "DOW~1" at position "7"
* connect to s3 failed folder and assert failure message "'_INVALID_': {'NHS_NUMBER': 'must be a valid NHS number. Max length 10.'}"

## test to validate invalid _SURNAME
------------------------------------
* connect to s3 and upload gp file with invalid item "surn11me" in row "DOW~1" at position "8"
* connect to s3 failed folder and assert failure message "'_INVALID_': {'SURNAME': 'must contain only uppercase alphabetic characters and space, apostrophe or hyphen. Max length 35.'}"

## test to validate invalid _FORNAME
------------------------------------
* connect to s3 and upload gp file with invalid item "F323meric" in row "DOW~1" at position "9"
* connect to s3 failed folder and assert failure message "{'FORENAMES': 'must contain only uppercase alphabetic characters and space, apostrophe, hyphen, comma or full-stop. Max length 35.'}"

## test to validate invalid _PREVIOUS SURNAME
---------------------------------------------
* connect to s3 and upload gp file with invalid item "prev323meric" in row "DOW~1" at position "10"
* connect to s3 failed folder and assert failure message "'_INVALID_': {'PREV_SURNAME': 'must contain only uppercase alphabetic characters and space, apostrophe or hyphen. Max length 35.'}"

## test to validate invalid _TITLE
----------------------------------
* connect to s3 and upload gp file with invalid item "prev323meric" in row "DOW~1" at position "11"
* connect to s3 failed folder and assert failure message "'_INVALID_': {'TITLE': 'must contain only uppercase alphabetic characters and space, apostrophe or hyphen. Max length 35.'}"

## test to validate invalid _SEX
--------------------------------
* connect to s3 and upload gp file with invalid item "SEX" in row "DOW~1" at position "12"
* connect to s3 failed folder and assert failure message "'_INVALID_': {'SEX': 'must be 1 for Male, 2 for Female, 0 for Indeterminate/Not Known or 9 for Not Specified.'}"

## test to validate invalid _DOB
--------------------------------
* connect to s3 and upload gp file with invalid item "'22220101" in row "DOW~1" at position "13"
* connect to s3 failed folder and assert failure message "'_INVALID_': {'DOB': 'must be a date in past in the format YYYYMMDD.'}"

## test to validate invalid _Address line 1
-------------------------------------------
* connect to s3 and upload gp file with invalid item "''1 sdsd" in row "DOW~1" at position "14"
* connect to s3 failed folder and assert failure message "'_INVALID_': {'ADDRESS_LINE1': 'must contain only uppercase alphabetic characters and space, apostrophe, hyphen, comma or full-stop. Max length 35.'}"

## test to validate invalid _Address line 2
-------------------------------------------
* connect to s3 and upload gp file with invalid item "''2 sdsd \n" in row "DOW~1" at position "15"
* connect to s3 failed folder and assert failure message "'ADDRESS_LINE2': 'must contain only uppercase alphabetic characters and space, apostrophe, hyphen, comma or full-stop. Max length 35.'"

## test to validate invalid file content structure
--------------------------------------------------
* connect to s3 and upload gp file with invalid item "'addingline2toline1" in row "DOW~1" at position "15"
* connect to s3 failed folder and assert failure message "Row 2 for all records must start with 'DOW~2'"

## test to validate invalid _Address line 3
-------------------------------------------
* connect to s3 and upload gp file with invalid item "''3 sdsd" in row "DOW~2" at position "2"
* connect to s3 failed folder and assert failure message "'ADDRESS_LINE3': 'must contain only uppercase alphabetic characters and space, apostrophe, hyphen, comma or full-stop. Max length 35.'"

## test to validate invalid _Address line 4
-------------------------------------------
* connect to s3 and upload gp file with invalid item "''4 sdsd" in row "DOW~2" at position "3"
* connect to s3 failed folder and assert failure message "'ADDRESS_LINE4': 'must contain only uppercase alphabetic characters and space, apostrophe, hyphen, comma or full-stop. Max length 35.'"

## test to validate invalid _Address line 5
-------------------------------------------
* connect to s3 and upload gp file with invalid item "''5 sdsdsdsd" in row "DOW~2" at position "4"
* connect to s3 failed folder and assert failure message "'ADDRESS_LINE5': 'must contain only uppercase alphabetic characters and space, apostrophe, hyphen, comma or full-stop. Max length 35.'"

## test to validate invalid _POSTCODE
-------------------------------------
* connect to s3 and upload gp file with invalid item "E1DD1AA" in row "DOW~2" at position "5"
* connect to s3 failed folder and assert failure message "'POSTCODE': 'must be in one of the following formats: AN   NAA, ANN  NAA, AAN  NAA, AANN NAA, ANA  NAA, AANA NAA'"

## test to validate invalid _DrugDispenser
------------------------------------------
* connect to s3 and upload gp file with invalid item "E1DD1AA" in row "DOW~2" at position "6"
* connect to s3 failed folder and assert failure message <DrugDespenserErrorMessage>

