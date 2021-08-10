BODY = """The GP file: {filename} has been compared to PDS at {timestamp}

{only_on_pds} patient records were found on PDS, that were not in the GP file.

{only_on_gp} patient records were found in the GP file, that are not associated to this GP in PDS.

The comparison run has also discovered {diffs_count} discrepancies that have generated {patient_count} work
item/s to resolve, with {pds_updated_count} record/s being automatically updated in PDS and
{human_validation_count} record/s being provided for the GP Practice to review and update.

The files generated can be found in your MESH mailbox:
    - {filelist}

For support reference, the Reconciliation Run Id associated to this email is: {job_id}"""
