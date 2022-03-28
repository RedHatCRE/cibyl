Bootstrap
=========

Installation
------------

Install `cibyl` from GitHub::

    pip install 'git+https://github.com/rhos-infra/cibyl.git'

To obtain latest stable released version of Cibyl, install it from PyPi::

    pip install cibyl

.. warning:: Using Cibyl from virtualenv might not work as expected if certifications are required to connect the CI system(s)
.. note:: For development purposes, it's recommended to use ``pip install -e ...``

Configuration
-------------

In order to use Cibyl's CLI, you should set up configuration first. Configuration is structured as follows::

  environments:
    example_env:
      example_system:
        system_type: jenkins
        url: http://example.jenkins.com
        user: example_username
        token: example_token

Default location for the configuration file is ``~/.config/cibyl.yaml``

For more information on how to set up configuration for CLI usage, read the `configuration <configuration.html#configuration>`_ section.

Usage - CLI
-----------

Once you've installed Cibyl and set up the configuration, you can start running cibyl commands

``cibyl --jobs`` will print all the jobs from each specified system in the configuration

To get an idea on what can you query for with cibyl, run ``cibyl -h``
