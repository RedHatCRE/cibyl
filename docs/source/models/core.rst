Core Models
===========

Core models (aka CI/CD models) are built-in CI/CD Cibyl models:

  * Environment: A CI/CD environment with one or more CI/CD systems. This is mostly a logical separation, rather than a physical one.
  * System: A CI/CD system such as Jenkins, Zuul ,etc.
  * Pipeline: A specific Zuul concept which used for describing a workflow
  * Job: A particular task/automation in the CI/CD system
  * Build: An execution instance of a job
  * Test: A test execution that is part of a build


The way they are organized and associated one with each other, mainly depends on the type of the CI/CD system being used.
For a Jenkins system for example, the hierarchy includes Job and Build models, while for Zuul system, the hierarchy includes Pipeline, Job and Build models.

::

    Environment
    ├── System
    │   └── Job       # Jenkins
    │       └── Build
    │           └── Test
    │   └── Pipeline  # Zuul
    │       └── Job
    │           └── Build
    │               └── Test
