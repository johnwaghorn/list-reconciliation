# List Reconciliation v0.2

## Options

- [AWS Service v0.1](#aws-service-v01)
- [DPS Service](#dps-service)
- [Spine Service](#spine-service)
- [AWS Service v0.2](#aws-service-v02)

## AWS Service v0.1

### Good

- Exists
- Seems to work for \<1,000 record files
- Can be remediated to somewhat working condition by February 2022
- Uses the AWS platform
- Decoupled from Spine core

### Bad

- Uses PDS API, so does not meet long term TRG advice, incomplete rate limiting implementation
- Cannot support record level validation rejections
- Still needs operational work, logging etc
- Still requires security remediation work and a Pen Test
- Unsure which specifications and requirements the validations are built to

### Questions

- Can we not get a faster/higher throughput PDS API?

## DPS Service

### Good

- Aligns to TRG advice
- No initial or upfront platform requirements cost
- Supporting libraries for key functionality, like MESH interaction, already exist
- Should be buildable by February 2022
- Opportunity to cross skill Engineers to DPS/Databricks/Spark

### Bad

- Cannot make use of Spine AWS Common Library
- Potentially cannot use Spine logging format (application logs may be able to use Spine format, not 100% sure on what flexibility DPS offers here)
- High coupling on DPS platform (seeing similar issues to Spine: long merge queues, high contention, high barrier to entry on local dev)
- Dependencies on knowledge and time on a non-DPS priority

## Spine Service

### Good

- Known and well supported infrastructure
- Robust underlying infrastructure
- Buildable by February 2022 (~30 day estimate)

### Bad

- One of the major drivers was to begin to decouple new work
- Will see Spine build and dev process contention
- Removes an opportunity for Engineers to work with AWS
- Resource requirements need adding to overall capacity planning

## AWS Service v0.2

### Good

- Full control
- Helps build base functionality needed for future Spine AWS based services
- Can be built by February 2022
- Does not "overload" the PDS API
- Many different services and technologies available on AWS

### Bad

- Requires application development and architecture
- Needs operational work, logging etc
- Requires security remediation work and repeated Pen Test
- You need to store and maintain a copy of PDS, this will be expensive and wasteful (will probably see issues like DynamoDB record size limitations as found by the AWS PDS POC)
- Need to make sure you don't just build a subset of DPS functionality, and then incur all of the overhead of maintaining and supporting it versus just using DPS and having a team running the platform

### Potential Architecture

![Target Architecture Diagram](../diagrams/ListReconciliationTarget.png)

## Suggestion

TBC

## Decision

TBC
