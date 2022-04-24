Jenkins Job Builder
===================

"Jenkins Job Builder" is the source for obtaining information

Usage
^^^^^

To following is a configuration sample of how to configure the 'Jenkins Job Builder' source::

    environments:
      example_environment:
        jenkins_system:
          system_type: jenkins
          sources:
            jjb_source:
              driver: jenkins_job_builder
              repos:
                  - url: 'https://jjb_repo_example.git'

Plugin Support
^^^^^^^^^^^^^^

The 'Jenkins Job Builder' source is supported by the following built-in plugins:

  * OpenStack
