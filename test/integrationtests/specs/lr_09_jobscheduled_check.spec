# Tests for LR-09 job scheduled check
-------------------------------------


## test to ensure able to trigger LR-09 sucessfully
---------------------------------------------------
* trigger lr09 and expected statuscode is "200"

## test to ensure when the inflight table is empty lr09 stopped sucessfully
---------------------------------------------------------------------------
* setup steps to empty all buckets
* setup steps to empty all database tables
* get InFlight table item count
* trigger lr09 and ensure scheduled checked successfully completed
