# CIbyl

Command line interface for querying CI environments

## Installation

```
pip install cibyl
```

Set up configuration in one of the following paths:
  * ~/.cibyl/cibyl.yaml
  * /etc/cibyl/cibyl.yaml

```
environments:
  env1:
    system1:
      sources:
        source1:
          url: ...
          type: jenkins
```

## Usage

To list existing environments and their systems, run `cibyl`

## How to Contribute?

Contributions are done via GitHub Pull Requests
