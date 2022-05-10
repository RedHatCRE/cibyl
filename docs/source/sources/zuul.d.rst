Zuul Definitions
================

Zuul Definitions is the source for pulling data out of Zuul job definition repositories (usually repos with zuul.d directory).

Zuul definitions support two ways to gather data from Zuul job definition repositories:

  1. By Clonning and parsing files in zuul.d dir
  2. By Quering GitHub API and parsing files in zuul.d dir

Cibyl will clone repos to ~/.cibyl directory.

When ``remote: True`` option is set it will query using GitHub API instead of cloning the repositories and query them locally.

.. warning:: To prevent rate limiting on GitHub you might need to add username and token options in the config.

Usage
^^^^^

To following is a configuration sample of how to configure the Zuul definitions source to work with local repos

.. include:: ../config_samples/zuul_definitions_local_configuration.rst

To following is a configuration sample of how to configure the Zuul definitions source to work with GitHub API

.. include:: ../config_samples/zuul_definitions_remote_configuration.rst

Plugin Support
^^^^^^^^^^^^^^

The "Zuul Definitions" source is supported by the following built-in plugins:

  * OpenStack
