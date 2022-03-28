Zuul API
========

The Zuul API source pulls data from the Zuul CI system.

Usage
^^^^^

To following is a configuration sample of how to configure the Zuul source::

    environments:
      example_environment:
        zuul_system:
          system_type: zuul
          sources:
            zuul_api_source:
              driver: zuul
              url: 'http://example.zuul.com'

Plugin Support
^^^^^^^^^^^^^^

The Zuul source is supported by the following built-in plugins:

  * OpenStack
