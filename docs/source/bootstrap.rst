Bootstrap
=========

Installation
------------

Install `cibyl` from GitHub (Recommended)::

    pip install 'git+https://github.com/rhos-infra/cibyl.git'

Configuration
-------------

In order to use Cibyl's CLI, you should set up configuration first in ``~/.config/cibyl.yaml``.

Configuration is structured as follows

.. include:: config_samples/minimal_configuration.rst

.. note:: | Red Hat OpenStack user? use the following command to set up the configuration:
          | wget https://url.corp.redhat.com/cibyl-config -O ~/.config/cibyl.yaml

For more information on how to set up the configuration, read the `configuration <configuration.html#configuration>`_ section.

Usage - CLI
-----------

Once you've installed Cibyl and set up the configuration, you can start running cibyl commands

``cibyl query --jobs`` will print all the jobs from each specified system in the configuration

To get an idea of what type of commands you can use with Cibyl, run ``cibyl -h``

To get an idea of what type of information you query for with Cibyl, run ``cibyl query -h``

For a more in depth guide on how to use Cibyl, read the `CLI usage
<usage/cli.html>`_ section.
