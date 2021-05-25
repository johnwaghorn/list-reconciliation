# ListRecon_File Validator Tests
---------------------------------

   |Description                                                                                                                  |DateTime|File        |Expected Message                              |
   |-----------------------------------------------------------------------------------------------------------------------------|--------|------------|----------------------------------------------|
   |Ensure when correct file name with valid date is given the file is processed sucessfully                                     |20210315|GPR4LNA1.C1A|Success                                       |
   |Ensure when file name is capitals the file is processed sucessfully                                                          |20210315|GPR4LNA1.C1A|Success                                       |
   |Ensure when file name is small letters the file is processed sucesfully                                                      |20210315|gpr4lna1.c1a|Success                                       |
   |Ensure when file name is in both captial and small letters then the file is processed sucessfully                            |20210315|gpr4LNa1.C1a|Success                                       |
   |Ensure when file name is in incorret format then the process should fail                                                     |20210315|GDR4BRF1.C1A|Filename must have the correct formatFailed   |
   |Ensure when file date is older than 14 days the process should fail                                                          |20210316|GPR4LNA1.C1A|File date must not be older than 14 daysFailed|
   |Ensure when file is processed the same day it should process sucessfully                                                     |20210315|GPR4LNA1.CFA|Success                                       |
   |Ensure when file was processed on end date of the year on the same day it should process sucessfully                         |20201231|GPR4LNA1.LVA|Success                                       |
   |Ensure when file name is for the last date of the year and processed on 14th Jan of next year, it should process successfully|20210114|GPR4LNA1.LVA|Success                                       |
   |Ensure future file from the last date of the year should fail                                                                |20210115|GPR4LNA1.LVA|File date must not be from the futureFailed   |
   |Ensure file older that 14 days from the last date of the year should fail - edge case                                        |20211231|GPR4LNA1.AVA|File date must not be older than 14 daysFailed|


## validate GP files with the provided table values and ensure the respective validation messages are received
* run gpextract for scenario <Description> using file <File> and date <DateTime> and ensure expected message is <Expected Message>

## validate GP file to check the columns on the invalid records count csv file is as expected
* run gpextract for scenario "positive scenario" using file "GPR4LNA1.C1A" and date "20210315" and ensure expected message is "Success"
* assert "records.csv" file keys are as expected

## validate  for non existing GP file 
* run gpextract for scenario using not existing file and ensure expected message is "No such file or directory: 'GPR4LNA1.EDA'Failed"