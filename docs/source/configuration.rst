Configuration
=============

Cibyl CLI is fully visible and usable only once you've setup the configuration file. This is because the CLI is dynamically changing based on the type of CI systems you have defined in the configuration file.

Format
^^^^^^

The configuration file is written in YAML::

  environments:              # List of environment files
    example_env:             # Environment name
      example_system:        # System name
        system_type:         # The type of the system (e.g. jenkins, zuul)
          sources:           # List of sources
            example_source:  # Source name
            driver:          # The driver to use (e.g. elasticsearch, jenkins, etc.)
            url:             # The URL to use to connect

Configuration Path
^^^^^^^^^^^^^^^^^^

By default cibyl will look for the configuration file in the following paths:

  * ``~/.config/cibyl.yaml``
  * ``/etc/cibyl/cibyl.yaml``


Validate Configuration
^^^^^^^^^^^^^^^^^^^^^^

The best way to validate the configuration you've added is to run the ``cibyl`` command. This should list the environments and systems specified in the configuration file.
