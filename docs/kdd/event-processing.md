# Event Processing

## Problem

This is a data processing system, we want to be scalable etc

## Choices

- AWS Eventbridge
- AWS Lambdas + DynamoDB
- AWS Step Functions + AWS Lambdas + DynamoDB

## Details

### AWS Eventbridge

Cannot encrypt with KMS, therefore we cannot put the data into the message bus, therefore we'd need to use something like DynamoDB for the record anyway and use Eventbridge just as a pointer, so limited benefit

### AWS Lambdas + DynamoDB

Have to do a lot of glue work in our own code, start and end of Lambdas have to be concerned with the recieving and sending out of data

### AWS Step Functions + AWS Lambdas + DynamoDB

Step Functions help make the Lambda code simpler, just input and outputs, the state machine can help compose the Lambdas and even handle actions like updating Job Status into DynamoDB

## Decision

AWS Step Functions + AWS Lambdas + DynamoDB
