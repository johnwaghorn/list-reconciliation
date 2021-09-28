# Gauge Integration Tests For List Recon Project

## Pre-requisite

Gauge, Python, Pip

## Installation

Gauge Instalation
Install Gauge - https://docs.gauge.org/getting_started/installing-gauge.html?os=windows&language=javascript&ide=vscode

Gauge Python Instalation

`gauge install python`

## Alternate Installation options

Install specific version

`gauge install python -v 0.2.3`
`[pip / pip3] install getgauge`

## How to Execute tests

# Cmd / Bash

1. Open terminal and navigate to the dir containing specs (`cd test/integrationtests`).
1. execute the command to run all the tests in the spec folder : `gauge run specs`

# Vscode / IntelliJ

1. Open the project in Vscode / IntelliJ.
1. To run all the tests in spec, navigate to the dir containing specs (`..tests/integrationtests/specs`) and
   click on the 'run spec' button on the spec title to run all the scenarios in the spec file.
1. To run individual tests, Goto the specific test in the spec and click on the 'run scenario'.
1. To view the execution results : `../reports/html-report/index.html`

### Tagging

Tags are used to associate labels with specifications or scenarios. Tags help in searching or filtering specs or scenarios.

Tags are written as comma separated values in the specification with a prefix Tags: . Both scenarios and specifications can be separately tagged, however, only one set of tags can be added to a single specification or scenario. A tag applied to a spec automatically applies to a scenario as well. More info here.(https://docs.gauge.org/writing-specifications.html?os=windows&language=javascript&ide=vscode#tags).

1. `wip` - for those scenarios which are under development and ready to be released.

**Note :** we can start giving the respective tags once its deployed to different environments
in the format : `env-(envName)`. For E.g. 'env-Staging', 'env-Production'

### Black

Use `make black` after writing the step implementation for every test specs.
