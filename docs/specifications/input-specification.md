# Input Specification

Input files, which check [differences](differences-specification.md) and create [output files](output-specification.md)

## File

### Contents

The Download process **MUST** collate the following fields of existing patient Registration data for each patient matching the Download requirement for transmission to the appropriate HA:

- GP Code
- NHS Number
- Surname
- First Forename
- Second Forename
- Other Forename(s)
- Previous Surname
- Title
- Sex
- Date of Birth
- Address (5 fields)
- Postcode
- Drugs Dispensed Marker
- RPP Mileage
- Blocked Route/Special District Marker
- Walking Units
- Residential Institute Code

Note that the NHS Number may be in any valid format for NHS Numbers, and will be the most up-to-date NHS Number of the patient on the GP System.

Attention should, therefore, be given to determining which patients are to be included within such a patient Download - for example:

- A patient marked on the GP System as having been reported as deceased **MUST** still be included within a Download if no Notification of Deduction has yet been received for that patient from the HA.
- A patient marked on the GP System as being treated as a Temporary Resident **MUST** NOT be included within a Download.
- A patient registered on the GP System for which no Acknowledgement has yet been received **MUST** be included within a Download.

### Records

Download records to be sent within a flat ASCII file **MUST** be physically stored as two records within the file as follows:

#### Record 1

- [Record Type](#transactionrecord-type-required)
- [Record 1](#transactionrecord-row-number-required)
- [GP Code](#gp-code-required)
- [Destination HA Cipher](#destination-ha-cipher-required)
- [Record Date](#transactionrecord-date-required)
- [Record Time](#transactionrecord-time-required)
- [Record Number](#transactionrecord-number-required)
- [NHS Number](#nhs-number)
- [Surname](#surname)
- [Forename(s)](#first-forename)
- [Previous Surname](#previous-surname)
- [Title](#title)
- [Sex](#sex)
- [Date of Birth](#date-of-birth)
- [Address - House Name](#address---house-name)
- [Address - Number/Road Name](#address---numberroad-name)

#### Record 2

- [Record Type](#transactionrecord-type-required)
- [Record 2](#transactionrecord-row-number-required)
- [Address - Locality](#address---locality)
- [Address - Post Town](#address---post-town)
- [Address - County](#address---county)
- [Address - Postcode](#address---postcode)
- [Drugs Dispensed Marker](#drugs-dispensed-marker)
- [RPP Mileage](#rpp-mileage)
- [Blocked Route/Special District Marker](#blocked-routespecial-district-marker)
- [Walking Units](#walking-units)
- [Residential Institute Code](#residential-institute-code)

### Structure

All fields **MUST** be delimited by the `~` character with the exception of the first and last fields for each physical record which **MUST** be only suffixed and prefixed by a `~` character, respectively.

Trailing `~` characters **MUST** be present.

Fields marked with an asterisk (`\*`) **MUST** contain a non-null value. Fields not containing a value **MUST** be null.

If the Download is split in to more than one flat ASCII file, only the first of these files should contain a header record (that is the file with a DOS filename extension ending in the character "A").

### Filename

`GPR4AAA1.XYZ`

- AAA is the HA Cipher of the HA for which the Download is being undertaken.
- X is a "month indicator" - the month in which the Download is being undertaken - "A" representing January, "B" representing February, ... ,"L" representing December.
- Y is a "day indicator" - the day of the month in which the Download is being undertaken - "1" representing the 1st, ... ,"9" representing the 9th, "A" representing the 10th, ... ,"V" representing the 31st.
- Z is an incrementing sequence of alphabetic characters starting at "A" if the Download is being split into a number of files. For example, if separate Download files are created for each GP in a Practice, Z **MUST** be "A" for the first Download file, "B" for the second Download file, and so on. If more than one floppy disk is required for a Download, each file on each disk **MUST** be allocated a unique filename.
- The format of Download transactions within the "Daily Transactions" file is not being dictated by this specification. However, it is strongly recommended that data is stored within this file in the format that it **MUST** be sent to the HA.
- As part of the transmission process, the Download transactions **MUST** be deleted from the "Daily Transactions" file. They **MUST** NOT be copied to the "Completed Transactions" file, and **MUST** NOT, therefore, appear within any Archive files. Additionally, it is recommended that Download transactions are not copied to the application level "Transaction Backup" file.

The GP Flat File should be renamed to include the GP Practice ID (represented by the ODS code) followed by an underscore.

For example: `A12345_GPR4YW01.DJB`

The List Reconcilliation Solution being unable to determine which GP Practice a patient or GP Flat File relates to. Therefore, ff the GP Flat file is not prefixed or is given an incorrect `Practice ID` followed by an underscore then this will result in a a large number of false positive differences being generated in the ['Not on PDS'](output-files.md#registration-differences-onlyongp-onlyonpds) registration output.

### File header

Before the Download records within the ASCII file, the GP System **MUST** create a header record containing the characters `503\*`.

## Records

Any records not marked with `(Required)` can be `null`/`None`/empty and will be treated as valid data.

### Transaction/Record Type (Required)

Within ASCII Download records, the Record Type **MUST** equal "DOW".
All out-going Download transactions generated by the transmission process **MUST** be combined within one EDIFACT message.

### Transaction/Record Row Identifier (Required)

**TODO: jstringer**

This identifies the individual rows that comprise the multi-row record:

- Record 1 = "1"
- Record 2 = "2"

### GP Code (Required)

Within EDIFACT Download transactions and ASCII Download records, the GP Code **MUST** be:

- the valid GMC National code for the patient's GP
- concatenated with ","
- concatenated with the "local" code for the patient's GP as known by the destination HA.

As such, the GP Code **MUST**:

- Have alphanumeric and "," characters only.
- Have a maximum length of 14 characters in the following format:
  Characters 1-7 = Fixed 7 numeric character GMC National GP code Character 8 = comma (,)
  Characters 9-14 = 1-6 alphanumeric character Local GP code
- Have alphabetic characters in upper case.

### Destination HA Cipher (Required)

Within EDIFACT Download transactions and ASCII Download records, the Destination HA Cipher **MUST**:

- Be the Cipher of the patient's responsible HA.
- Be a valid HA Cipher, i.e. be a current live England and Wales code from the Table of
  Valid HA Ciphers (see Appendix D). As such, the Destination HA Cipher **MUST**:

* Have alphanumeric characters only.
* Have a maximum length of 3 characters. * Have alphabetic characters in upper case.
  Clearly, the Destination HA Cipher **MUST** be identical for all patients within a single Download.

### Transaction/Record Date (Required)

If the Download is to be sent to an HA within a flat ASCII file on a floppy disk, a Record Date and Time **MUST** be allocated to each Download record. These **MUST** be the same for every Download record and **MUST** be the date and time that the Download was undertaken.

Within ASCII Download records, the Record Date **MUST** be in the format "CCYYMMDD" and
the Record Time in the format "HHMM".
All out-going Download transactions generated by the transmission process **MUST** be combined within one EDIFACT message with a Transaction Date and Time qualifier "137", format "203" - "CCYYMMDDHHMM" within a DTM segment.
Transaction/Record Number (Required)
Within EDIFACT Download transactions and ASCII Download records, the Transaction/Record Number **MUST**:

- Have numeric characters only.
- Have a maximum length of 7 characters.
- Have a value of a positive integer.

### Transaction/Record Time (Required)

If the Download is to be sent to an HA within a flat ASCII file on a floppy disk, a Record Date and Time **MUST** be allocated to each Download record. These **MUST** be the same for every Download record and **MUST** be the date and time that the Download was undertaken.

**TODO: jstringer**

### Transaction/Record Number (Required)

Each Download transaction or record **MUST** be allocated a unique Transaction or Record Number. This will represent a unique identifier for that transaction or record. An Upload transaction or record raised at an HA during the processing of a Download will be given the same Transaction or Record Number as the corresponding Download transaction or record.

This Transaction or Record Number may be:

- From the sequence of Registration Transaction Numbers used for Acceptances, Amendments, etc.
- From a separate sequence of Download Transaction Numbers. or
- A unique numeric identifier already stored against a patient on the GP System conforming to the validation requirements.

Irrespective of which method is used, the one-to-one relationship between Transaction or Record Number and patient **MUST** be retained within the GP System for the possible receipt of corresponding Upload transactions.

If the Download is to be transmitted to an HA over the Network, the Transaction Numbers may be allocated to the Download transactions either at the time of their generation within the "Daily Transactions" file or at the time of transmission.

### NHS Number

Within EDIFACT Download transactions and ASCII Download records, the NHS Number **MUST** be the existing, most up-to-date NHS Number of the patient and **MUST** be in one of the acceptable formats detailed in Appendix F. As such, the NHS Number **MUST**:

- Have alphanumeric, "?" or "/" characters only.
- Have a maximum length of 15 characters.
- Have alphabetic characters in upper case.
  or **MUST** be an all-numeric Number of 10 digits including a check digit (the 10th and final digit in the Number).

### Surname

Within EDIFACT Download transactions and ASCII Download records, the Surname **MUST**:

- Have alphabetic, SPACE, "'" and "-" characters only.
- Have a maximum length of 35 characters (Surnames of more than 35 characters **MUST** be truncated for these purposes).
- Have alphabetic characters in upper case.

### Forename(s)

Within the Download records in the ASCII file, the GP System **MUST** ensure that the First Forename, Second Forename and Other Forenames fields are combined to make one overall Patient Forename record. This overall Patient Forename should then be the value within the Download.

#### First Forename

Within EDIFACT Download transactions, the First Forename **MUST**:

- Have alphabetic, SPACE, "'" "," "-" and "." characters only.
- Have a maximum length of 35 characters (First Forenames of more than 35 characters **MUST** be truncated for these purposes).
- Have alphabetic characters in upper case.

#### Second Forename

Within EDIFACT Download transactions, the Second Forename **MUST**:

- Have alphabetic, SPACE, "'" "," "-" and "." characters only.
- Have a maximum length of 35 characters (Second Forenames of more than 35 characters **MUST** be truncated for these purposes).
- Have alphabetic characters in upper case.

#### Other Forenames

Within EDIFACT Download transactions, the Other Forenames **MUST**:

- Have alphabetic, SPACE, "'" "," "-" and "." characters only.
- Have a maximum length of 35 characters (Other Forenames totalling more than 35 characters **MUST** be truncated for these purposes).
- Have alphabetic characters in upper case.

### Previous Surname

Within EDIFACT Download transactions and ASCII Download records, the Previous Surname **MUST**:

- Have alphabetic, SPACE, "'" and "-" characters only.
- Have a maximum length of 35 characters (Previous Surnames of more than 35 characters
  **MUST** be truncated for these purposes).
- Have alphabetic characters in upper case.

### Title

Within EDIFACT Download transactions and ASCII Download records, the Title **MUST**:

- Have alphabetic, SPACE, "'" and "-" characters only.
- Have a maximum length of 35 characters (Titles of more than 35 characters **MUST** be truncated for these purposes).
- Have alphabetic characters in upper case.

### Sex

Within EDIFACT Download transactions and ASCII Download records, the Sex **MUST** be one of:

- "1" for Male
- "2" for Female
- "0" for Indeterminate/Not Known
- "9" for Not Specified.

### Date of Birth

Within ASCII Download records, the Date of Birth **MUST**:

- be in the format "CCYYMMDD".

Within EDIFACT Download transactions, the Date of Birth **MUST** have qualifier "329", format "102" - "CCYYMMDD" within a DTM segment.
For both, the Date of Birth **MUST** NOT be in the future

### Address - House Name

Within EDIFACT Download transactions and ASCII Download records, the Address - House Name **MUST**:

- Have alphanumeric, SPACE, "'", "-", "." and "," characters only.
- Have a maximum length of 35 characters (House Names of more than 35 characters
  **MUST** be truncated for these purposes).
- Have alphabetic characters in upper case.

The Address - House Name **MUST** only contain the flat number or name of a property (if one exists).

### Address - Number/Road Name

Within EDIFACT Download transactions and ASCII Download records, the Address – Number/Road Name **MUST**:

- Have alphanumeric, SPACE, "'", "-", "." and "," characters only.
- Have a maximum length of 35 characters (Number/Road Names of more than 35
  characters **MUST** be truncated for these purposes).
- Have alphabetic characters in upper case.

The Address - Number/Road Name **MUST** only contain the property number (if one exists) and the road/street name of the property.

### Address - Locality

Within EDIFACT Download transactions and ASCII Download records, the Address - Locality **MUST**:

- Have alphanumeric, SPACE, "'", "-", "." and "," characters only.
- Have a maximum length of 35 characters (Localities of more than 35 characters **MUST** be truncated for these purposes).
- Have alphabetic characters in upper case.

The Address - Locality **MUST** only contain the first village/town name/area (if one exists) if different to the property's post town name.

### Address - Post Town

Within EDIFACT Download transactions and ASCII Download records, the Address - Post Town **MUST**:

- Have alphanumeric, SPACE, "'", "-", "." and "," characters only.
- Have a maximum length of 35 characters (Post Towns of more than 35 characters **MUST** be truncated for these purposes).
- Have alphabetic characters in upper case.

The Address - Post Town **MUST** only contain the post town name of the property.

### Address - County

Within EDIFACT Download transactions and ASCII Download records, the Address - County **MUST**:

- Have alphanumeric, SPACE, "'", "-", "." and "," characters only.
- Have a maximum length of 35 characters (Counties of more than 35 characters **MUST** be truncated for these purposes).
- Have alphabetic characters in upper case.
  The Address - County **MUST** only contain the county of the property (if one exists).

### Address - Postcode

Within EDIFACT Download transactions and ASCII Download records, the Address - Postcode **MUST**:

- Have alphanumeric and SPACE characters only.
- Have alphabetic characters in upper case.
- Have a fixed length of 8 characters and be in one of the following six formats:
  - "AN   NAA"
  - "ANN  NAA"
  - "AAN  NAA"
  - "AANN NAA"
  - "ANA  NAA"
  - "AANA NAA"

For postcodes of the format "AN NAA" For postcodes of the format "ANN NAA" For postcodes of the format "AAN NAA" For postcodes of the format "AANN NAA" For postcodes of the format "ANA NAA" For postcodes of the format "AANA NAA"

### Drugs Dispensed Marker

Within EDIFACT Download transactions and ASCII Download records, the Drugs Dispensed Marker **MUST**:

- only contain a single upper case "Y" character if set "on".

### RPP Mileage

Within EDIFACT Download transactions and ASCII Download records, the RPP Mileage **MUST**:

- Have numeric characters only.
- Have a maximum length of 2 characters.
- Have a value of a positive integer in the range 3 to 50.

### Blocked Route/Special District Marker

Within EDIFACT Download transactions and ASCII Download records, the Blocked Route/Special District Marker **MUST** be one of:

- a single upper case "B" if being set to "Blocked Route" or "Special District".
- a single upper case "S" character if being set to "Special District".

### Walking Units

Within EDIFACT Download transactions and ASCII Download records, the Walking Units **MUST**:

- Have numeric characters only.
- Have a maximum length of 2 characters.
- Have a value of a positive integer in the range 3 to 99 and be exactly divisible by 3.

The GP System **MUST** ensure that a non-zero value for Walking Units may only be held for a patient if a non-zero value for RPP Mileage is also held for that patient.

### Residential Institute Code

Within EDIFACT Download transactions and ASCII Download records, the Residential Institute Code **MUST**:

- be a valid Residential Institute Code; i.e. the Code **MUST** be within the Table of Valid Residential Institute Codes for the patient's responsible HA (see section 4.3.4).

As such, the Residential Institute Code **MUST**:

- Have alphanumeric characters only.
- Have a maximum length of 2 characters.
- Have alphabetic characters in upper case.

## Examples

Example of valid file named `K82070_GPR4LNA1.IAA`:

```csv
503\*
DOW~1~1111111,1234~LNA~20210919~1500~985440~4874773259~SZYSZLYK~LIXUE~MICKEY~MR~1~19471201~~45 HIGH STREET
DOW~2~~SHIPLEY~SURREY~KT8  2QJ~Y~~~~
DOW~1~1111111,1234~LNA~20210919~1500~503958~7092823059~MORROW~MAJDIYYA~SINGH~MR~1~19841221~~103 HOOKFIELD
DOW~2~CHIPSTEAD~LEATHERHEAD~~KT10 0NP~Y~~~~
DOW~1~1111111,1234~LNA~20210919~1500~894772~4732188676~HASKELL~CASS~~MRS~1~19350421~~COURT LANE
```
