Feature: List Reconciliation E2E
  In order to reconcile a GPs Data, we need to split and store some PDS data
  from DPS and then recieve a GP File from MESH that will be processed, with
  the results put back into MESH and a summary email sent out

  Scenario: small GP file
    Given we have processed PDS data
    When a GP File is recieved from MESH
    Then a successful reconciliation is produced
    And a summary email is created for sending
