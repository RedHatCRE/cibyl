# CIbyl

CIbyl allows you easily discover and query CI related data from your CI environments

## Quickstart

```
git clone https://review.gerrithub.io/rhos-infra/cibyl
cd cibyl && pip install .
```

Once you have your CIbyl [configuration](#configuration) set up, you can start running `cibyl` commands.

To get information on your configured CI environments, run: `cibyl query`

## Configuration

* The configuration file is YAML based and the hierarchy it supports is the following: Env -> System(s) -> Source(s)
    * Env is the logical CI environment which can include one or more CI systems (e.g. Jenkins, GitHub Actions, ...)
    * System is an actual CI system (currently support are: none :'()
    * Source is where data on the CI system can be pulled from (e.g. the CI system itself, job definitions repository, ELK, etc.)

* The configuration file path by default is `~/.cibyl/cibyl.yaml` but, it can be controlled with the `--config` argument

* A full sample is available in [samples/cibyl.yaml)(samples/cibyl.yaml)

```
environments:
  - env_name:
    - system_name:
      jobs: 'phase1-*'
      type: jenkins
      url: http://some_jenkins.com
      sources:
        source1_name:
          priority: 0
          driver: ...
          - 'repo1':
            url: http://some_job_definitions_repo
        source2_name
          priroty: 2
          driver: ...
  - env2_name:
    ...
```
