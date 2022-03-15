# CIbyl

Command line interface for querying CI environments

## Installation

```
pip install cibyl
```

Set up configuration in one of the following paths:
  * ~/.cibyl/cibyl.yaml
  * /etc/cibyl/cibyl.yaml

A valid configuration should specify an environment, its system(s) and the
system(s) details.
Use the configuration below as a minimal configuration file.
```
environments:
    env_1:
        jenkins_system:
            system_type: ""
```
For query purposes, add sources in the following format:

```
environments:
  staging:
    environment1:
      system_type: 'SYSTEM_TYPE'
      sources:
        source1:
          driver: 'DRIVER'
          username: 'USERNAME'
          token: 'PERSONAL_TOKEN'
          url: 'https://URL.com'
```
## Usage

To list existing environments and their systems, run `cibyl`

## How to Contribute?

Contributions are done via GitHub Pull Requests
