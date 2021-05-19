# ListRecon_File Validator Tests
---------------------------------

   |DateTime|File        |Expected Message                                                                   |
   |--------|------------|-----------------------------------------------------------------------------------|
   |20210315|GPR4LNA1.C1A|Success                                                                            |
   |20210315|GPR4LNA1.C1A|Success                                                                            |
   |20210315|gpr4lna1.c1a|Success                                                                            |
   |20210315|gpr4LNa1.C1a|Success                                                                            |
   |20210315|GDR4BRF1.C1A|Filename must have the correct formatFailed                                        |
   |20210316|GPR4LNA1.C1A|File date must not be older than 14 daysFailed                                     |
   |20210315|GPR4LNA1.CFA|Success                                                                            |
   |20201231|GPR4LNA1.LVA|Success                                                                            |
   |20210114|GPR4LNA1.LVA|Success                                                                            |
   |20210115|GPR4LNA1.LVA|File date must not be from the futureFailed                                        |
   |20211231|GPR4LNA1.AVA|File date must not be older than 14 daysFailed                                     |


## validate GP files with the provided table values and ensure the respective validation messages are received
* run gpextract for <File> and date <DateTime> and expected message is <Expected Message>
