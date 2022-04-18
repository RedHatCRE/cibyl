Bootstrap
=========

Installation
------------

Install `cibyl` from GitHub (Recommended)::

    pip install 'git+https://github.com/rhos-infra/cibyl.git'

Configuration
-------------

In order to use Cibyl's CLI, you should set up configuration first in ``~/.config/cibyl.yaml``.

Configuration is structured as follows::

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

Each type of system will require a different set of parameters in order to start using/querying it.
For more information on how to set up configuration for CLI usage, read the `configuration <configuration.html#configuration>`_ section.

Usage - CLI
-----------

Once you've installed Cibyl and set up the configuration, you can start running cibyl commands

``cibyl --jobs`` will print all the jobs from each specified system in the configuration

To get an idea of what type of information you query for with Cibyl, run ``cibyl -h``
