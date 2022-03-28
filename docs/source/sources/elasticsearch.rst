Elasticsearch
=============

The Elasticsearch source pulls data from the different indexes of the Elasticsearch database.

Usage
^^^^^

To following is a configuration sample of how to configure the Elasticsearch source::

    environments:
      example_environment:
        jenkins_system:
          system_type: jenkins
          sources:
            jenkins_source:
              driver: elasticsearch
              username: some_username
              url: 'http://elasticsearch.example.com:9200'

Plugin Support
^^^^^^^^^^^^^^

The Elasticsearch source is supported by the following built-in plugins:

  * OpenStack
