Sources
=======

Sources in Cibyl are responsible for performing the queries and getting the data the user is interested in.
A source can be anything: a CI system, repository, database, etc. Cibyl supports the following sources out-of-the-box:

  * `Jenkins <sources/jenkins.html>`_
  * `Jenkins Job Builder <sources/jenkins-job-builder.html>`_
  * `Zuul <sources/zuul.html>`_
  * `Elasticsearch <sources/elasticsearch.html>`_
  * `Zuul Job Definitions <sources/zuul.d.html>`_

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
   :widths: 20 40 10 10 10 10 10
   :header-rows: 1

   * - Argument / Source
     - Description
     - Jenkins
     - Zuul
     - ES
     - JJB
     - Zuul.d
   * - --jobs
     - | Jobs names or pattern
       | Default: all jobs
     - |:ballot_box_with_check:|
     - |:ballot_box_with_check:|
     - |:ballot_box_with_check:|
     - |:ballot_box_with_check:|
     - |:black_square_button:|
   * - --builds
     - | Build numbers
       | Default: all builds
     - |:ballot_box_with_check:|
     - |:ballot_box_with_check:|
     - |:ballot_box_with_check:|
     - |:x:|
     - |:x:|
   * - --last-build
     - | The last build of a job
     - |:ballot_box_with_check:|
     - |:ballot_box_with_check:|
     - |:ballot_box_with_check:|
     - |:x:|
     - |:x:|
   * - --build-status
     - | Build status (default: all)
       | failure, success,
       | abandoned, unstable
     - |:ballot_box_with_check:|
     - |:ballot_box_with_check:|
     - |:ballot_box_with_check:|
     - |:x:|
     - |:x:|
   * - --tests
     - | Test names or pattern
       | Default: all tests
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:ballot_box_with_check:|
     - |:x:|
     - |:x:|
   * - --test-result
     - | Test result (default: all)
       | success, failed, skipped
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:ballot_box_with_check:|
     - |:x:|
     - |:x:|
   * - --test-duration
     - | Test duration (in seconds,
       | default: all)
       | (Can be also range: ">=3")
     - |:ballot_box_with_check:|
     - |:black_square_button:|
     - |:black_square_button:|
     - |:x:|
     - |:x:|
