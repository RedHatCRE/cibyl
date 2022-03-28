Sources
=======

Sources in Cibyl are responsible for performing the queries and getting the data the user is interested in.
A source can be anything: a CI system, repository, database, etc. Cibyl supports the following sources out-of-the-box:

  * Jenkins
  * Jenkins Job Builder
  * Zuul
  * Elasticsearch
  * Zuul Job Definitions

Configuring Sources
-------------------

The following is an example of Jenkins source configuration::

    environments:
      example_environment:
        jenkins_system:
          system_type: jenkins
          sources:
            jenkins_source:
              driver: jenkins
              username: some_username
              token: some_token
              url: https://jenkins.example.com

See `configuration <configuration.html#configuration>`_ to understand how to properly configure Cibyl for CLI usage.

Source Interface
----------------

Each source can support one or more of the arguments specified by the different models of Cibyl.
The only constraint regarding sources is that each source must inherit from the Source class.

Arguments Matrix
----------------

.. list-table:: The supported arguments in the different built-in sources
   :widths: 25 25 25 25 25 25
   :header-rows: 1

   * - Argument / Source
     - Jenkins
     - Zuul API
     - Elasticsearch
     - JJB
     - Zuul.d
   * - --jobs
     - |:ballot_box_with_check:|
     - |:x:|
     - |:ballot_box_with_check:|
     - |:ballot_box_with_check:|
     - |:x:|
   * - --job-name
     - |:ballot_box_with_check:|
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
   * - --job-url
     - |:ballot_box_with_check:|
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
   * - --builds
     - |:ballot_box_with_check:|
     - |:x:|
     - |:ballot_box_with_check:|
     - |:x:|
     - |:x:|
   * - --last-build
     - |:ballot_box_with_check:|
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
   * - --build-status
     - |:ballot_box_with_check:|
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
   * - --build-number
     - |:ballot_box_with_check:|
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
   * - --tests
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
   * - --test-name
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
   * - --test-class-name
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
   * - --test-result
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
     - |:x:|
