# ListRecon_File Validator Tests
---------------------------------
|DateTime  | File1       | File2       | Expected Message                                                             |
|----------|-------------|-------------|------------------------------------------------------------------------------|
|20210315  |GPR4LNA1.C1A |GPR4LNA1.C1B |Success                                                                       |
|20210315  |GPR4LNA1.C1A |GPR4LNA1.C1B |Success                                                                       |
|20210315  |gpr4lna1.c1a |gpr4lna1.c1b |Success                                                                       |
|20210315  |gpr4LNa1.C1a |GPr4lna1.c1B |Success                                                                       |
|20210315  |GPR4LNA1.C1A |GPR4PNA1.C1B |All filenames must be identical up to the penultimate characterFailed         |
|20210315  |GPR4LNA1.C1A |GPR4LNA1.C1D |File extension identifiers must be sequential, starting from 'A'Failed        |
|20210315  |GDR4BRF1.C1A |GDR4BRF1.C1B |All filenames must have the correct formatFailed                              |
|20210316  |GPR4LNA1.C1A |GPR4LNA1.C1B |File date must not be older than 14 daysFailed                                |
|20210315  |GPR4LNA1.CFA |GPR4LNA1.CFB |Success                                                                       |
|20201231  |GPR4LNA1.LVA |GPR4LNA1.LVB |Success                                                                       |
|20210114  |GPR4LNA1.LVA |GPR4LNA1.LVB |Success                                                                       |
|20210115  |GPR4LNA1.LVA |GPR4LNA1.LVB |File date must not be from the futureFailed                                   |
|20211231  |GPR4LNA1.AVA |GPR4LNA1.AVB |File date must not be older than 14 daysFailed                                |


## validate GP files with the provided table values and ensure the respective validation messages are received
* run gpextract for <File1> and <File2> and date <DateTime> and expected message is <Expected Message>