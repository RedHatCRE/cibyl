Installation
============

Install `cibyl` from GitHub (Recommended)::

    pip install 'git+https://github.com/rhos-infra/cibyl.git'

To obtain latest stable released version of Cibyl, install it from PyPi::

    pip install cibyl

.. warning:: Using Cibyl from virtualenv might not work as expected if certifications are required to connect the CI system(s)
.. note:: For development purposes, it's recommended to use ``pip install -e 'git+https://github.com/rhos-infra/cibyl.git'``

Configuration
-------------

In order to use Cibyl's CLI, you should set up configuration first. Configuration is structured as follows::

  environments:
    example_env:
      example_system:
        system_type: jenkins
        sources:
          osp_jenkins:
            driver: jenkins
            url: 'https://some.jenkins.com'
            cert: False
            username: example_username  # Required specifically by Jenkins
            token: example_token        # Required specifically by Jenkins

Default location for the configuration file is ``~/.config/cibyl.yaml``

Each type of system will require a different set of parameters in order to start using/querying it.
For more information on how to set up configuration for CLI usage, read the `configuration <configuration.html#configuration>`_ section.
