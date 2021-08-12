# Tests for LR-02 lambda to validate and parse the GP file
----------------------------------------------------------

|InvalidItem     |Row  |Position|InvalidMessage                                                                                                                                                                                                               |
|----------------|-----|--------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|DOWNLOAD        |DOW~1|0       |Row 1 for all records must start with 'DOW~1'                                                                                                                                                                                |   
|12345678,abcdefg|DOW~1|2       |"_INVALID_": {"REGISTERED_GP_GMC_NUMBER,REGISTERED_GP_LOCAL_CODE": "GP Code - Must be a valid 7-digit numeric GMC National GP code and 1-6-digit alphanumeric Local GP code separated by a comma.", "ON_LINES": "6-7"        |   
|PNA             |DOW~1|3       |"_INVALID_": {"TRADING_PARTNER_NHAIS_CIPHER": "Destination HA Cipher - Must be a valid 3-digit alphanumeric code that matches the GP HA cipher", "ON_LINES": "6-7"}                                                          |    
|23230101        |DOW~1|4       | "_INVALID_": {"DATE_OF_DOWNLOAD": "Transaction/Record Date and Time - Must be a valid transmission date and timestamp, in the format YYYMMDDHHMM, which is less than 14 days old and not in the future.", "ON_LINES": "6-7"}|   
|null            |DOW~1|6       |"_INVALID_": {"TRANS_ID": "Transaction/Record Number - Must be a unique, not-null integer greater than 0.", "ON_LINES": "6-7"}                                                                                               |
|null            |DOW~1|7       |"_INVALID_": {"NHS_NUMBER": "NHS Number - Must be a valid NHS number. Max length 10.", "ON_LINES": "6-7"}}                                                                                                                   |
|surn11me        |DOW~1|8       |"_INVALID_": {"SURNAME": "Surname - must contain only uppercase alphabetic characters and space, apostrophe or hyphen. Max length 35.", "ON_LINES": "6-7"}                                                                                                                                                                                                                          |
|F323meric       |DOW~1|9       |"_INVALID_": {"FORENAMES": "Forename - must contain only uppercase alphabetic characters and space, apostrophe, hyphen, comma or full-stop. Max length 35.", "ON_LINES": "6-7"}                                                                                                                                                                                                     |
|prev323meric    |DOW~1|10      |"_INVALID_": {"PREV_SURNAME": "Surname - must contain only uppercase alphabetic characters and space, apostrophe or hyphen. Max length 35.", "ON_LINES": "6-7"}                                                                                                                                                                                                                     |
|Title           |DOW~1|11      |"_INVALID_": {"TITLE": "Title - must contain only uppercase alphabetic characters and space, apostrophe or hyphen. Max length 35.", "ON_LINES": "6-7"}                                                                                                                                                                                                                              |
|SEX             |DOW~1|12      |"_INVALID_": {"SEX": "Sex - Must be 1 for Male, 2 for Female, 0 for Indeterminate/Not Known or 9 for Not Specified.", "ON_LINES": "6-7"}                                                                                                                                                                                                                                            |
|22220101        |DOW~1|13      |"_INVALID_": {"DOB": "Date of Birth - Must be a date in the past in the format YYYYMMDD.", "ON_LINES": "6-7"}                                                                                                                                                                                                                                                                       |
|''1 sdsd        |DOW~1|14      |"_INVALID_": {"ADDRESS_LINE1": "Address Line - Must contain only uppercase alphabetic characters and space, apostrophe, hyphen, comma or full-stop. Max length 35.", "ON_LINES": "6-7"}                                                                                                                                                                                             |
|'addingln2toln1 |DOW~1|15      |"error_type": "INVALID_STRUCTURE", "message": ["Row 2 for all records must start with 'DOW~2'"]                                                                                                                                                                                                                                                                                     |
|''3 sdsd        |DOW~2|2       |"_INVALID_": {"DATE_OF_DOWNLOAD": "Transaction/Record Date and Time - Must be a valid transmission date and timestamp, in the format YYYMMDDHHMM, which is less than 14 days old and not in the future.", "ADDRESS_LINE3": "Address Line - Must contain only uppercase alphabetic characters and space, apostrophe, hyphen, comma or full-stop. Max length 35.", "ON_LINES": "6-7"} |
|''4 sdsd        |DOW~2|3       |"_INVALID_": {"DATE_OF_DOWNLOAD": "Transaction/Record Date and Time - Must be a valid transmission date and timestamp, in the format YYYMMDDHHMM, which is less than 14 days old and not in the future.", "ADDRESS_LINE4": "Address Line - Must contain only uppercase alphabetic characters and space, apostrophe, hyphen, comma or full-stop. Max length 35.", "ON_LINES": "6-7"} |
|''5 sdsdsdsd    |DOW~2|4       | "_INVALID_": {"DATE_OF_DOWNLOAD": "Transaction/Record Date and Time - Must be a valid transmission date and timestamp, in the format YYYMMDDHHMM, which is less than 14 days old and not in the future.", "ADDRESS_LINE5": "Address Line - Must contain only uppercase alphabetic characters and space, apostrophe, hyphen, comma or full-stop. Max length 35.", "ON_LINES": "6-7"}|
|E1DD1AA         |DOW~2|5       |"_INVALID_": {"DATE_OF_DOWNLOAD": "Transaction/Record Date and Time - Must be a valid transmission date and timestamp, in the format YYYMMDDHHMM, which is less than 14 days old and not in the future.", "POSTCODE": "Postcode - Must be 8 characters and in one of the following formats: AN   NAA, ANN  NAA, AAN  NAA, AANN NAA, ANA  NAA, AANA NAA.", "ON_LINES": "6-7"}        |
|E1DD1AA         |DOW~2|6       |"_INVALID_": {"DATE_OF_DOWNLOAD": "Transaction/Record Date and Time - Must be a valid transmission date and timestamp, in the format YYYMMDDHHMM, which is less than 14 days old and not in the future.", "DRUGS_DISPENSED_MARKER": "Drug Dispensed Marker - Must be 'Y' or blank.", "ON_LINES": "6-7"}         |



* setup steps to empty all buckets

## test to ensure correct validation messages are logged in the fail logs folder for different invalid scenarios
----------------------------------------------------------------------------------------------------------------
* connect to s3 and upload gp file with invalid item <InvalidItem> in row <Row> at position <Position>
* connect to s3 failed folder and assert failure message <InvalidMessage>


## test to invalid data provided in position 15 raised correct valid error message 
---------------------------------------------------------------------------------
* connect to s3 and upload gp file with invalid item "''2 sdsd\n" in row "DOW~1" at position "15"
* connect to s3 failed folder and assert failure message "Address Lines - Must contain only uppercase alphabetic characters and space, apostrophe, hyphen, comma or full-stop. Max length 35."
