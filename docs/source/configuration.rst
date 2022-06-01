Configuration
=============

Cibyl CLI is fully visible and usable only once you've setup the configuration file. This is because the CLI is dynamically changing based on the type of CI systems you have defined in the configuration file.

Format
^^^^^^

The configuration file is written in YAML:

.. include:: config_samples/minimal_configuration.rst

Configuration Path
^^^^^^^^^^^^^^^^^^

By default cibyl will look for the configuration file in the following paths:

  * ``~/.config/cibyl.yaml``
  * ``/etc/cibyl/cibyl.yaml``


Sources
^^^^^^^

Cibyl supports multiple different types of sources. Each configured in a different way:

  * `Jenkins <sources/jenkins.html>`_
  * `Zuul API <sources/zuul_api.html>`_
  * `Elasticsearch <sources/elasticsearch.html>`_
  * `Zuul Definitions <sources/zuul.d.html>`_
  * `Jenkins Job Builder <sources/jenkins-job-builder.html>`_

Validate Configuration
^^^^^^^^^^^^^^^^^^^^^^

The best way to validate the configuration you've added is correct, is to run the ``cibyl`` command. This should list the environments and systems specified in the configuration file.

Full Configuration
^^^^^^^^^^^^^^^^^^

.. include:: config_samples/full_configuration.rst

Disabling environments, systems and sources
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It's possible to disable each type of entity in Cibyl with the directive ``enabled: false``.
For example, the following will disable the environment ``staging``` and the system ``production-2``

.. include:: config_samples/disabled_configuration.rst


Note: you can't use a disabled environment, even if specifying it directly with one of the following arguments: --envs, --systems and --sources.
