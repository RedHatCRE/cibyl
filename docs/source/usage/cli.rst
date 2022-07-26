CLI
===

Cibyl can be used as as a CLI tool to query CI related information from
multiple CI systems. Cibyl can provide information from two domains: CI/CD data
and product-specific data. The first corresponds to concepts that are pertinent
to many CI systems, like builds, jobs, tests or system-specific concepts like pipelines
and tenants in Zuul systems (for more details on CI concepts supported by cibyl
check the `core models <../models/core.html>`_ section).

Product-specific information is provided by plugins (see the `openstack plugin <../plugins/openstack.html>`_
as an example). As the name indicates, these are properties that are not related
to the CI system but to the product being tested. In the case of openstack,
some examples include the topology of the deployment, or the openstack version
being deployed.

Due to this dual source of information, cibyl can be used to query both kinds
of properties, as well as combine them in more complex queries. This page will
provide several examples of queries that can be done with cibyl.

CLI arguments that accept values follow the assumption that if they are passed
without any value, the user is requesting to list the corresponding
information, while if passed with a value, the value will be used as a filter.
As an example, running ``cibyl --jobs`` will list all available jobs, while
``cibyl --jobs abc`` will list the jobs that have the string `abc` in their
names.

.. note:: Throughout this page we assume  for simplicity that there is only one
   CI system defined in the user configuration. Nevertheless, every command
   shown here can be run with a configuration composed of multiple
   environments, systems and sources. Check the `configuration
   <../configuration.html>`_ section for
   more details on how to construct the configuration for such cases.

.. note:: In cibyl, all cli arguments that accept a value, like `--jobs` or
   `--tests` will consider the input as a regular expression. The regex are
   matched using the syntax defined in the re module (`docs <https://docs.python.org/3/library/re.html>`_).

General parameters
------------------

Before listing interesting use-cases, cibyl has also a set of application-wide
cli arguments that will affect the queries.

``-d, --debug``
    Turn on debug-level logging

``-v, --verbose``
    Verbosity level. This flag is additive, -vv will print more output than -v.
    In verbose mode, additional fields for the output are printed, such as the
    url for jobs, or the duration for builds.

``-c, --config``
    Path to the configuration file, this can be a local path, or a url. If it's
    a url, the file will be downloaded and stored in your local machine.

``--log-mode=[terminal|file|both]``
    Where to write the logging output. Options are terminal, file or both,
    default is both.

``--log-file``
    Path to store the logging output if the `file` or `both` option for
    ``--log-mode`` is selected, default is `cibyl_output.log`.

``--output-format=[text|colorized|json]``
    Sets the output format. Both text and colorized print to standard output,
    but the colorized uses color for better visuals. Json support is not
    complete.

``-p, --plugin``
    Plugins to use in the queries.

CI/CD queries
-------------

Environment selection
^^^^^^^^^^^^^^^^^^^^^

The user configuration might consist of many environments, systems and sources.
However, for any particular query the user might want to only use a subset of
the defined environments. There are four arguments that can be used to achive
this:

``--envs``
    Environments to use in the query, filtering by name

``--systems``
    Systems to use in the query, filtering by name

``--system-type``
    Systems to use in the query, filtering by type

``--sources``
    Sources to use in the query, filtering by name

The arguments presented in this section can be combined with any of the
commands shown anywhere in this page.

Job queries
^^^^^^^^^^^

Cibyl can be used to query the list of all jobs defined in a CI system::

    cibyl --jobs

or to list the jobs that contain the string `123`::

    cibyl --jobs 123

or to list the jobs that end with the string `123`::

    cibyl --jobs "123$"

Build queries
^^^^^^^^^^^^^

Cibyl can be used to query the list of all builds for all jobs defined in a CI system::

    cibyl --jobs --builds

or the last build for all jobs::

    cibyl --jobs --last-build

or the last build for all jobs where that build failed::

    cibyl --jobs --last-build --build-status FAILED

.. note:: The value for the --build-status argument in case insensitive, so
   both `FAILED` and `failed` would produce the same result

or the last build for all jobs that have the string `123` in the name and where that build failed::

    cibyl --jobs 123 --last-build --build-status FAILED

Test queries
^^^^^^^^^^^^

Cibyl can be used to query the list of all tests for all jobs defined in a CI system. To query for tests, the user must specify a build where the tests were run, either through the --last-build or --builds arguments::

    cibyl --jobs --last-build --tests

listing the tests that run in build number 5::

    cibyl --jobs --builds 5 --tests

or list the  tests that contain the string `123` in their name::

    cibyl --jobs --last-build --tests 123

or list only the failing tests::

    cibyl --jobs --last-build --test-result FAILED

or list only the tests that run for more than 5 minutes, but less than 10
minutes (test duration is specified in seconds)::

    cibyl --jobs --last-build --test-duration ">300" "<600"

.. _ranged:
.. note:: The --test-duration is a ranged argument. In cibyl, ranged arguments
   take multiple values in the form "OPERATOR VALUE", without the space in
   between. Common operators like "<", ">", "!=", "==", "<=", ">=" are supported.
   Additionally using a single equal sign "=" is also a valid equality operator,
   and if no operator is specified, the equality one is used by deafault.

Zuul specific queries
^^^^^^^^^^^^^^^^^^^^^

In cibyl, there are some argumetns that are only supported when running queries against a Zuul system, and will be ignored otherwise. For example, we can list all jobs in the `default` tenant::

    cibyl --tenants default --jobs

or list all jobs related to project `example-project` in all tenants::

    cibyl --projects example-project --jobs

or list all jobs under the `check` pipeline::

    ciby --pipelines check --jobs

The arguments shown in previous sections can be combined with the Zuul specific
ones. For example, we could use cibyl to list the last build of the jobs that
have the string `123` in their name, belong to a project named `example`, to
a `check` pipeline and under the `default` tenant, but only if the build was
successful::

    cibyl --tenants default --project example --pipeline check --jobs 123
    --last-build --build-statu SUCCESS

Jenkins specific queries
^^^^^^^^^^^^^^^^^^^^^^^^

As is the case with Zuul systems, Jenkins systems have some specific arguments
that can combined with the more general ones. Cibyl can query Jenkins systems
to list the stages that were run in a build. For example the following command
would show the stages run for the last build of the job called `job_name`::

    cibyl --jobs job_name --last-build --stages


Product queries
---------------

Openstack queries
^^^^^^^^^^^^^^^^^

As part of the functionality provided by the openstack plugin, cibyl can query
the CI systems for openstack related information. For example it's quite simple
to list the version of the ip protocol used in each job::

    cibyl --ip-version

or listing the jobs that use ipv6 protocol::

    cibyl --ip-version 6

Similarly, other openstack properties can be used for queries, and can be
combined for more complex queries. Building on the previous example, let's
build a cibyl command to show the network backend used in every job that also
used ipv6::

    cibyl --ip-version 6 --network-backend

Other examples of relevant openstack arguments include the spec, which provides
the full Openstack specification of a job (note that the spec argument only accepts
one value, more details in the `spec section <../plugins/openstack.html#spec>`_ of
the openstack plugin documentation)::

    cibyl --spec job_name

checking which jobs setup the tests from git, instead of rpm packages::

    cibyl --test-setup git

or filtering by the number of compute and controller nodes used in
a deployment. This can be done via the ``--controllers`` and ``--computes``
arguments, which are ranged arguments (see :ref:`note above<ranged>` for more deatils on what
that means). Let's see an example of how to query for those jobs that use at
least 2 compute nodes and more than 3 controller nodes, but no more than
6 controllers::

    cibyl --controllers ">3" "<=6" --computes ">=2"

The list shown here is not a comprehensive collection of all the arguments defined in
the openstack plugin, check the `plugin page <../plugins/openstack.html>`_ in the documentation for the full list.

Combination of openstack and CI/CD queries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In a cibyl query, CI/CD and openstack arguments can be combined to form
more complex queries. This section will show some examples of such calls. The
following call will list all jobs that contain the string `example`, deploy
openstack using `ceph` as the cinder backend and `geneve` as the network
backend, and also print the last build for each job::

    cibyl --jobs example --cinder-backend ceph --network-backend geneve
    --last-build

the previous example could be expanded to only list those jobs that had
a passing last build::

    cibyl --jobs example --cinder-backend ceph --network-backend geneve
    --last-build --build-status SUCCESS
