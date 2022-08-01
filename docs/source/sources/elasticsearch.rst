Elasticsearch
=============

The Elasticsearch source pulls data from the different indexes of the Elasticsearch database.

Usage
^^^^^

To following is a configuration sample of how to configure the Elasticsearch source

.. include:: ../config_samples/elasticsearch_configuration.rst

Fields
^^^^^^

Elasticsearch should include the following fields in order to be fully operational:

- job_name
- build_number
- build_result
- current_build_result

Plugin Support
^^^^^^^^^^^^^^

The Elasticsearch source is supported by the following built-in plugins:

  * OpenStack
