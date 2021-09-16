# Security

## Human Controls

* Github PR Code reviews, requiring code owner approval and passing checks
* CI checks include CodeQL, TFSec, Unit and Integration tests, and a deployed environment.
* TFSec custom rules so we can enforce own requirements
* Dependabot which checks daily for deps updates and creates PRs

## Account Controls

* Breakglass access to production account only - TODO
* All AWS account actions collected by CloudTrail
* AWS Cloudtrail and NHSD LandingZone enforcement of NHSD security requirements.
* AWS Config rules to ensure ongoing conformance
* Account level S3 Public Access blocking
* IAM password policy increased requirements (not used though)
* All non-`eu-west-2` regions have had default resources destroyed - TODO

## AWS Controls

* AWS Cloudtrail (via LandingZone)
* Get all the SCPs enabled - TODO
* AWS Well Architected Review - TODO
* AWS Config
* KMS for S3, Dynamo, Cloudwatch and SSM
* CloudWatch logs, need to be forwarded to Splunk - TODO

## AWS Network Controls

* VPC per account with private, intra and public subnets
* Intra (no-outbound internet access) Subnets for data processing Lambdas
* Internet/NAT Gateways, Routing Tables etc
* Splunk Forwarding, Email and Mesh Lambdas sit in Public Subnets
* VPC Endpoints for Step Functions, Lambda, DynamoDB, S3 and SSM in Private Subnets
* VPC Flow Logs and shipping to Splunk - TODO
* VPC ACLs, only 443 out, high ports return - TODO?

## Observability Controls

* Splunk Dashboards - TODO
* Splunk Alerting - TODO

## Testing Controls

* Pytest, unit testing
* Behave, integrating testing
* Github Actions, for CI enforcing testing as part of pipeline

## Supply Chain Controls

* Github Dependabot and CodeQL scanning
* Artefact based automated deployment, so only code build happens once on merge to main branch, this can be scanned further - TODO
* Use of pipenv, as pip and requirements.txt do not provide a lock based mechanism that can ensure we're using the same hash of downloaded libraries
* Lambdas doing data handling should have minimal use of non-standard library python, reviewed on a per requirement basis
* Move to continuous/automated deployment, so deployment times cannot be socially engineered or guessed - TODO

## NHSD Controls

* Spine Incident management/response
* Frequent Security/Pen Testing
