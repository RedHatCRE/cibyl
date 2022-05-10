CIbyl
=====

Cibyl is a command-line interface and REST API for querying CI/CD environments and systems.

Installation
************

``pip install git+https://github.com/rhos-infra/cibyl.git``

Next, set up `configuration <http://cibyl.readthedocs.org/>`_

.. include:: docs/source/config_samples/minimal_configuration.rst

Usage
*****

``cibyl`` for listing environments and systems as specified in the configuration

``cibyl --jobs`` will print all the jobs available in your CI system

``cibyl --jobs --system <SYSTEM NAME>`` will print all the jobs from one specific system

``cibyl --jobs --builds`` will print the jobs as well as the status of all the builds of that job


Official Documentation
**********************

For more information please read our `Documentation <http://cibyl.readthedocs.org>`_
