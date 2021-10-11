# Input Specification

Input files, which check [differences](differences-specification.md) and create [output files](output-specification.md)

## File

### Example

Example of valid file named `K82070_GPR4LNA1.IAA`:

```csv
503\*
DOW~1~1111111,1234~LNA~20210919~1500~985440~4874773259~SZYSZLYK~LIXUE~MICKEY~MR~1~19471201~~45 HIGH STREET
DOW~2~~SHIPLEY~SURREY~KT8  2QJ~Y~~~~
DOW~1~1111111,1234~LNA~20210919~1500~503958~7092823059~MORROW~MAJDIYYA~SINGH~MR~1~19841221~~103 HOOKFIELD
DOW~2~CHIPSTEAD~LEATHERHEAD~~KT10 0NP~Y~~~~
DOW~1~1111111,1234~LNA~20210919~1500~894772~4732188676~HASKELL~CASS~~MRS~1~19350421~~COURT LANE
```

### Contents

The extract process **must** collate the following fields of existing patient Registration data for each patient:

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

Additional Patients to be included in a patient extract:

- A patient marked on the GP System as having been reported as deceased **must** still be included within a extract if no Notification of Deduction has yet been received for that patient from the HA.
- A patient registered on the GP System for which no Acknowledgement has yet been received **must** be included within a extract.

Additional Patients not to be included in a patient extract:

- A patient marked on the GP System as being treated as a Temporary Resident **must not** be included within a extract.

### Records

Extract records to be sent **must** be stored as two records within the file as follows:

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

### Delimiter

All fields **must** be delimited by the `~` character with the exception of the first and last fields for each physical record which **must** be only suffixed and prefixed by a `~` character, respectively.

For example:

Correct - `Field1~Field2~Field3`
Incorrect - `~Field1~Field2~Field3~`

The end of each record **must** be separated by a newline character.

### Filename

`A00000_GPR4AAA1.XYZ`

- `A00000` is the GP Practice ODS code.
- `GPR4` is the... and should be represented as is.
- `AAA` is the HA Cipher of the HA for which the extract has been generated.
- `1` is the... and should be represented as is.
- `X` is a "month indicator", the month in which the extract has been generated:
  - `A` representing January
  - `B` representing February
  - `C` representing March
  - `D` representing April
  - `E` representing May
  - `F` representing June
  - `G` representing July
  - `H` representing August
  - `I` representing September
  - `J` representing October
  - `K` representing November
  - `L` representing December
- `Y` is a "day indicator", the day of the month in which the extract has been generated:
  - `1` representing the 1st
  - `2` representing the 2nd
  - `3` representing the 3rd
  - `4` representing the 4th
  - `5` representing the 5th
  - `6` representing the 6th
  - `7` representing the 7th
  - `8` representing the 8th
  - `9` representing the 9th
  - `A` representing the 10th
  - `B` representing the 11th
  - `C` representing the 12th
  - `D` representing the 13th
  - `E` representing the 14th
  - `F` representing the 15th
  - `G` representing the 16th
  - `H` representing the 17th
  - `I` representing the 18th
  - `J` representing the 19th
  - `K` representing the 20th
  - `L` representing the 21st
  - `M` representing the 22nd
  - `N` representing the 23rd
  - `O` representing the 24th
  - `P` representing the 25th
  - `Q` representing the 26th
  - `R` representing the 27th
  - `S` representing the 28th
  - `T` representing the 29th
  - `U` representing the 30th
  - `V` representing the 31st
- `Z` is the multipart file identifier, however we only support single input files so the value should be `A`.

For example: `A12345_GPR4YW01.DJB`

Which contains the following information:

GP ODS Code: `A12345`
HA Cipher: `YW0`
Extract Date: `April 19th`

The List Reconciliation Solution cannot itself determine which GP Practice a patient or GP Flat File relates to. Therefore, if the GP Flat file is not prefixed or is given an incorrect `Practice ID` followed by an underscore then this will result in a a large number of false positive differences being generated in the ['Not on PDS'](output-files.md#registration-differences-onlyongp-onlyonpds) registration output.

### File header

Before the records within the extract, there **must** be a header record containing the characters `503\*`.

## Records

Any records not marked with `(Required)` can be `null`/`None`/empty and will be treated as valid data.

### Transaction/Record Type (Required)

The Record Type **must** equal "DOW".

### Transaction/Record Row Identifier (Required)

This identifies the individual rows that comprise the multi-row record:

- Record 1 = "1"
- Record 2 = "2"

### GP Code (Required)

The GP Code **must** be:

- the valid GMC National code for the patient's GP
- concatenated with ","
- concatenated with the "local" code for the patient's GP as known by the destination HA.

As such, the GP Code **must**:

- Have alphanumeric and "," characters only.
- Have a maximum length of 14 characters in the following format:
  - Characters 1-7 = Fixed 7 numeric character GMC National GP code
  - Character 8 = comma (,)
  - Characters 9-14 = 1-6 alphanumeric character Local GP code
- Have alphabetic characters in upper case.

### Destination HA Cipher (Required)

The Destination HA Cipher **must**:

- Be the Cipher of the patient's responsible HA.
- Be a valid HA Cipher, i.e. be a current live England and Wales code from the Table of
- The Destination HA Cipher **must** be identical for all patients within a single extract.

Valid HA Ciphers (see Appendix D). As such, the Destination HA Cipher **must**:

- Have alphanumeric characters only.
- Have a maximum length of 3 characters.
- Have alphabetic characters in upper case.

### Transaction/Record Date (Required)

A Record Date **must** be allocated to each record. These **must** be the same for every record and **must** be the date that the extract was undertaken.

The Record Date **must** be in the format:

- "YYYYMMDD"

### Transaction/Record Time (Required)

A Record Time **must** be allocated to each record. These **must** be the same for every record and **must** be the time that the extract was undertaken.

The Record Time **must** be in the format:

- "HHMM"

### Transaction/Record Number (Required)

The Transaction/Record Number **must**:

- Have numeric characters only.
- Have a maximum length of 7 characters.
- Have a value of a positive integer.

Each Download transaction or record **must** be allocated a unique Transaction or Record Number. This will represent a unique identifier for that transaction or record.

This Transaction or Record Number may be:

- From the sequence of Registration Transaction Numbers used for Acceptances, Amendments, etc.
- From a separate sequence of Download Transaction Numbers. or
- A unique numeric identifier already stored against a patient on the GP System conforming to the validation requirements.

Irrespective of which method is used, the one-to-one relationship between Transaction or Record Number and patient **must** be retained within the GP System.

### NHS Number

The NHS Number **must** be the existing, most up-to-date NHS Number of the patient and **must**:

- An all-numeric Number of 10 digits including a check digit (the 10th and final digit in the Number).

Or:

- Have alphanumeric, "?" or "/" characters only.
- Have a maximum length of 15 characters.
- Have alphabetic characters in upper case.

### Surname

The Surname **must**:

- Have alphabetic, ` ` (space), `'` and `-` characters only.
- Have a maximum length of 35 characters (Surnames of more than 35 characters **must** be truncated for these purposes).
- Have alphabetic characters in upper case.

### Forename

Within an extract all Forenames fields are combined to make one overall Patient Forename record. This overall Patient Forename **must**:

- Have alphabetic, ` ` (space), "'" "," "-" and "." characters only.
- Have a maximum length of 35 characters (First Forenames of more than 35 characters **must** be truncated for these purposes).
- Have alphabetic characters in upper case.

### Previous Surname

The Previous Surname **must**:

- Have alphabetic, ` ` (space), `'` and `-` characters only.
- Have a maximum length of 35 characters (Previous Surnames of more than 35 characters
  **must** be truncated for these purposes).
- Have alphabetic characters in upper case.

### Title

The Title **must**:

- Have alphabetic, ` ` (space), `'` and `-` characters only.
- Have a maximum length of 35 characters (Titles of more than 35 characters **must** be truncated for these purposes).
- Have alphabetic characters in upper case.

### Sex

The Sex **must** be one of:

- "1" for Male
- "2" for Female
- "0" for Indeterminate/Not Known
- "9" for Not Specified.

### Date of Birth

The Date of Birth **must**:

- be in the format "CCYYMMDD".
- **must not** be in the future

### Address - House Name

The Address - House Name **must**:

- Have alphanumeric, ` ` (space), `'`, `-`, `.` and `,` characters only.
- Have a maximum length of 35 characters (House Names of more than 35 characters
  **must** be truncated for these purposes).
- Have alphabetic characters in upper case.

The Address - House Name **must** only contain the flat number or name of a property (if one exists).

### Address - Number/Road Name

The Address – Number/Road Name **must**:

- Have alphanumeric, ` ` (space), `'`, `-`, `.` and `,` characters only.
- Have a maximum length of 35 characters (Number/Road Names of more than 35
  characters **must** be truncated for these purposes).
- Have alphabetic characters in upper case.

The Address - Number/Road Name **must** only contain the property number (if one exists) and the road/street name of the property.

### Address - Locality

The Address - Locality **must**:

- Have alphanumeric, ` ` (space), `'`, `-`, `.` and `,` characters only.
- Have a maximum length of 35 characters (Localities of more than 35 characters **must** be truncated for these purposes).
- Have alphabetic characters in upper case.

The Address - Locality **must** only contain the first village/town name/area (if one exists) if different to the property's post town name.

### Address - Post Town

The Address - Post Town **must**:

- Have alphanumeric, ` ` (space), `'`, `-`, `.` and `,` characters only.
- Have a maximum length of 35 characters (Post Towns of more than 35 characters **must** be truncated for these purposes).
- Have alphabetic characters in upper case.

The Address - Post Town **must** only contain the post town name of the property.

### Address - County

The Address - County **must**:

- Have alphanumeric, ` ` (space), `'`, `-`, `.` and `,` characters only.
- Have a maximum length of 35 characters (Counties of more than 35 characters **must** be truncated for these purposes).
- Have alphabetic characters in upper case.
  The Address - County **must** only contain the county of the property (if one exists).

### Address - Postcode

The Address - Postcode **must**:

- Have alphanumeric and ` ` (space) characters only.
- Have alphabetic characters in upper case.
- Have a fixed length of 8 characters and be in one of the following six formats:
  - `AN   NAA`
  - `ANN  NAA`
  - `AAN  NAA`
  - `AANN NAA`
  - `ANA  NAA`
  - `AANA NAA`

### Drugs Dispensed Marker

The Drugs Dispensed Marker **must**:

- only contain a single upper case `Y` character if set "on".

### RPP Mileage

The RPP Mileage **must**:

- Have numeric characters only.
- Have a maximum length of 2 characters.
- Have a value of a positive integer in the range 3 to 50.

### Blocked Route/Special District Marker

The Blocked Route/Special District Marker **must** be one of:

- a single upper case `B` if being set to "Blocked Route" or "Special District".
- a single upper case `S` character if being set to "Special District".

### Walking Units

The Walking Units **must**:

- Have numeric characters only.
- Have a maximum length of 2 characters.
- Have a value of a positive integer in the range 3 to 99 and be exactly divisible by 3.

The GP System **must** ensure that a non-zero value for Walking Units may only be held for a patient if a non-zero value for RPP Mileage is also held for that patient.

### Residential Institute Code

The Residential Institute Code **must**:

- be a valid Residential Institute Code; i.e. the Code **must** be within the Table of Valid Residential Institute Codes for the patient's responsible HA.

As such, the Residential Institute Code **must**:

- Have alphanumeric characters only.
- Have a maximum length of 2 characters.
- Have alphabetic characters in upper case.
