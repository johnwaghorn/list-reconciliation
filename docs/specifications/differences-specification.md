# Differences Specification

Differences rules, which from given [input files](input-specification.md) and generate [output files](output-specification.md)

## Date of Birth MN-BR-DB-01

If mismatch in DOB

Requires Validation

Create DSA Work Item

## Surname MN-BR-SN-01

If surname mismatch

Requires Validation

Create DSA Work Item

## Forenames MN-BR-FN-01

Forename(s) (including middle name)

If forenames mismatch

Requires Validation

Create DSA Work Item

## Title MN-BR-TL-01

If title mismatch

Requires Validation

Create DSA Work Item

## Gender MN-BR-SX-01

Sex (Gender)

If mismatch in sex (Gender)

Requires Validation

Create DSA Work Item

## Address MN-BR-AD-01

If there is a mismatch in the concatenation of address fields without the postcode

e.g.1 High Street, Leeds compared to 1 The Hight Street, Leeds
e.g.2 1 High Street, Leeds compared to 12 Main Street, York

Requires Validation

Create DSA Work Item

## Postcode MN-BR-AD-02

If there is a mismatch in the postcode when extraneous white space have been removed

e.g. LS1  2PQ (two spaces in the data) in the flat file
and LS2 1PQ in PDS would result in a compare of LS1 2PQ against LS2 1PQ

Requires Validation

Create DSA Work Item
