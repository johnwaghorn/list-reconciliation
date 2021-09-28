# List Reconciliation v0.1

## Options

- [AWS Service](#aws-service)
- [DPS Service](#dps-service)
- [Spine Service](#spine-service)

## AWS Service

### Good

- AWS platform
- Decoupled from main Spine
- Uses PDS API, following API first guidance

### Bad

- Starting from nothing
- Will need to define best practices

## DPS Service

### Good

- Aligns to TRG advice
- No initial or upfront platform requirements required
- Supporting libraries for key functionality, like MESH interaction, already exist
- Should be buildable by February

### Bad

- Cannot make use of Spine AWS Common. Potentially cannot use Spine logging format (application logs may be able to use Spine format, not 100% sure on what flexibility DPS offers here)
- High coupling on DPS platform (seeing similar issues to Spine: long merge queues, high contention, high barrier to entry on local dev)
- Dependencies on knowledge and time on a non-DPS priority

## Spine Service

### Good

- Known and well supported infrastructure
- Buildable by February (Tyler gave ~30 day estimate)

### Bad

- One of the major drivers was to begin to decouple new work
- Will see Spine build and dev process contention

## Suggestion

[AWS Service](#aws-service)

## Decision

[AWS Service](#aws-service)
