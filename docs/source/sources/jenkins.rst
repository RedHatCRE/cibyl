Jenkins
=======

The Jenkins source pulls data from the Jenkins API.

Usage
^^^^^

To following is a configuration sample of how to configure the Jenkins source::

    environments:
      example_environment:
        jenkins_system:
          system_type: jenkins
          sources:
            jenkins_source:
              driver: jenkins
              username: some_username
              cert: True
              token: some_token
              url: 'http://jenkins.example.com'

Plugin Support
^^^^^^^^^^^^^^

The Jenkins source is supported by the following built-in plugins:

  * OpenStack
