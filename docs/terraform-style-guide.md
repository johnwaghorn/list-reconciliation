# Terraform Style Guide

## All code should be formatted

All code should be committed after being run through `terraform fmt`, the CI build will fail if code does not pass a format check

## Consolidate multiple resource outputs to single object output

There's currently a lot of duplication in the terraform outputs
We should combine these into a single object in the output, to help keep readability and ease of change
These can then be read as JSON objects into the test code that consumes them

## Name things by their AWS name

As terraform is not platform agnostic and to be consistent with the rest of the code, we should ensure all resources match their AWS name

## Terraform naming conventions

* Names of AWS things have hypens in them, not underscores
* Unless the service only allows `[A-Za-z0-9]` then use CamelCase naming
* Names of terraform resources are lowercase and use underscores, not hypens
* File names should be plurals (eg outputs.tf)
* Don't use only the component ID (`LR-[0-9]*`) in code, use the full name

## Use top level variables for only things to dynamically change on each build

We don't have anything that needs this, until we need to pass in the roles for the preprod and prod accounts, we should be using locals instead

Variables are still needed to pass data between modules

## Use AWS data resources rather than inlined JSON

On several resources, such as IAM policies, we use inlined JSON to define the policy

We should use the IAM Policy Data Resources, which can be `terraform fmt`'d, validated and provides a slightly better developer experience as you're writing HCL not JSON
