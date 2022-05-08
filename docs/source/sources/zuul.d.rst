Zuul Definitions
================

Zuul Definitions is the source for pulling data out of Zuul job definition repositories (usually repos with zuul.d directory).

Zuul definitions support two ways to gather data from Zuul job definition repositories.
1. By Clonning and parsing files in zuul.d dir
2. By Quering GitHub api and parsing files in zuul.d dir

Cibyl will clone repos in ~/.cibyl directory.

When remote: True option is set it will query using github api. To prevent Rate Limiting on GitHub you might need to add
username and token options in the config.


Usage
^^^^^

To following is a configuration sample of how to configure the Jenkins source::

    environments:
      example_environment:
        zuul_system:
          system_type: zuul
          sources:
            zuul_definitions_source:
              driver: zuul.d
              remote: False
              username: "johnsnow"
              token: "ghp_abcdefhijklmnopqrstuvwxyz123456789"
              repos:
                  - url: 'http://zuul_defitions_repo.git'
                  - url: 'http://zuul_defitions_repo1.git'

Plugin Support
^^^^^^^^^^^^^^

The "Zuul Definitions" source is supported by the following built-in plugins:

  * OpenStack
