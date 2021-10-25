# Differences Specification

Differences rules, which from given [input files](input-specification.md) and generate [output files](output-specification.md)

## MVP Comparison Rules

During the MVP, [output files](output-specification.md) will be generated of these comparisons and be returned to PCSE, where they will create any update or change actions.

### Date of Birth MN-BR-DB-01

If: mismatch in DOB

Then: Requires Validation

Action: Difference added to output file

### Surname MN-BR-SN-01

If: surname mismatch

Then: Requires Validation

Action: Difference added to output file

### Forenames MN-BR-FN-01

Forename(s) (including middle name)

If: forenames mismatch

Then: Requires Validation

Action: Difference added to output file

### Title MN-BR-TL-01

If: title mismatch

Then: Requires Validation

Action: Difference added to output file

### Gender MN-BR-SX-01

Sex (Gender)

If: mismatch in sex (Gender)

Then: Requires Validation

Action: Difference added to output file

### Address MN-BR-AD-01

If: there is a mismatch in the concatenation of address fields without the postcode

Then: Requires Validation

Action: Difference added to output file

### Postcode MN-BR-AD-02

If: there is a mismatch in the postcode when extraneous white space have been removed

Then: Requires Validation

Action: Difference added to output file

## Automated Business Rules

Here are outlined a set of comparison rules that will trigger either:

- the creation of DSA work items, which will allow for update or change actions to be manually validated and processed
- PDS update requests, for differences that are correct in the GP System that can be updated without manual validation
- GP update requests, for differences that are correct in PDS that can be updated without manual validation

### Date of Birth BR-DB-01

If: mismatch in DOB

Then: Requires Validation

Action: Create DSA Work Item

### Surname BR-SN-01

If: there is a Surname mismatch, and title changed from Mrs (PDS) to Miss (GP), but forename is the same

Then: Accepted Difference

Action: Update PDS with GP record

### Surname BR-SN-02

If: there is a Surname mismatch, and title changed from Mrs (GP) to Miss (PDS), but forename is the same

Then: Accepted Difference

Action: Update PDS with GP record

### Surname BR-SN-03

If: there is a Surname mismatch, but no change to forename, and title hasn’t changed

Then: Requires Validation

Action: Create DSA Work Item

### Surname BR-SN-04

If: there is a Surname mismatch due to additional name data i.e. Colman-Rich (PDS) now just Colman (GP)

Then: Accepted Difference

Action: Update GP with PDS record

### Surname BR-SN-05

If: there is a Surname mismatch due to additional name data i.e. Colman-Rich (GP) now just Colman (PDS

Then: Accepted Difference

Action: Update PDS with GP record

### Surname BR-SN-07

If: there is a Surname mismatch due to a "-" in a double barrell name i.e. Angela Kew Jones (PDS), but Angela Kew-Jones (GP)

Then: Accepted Difference

Action: Update PDS with GP record

### Surname BR-SN-08

If: there is a Surname mismatch due to a "-" in a double barrell name i.e. Angela Kew Jones (GP), but Angela Kew-Jones (PDS)

Then: Accepted Difference

Action: Update PDS with GP record

### Forename(s) (including middle name) BR-FN-01

If: no first or middle name in one of the sources, but there is a first or middle name in the other source

Then: Accepted Difference

Action: Update the source that has the missing first or middle name

### Forename(s) (including middle name) BR-FN-02

If: a matching first name exists in both sources, but one source also has another name (assumed to be the middle name) i.e. If mismatch is forename is due to an additional name/s in one data set

Then: Accepted Difference

Action: Update the source that doesn’t have the middle name

### Title BR-TL-01

If: title mismatch, but forename and surname the same

Then: Accepted Difference

Action: Update PDS with GP record

### Title BR-TL-02

If: title is missing from one source, but is in the other, but forename and surname the same

Then: Accepted Difference

Action: Update the source that has the missing Title

### Total name BR-TN-01

If: there is a mismatch in forename and surname, and they are wrong way round i.e. forename: Colman and surname: James (GP
Data) vs forename James Surname Colman (PDS)

Then: Accepted Difference

Action: Update PDS System with GP Data

### Total name BR-TN-02

If: there is a mismatch due to capital letters eg Angela Kew (PDS), but angela kew (GP)

Then: Accepted Difference

Action: Update GP record with PDS data

### Total name BR-TN-03

If: there is a mismatch due to capital letters eg Angela Kew (GP), but angela kew (PDS)

Then: Accepted Difference

Action: Update PDS with GP record

### Total name BR-TN-04

If: there is a difference across Total name (Title, Forename(s), Surname), and not covered by active rules in BR-TL, BR-FN, BR-SN
or BR-TN rules

Then: Requires Validation

Action: Create DSA Work Item

### Sex BR-SX-01

If: any mismatch in sex

Then: Requires Validation

Action: Create DSA Work Item

### Address BR-AD-01

If: there is a mismatch in the concatenation of address fields without the postcode e.g. 1 High Street, Leeds compared to 1 The Hight Street, Leeds E.g.2 1 High Street, Leeds compared to 12 Main Street, York

Then: Requires Validation

Action: Create DSA Work Item

### Address BR-AD-02

If: there is a mismatch in the postcode when spaces have been removed e.g. LS1 2PQ in the flat file and LS2 1PQ in PDS would result in a compare of LS12PQ against LS21PQ, resulting in a validation required e.g.2. LS1 2PQ and RG12 7TU

Then: Requires Validation

Action: Create DSA Work Item

### Drugs Dispensed Marker BR-DD-01

If: Drug Dispensed Marker mismatch between PDS and flat file, Drug Dispensed Marker = 'Yes' in PDS and '' (meaning 'N') in Flat file, if Practice setting = 'No', Then update Drug Dispensed Marker value in PDS with the 'No'

Then: Accepted Difference

Action: Update PDS with 'No'

### Drugs Dispensed Marker BR-DD-02

If: Drug Dispensed Marker mismatch between PDS and flat file, Drug Dispensed Marker = 'Yes' in PDS and '' (meaning 'N') in Flat file, if Practice setting = 'Yes'

Then: Accepted Difference

Action: Update PDS with GP Practice System 'No'

### Drugs Dispensed Marker BR-DD-03

If: Drug Dispensed Marker mismatch between PDS and flat file, Drug Dispensed Marker = 'No' in PDS and 'Yes' in Flat file, if Practice setting = 'No', Then update Drug Dispensed Marker value in GP Practice System with the 'No'

Then: Accepted Difference

Action: Update GP Practice System with 'No'

### Drugs Dispensed Marker BR-DD-04

If: Drug Dispensed Marker mismatch between PDS and flat file, Drug Dispensed Marker = 'No' in PDS and 'Yes' in Flat file, if Practice setting = 'Yes'

Then: Accepted Difference

Action: Update PDS with GP Practice System 'Yes'
