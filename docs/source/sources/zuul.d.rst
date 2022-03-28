Zuul Definitions
================

Zuul Definitions is the source for pulling data out of Zuul job definition repositories (usually repos with zuul.d directory).

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
              url: 'http://zuul_defitions_repo.git

Plugin Support
^^^^^^^^^^^^^^

The "Zuul Definitions" source is supported by the following built-in plugins:

  * OpenStack
