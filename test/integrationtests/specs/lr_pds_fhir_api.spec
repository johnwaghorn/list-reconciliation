# PDS FHIR API Tests

## Ensure able to access FHIR R4 PATIENT Record sucessfully

* trigger fhir r4 patient api for patient_id "9000000009" and assert response as expected

## Ensure 412 is thrown when missing X-Request-ID

* trigger fhir r4 patient api for patient_id "9000000009" and assert status code 412 for missing X-Request-ID
