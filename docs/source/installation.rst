Installation
============

.. code-block:: bash
   :linenos:

        pip install cibyl

Set up configuration in one of the following paths:
  * ~/.config/cibyl.yaml
  * /etc/cibyl/cibyl.yaml

A valid configuration should specify an environment, its system(s) and the
system(s) details.
Use the configuration below as a minimal configuration file.

.. code-block:: yaml
   :linenos:

        environments:
            env_1:
                jenkins_system:
                    system_type: ""

For query purposes, add sources in the following format:


.. code-block:: yaml
   :linenos:

        environments:
          staging:
            environment1:
              system_type: 'SYSTEM_TYPE'
              sources:
                source1:
                  driver: 'DRIVER'
                  username: 'USERNAME'
                  token: 'PERSONAL_TOKEN'
                  url: 'https://URL.com'
