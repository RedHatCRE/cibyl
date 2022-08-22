CIbyl
=====

.. image:: https://github.com/rhos-infra/cibyl/actions/workflows/pipeline.yaml/badge.svg
   :target: https://github.com/rhos-infra/cibyl/actions/workflows/pipeline.yaml
   :alt: Build Status

Cibyl is a command-line interface and REST API for querying CI/CD environments and systems.

Installation
************

``pip install git+https://github.com/rhos-infra/cibyl.git``

Next, set up `configuration <http://cibyl.readthedocs.org/>`_

::

  environments:                 # List of CI/CD environments
    production:                 # An environment called "production"
      production_jenkins        # A single system called "production_jenkins"
        system_type: jenkins    # The type of the system (jenkins or zuul)
        sources:                # List of sources belong to "production_jenkins" system
          jenkins_api:          # The name of the source which belongs to "production_jenkins" system
            driver: jenkins     # The driver the source will be using
            url: https://...    # The URL of the system
            username: user      # The username to use for the authentication
            token: xyz          # The token to use for the authentication
            cert: False         # Disable/Enable certificates to use for the authentication

Usage
*****

``cibyl`` for listing environments and systems as specified in the configuration

``cibyl query --jobs`` will print all the jobs available in your CI system

``cibyl query --jobs --system <SYSTEM NAME>`` will print all the jobs from one specific system

``cibyl query --jobs --builds`` will print the jobs as well as the status of all the builds of that job

Official Documentation
**********************

For more information please read our `Documentation <http://cibyl.readthedocs.org>`_
