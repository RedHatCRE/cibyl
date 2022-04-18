CIbyl
=====

Cibyl is a command-line interface and REST API for querying CI environments and systems.

Installation
************

``pip install git+https://github.com/rhos-infra/cibyl.git``

Next, set up `configuration <http://cibyl.readthedocs.org/>`_::

  environments:
      example_env:
        example_system:
          system_type: jenkins
          sources:
            osp_jenkins:
              driver: jenkins
              url: 'https://some.jenkins.com'
              username: example_username  # Required specifically by Jenkins
              token: example_token        # Required specifically by Jenkins

Usage
*****

``cibyl`` for listing environments and systems as specified in the configuration

``cibyl --jobs`` will print all the jobs available in your CI system

``cibyl --jobs --system <SYSTEM NAME>`` will print all the jobs from one specific system

``cibyl --jobs --builds`` will print the jobs as well as the status of all the builds of that job


Official Documentation
**********************

For more information please read our `Documentation <http://cibyl.readthedocs.org>`_
