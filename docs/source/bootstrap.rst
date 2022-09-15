Bootstrap
=========

Installation
------------

Install `cibyl` from PyPI (Recommended)::

    pip install cibyl

Another option (only recommended for more experienced users) is to install `cibyl` from GitHub::

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

Once you've installed Cibyl and set up the configuration, you can start running cibyl commands.
The command::

    cibyl query --jobs

will print all the jobs from each specified system in the configuration

To get an idea of what type of commands you can use with Cibyl, run::

    cibyl -h

To get an idea of what type of information you query for with Cibyl, run::

    cibyl query -h

If your configuration file is not saved in a default path (e.g
``~/.config/cibyl.yaml``) you can use with the ``--config`` argument. For
example, to list all jobs for each system::

    cibyl --config /config/file/path query --jobs

For a more in depth guide on how to use Cibyl, read the `CLI usage
<usage/cli.html>`_ section.
