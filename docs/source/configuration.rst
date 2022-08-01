Configuration
=============

Cibyl CLI is fully visible and usable only once you've setup the configuration file.
This is because the CLI is dynamically changing based on the type of CI systems
you have defined in the configuration file.

Format
^^^^^^
The configuration file is written in YAML and is divided in two sections:
`environments` and `plugins`. See below for an example of a minimal
configuration that shows both sections.

.. include:: config_samples/minimal_configuration.rst

The `environments` contains a list of environments. Each environment might
contain one or more systems, which in turn might contain one or more sources.
More details about this hierarchy can be found in the `Core Models section
<models/core.html#core-models>`_. In short, an environment models a group of CI
systems that are setup for a common purpose. At the same time, each CI system
can have multiple sources of information available. See the `Full Configuration`_
section for an example of a configuration file with multiple environments,
systems and sources.

The `plugins` section contains a list of plugins that should be loaded to
provide cibyl with product-specific functionality.

Configuration Path
^^^^^^^^^^^^^^^^^^

By default cibyl will look for the configuration file in the following paths:

  * ``~/.config/cibyl.yaml``
  * ``/etc/cibyl/cibyl.yaml``

A different path can be used if the argument ``--conf path`` is used.
Additionally, the ``--conf`` argument also supports passing a URL to
configuration file. If a URL is passed, it will be downloaded to ``~/.config/cibyl.yaml``.

Sources
^^^^^^^

Cibyl supports multiple different types of sources. Each source may require some
specific configuration. Below we link a page for each source implemented in
cibyl. This pages contain a brief description of the source, a configuration
sample and which plugins support it.

  * `Jenkins <sources/jenkins.html>`_
  * `Zuul API <sources/zuul_api.html>`_
  * `Elasticsearch <sources/elasticsearch.html>`_
  * `Zuul Definitions <sources/zuul.d.html>`_
  * `Jenkins Job Builder <sources/jenkins-job-builder.html>`_

Validate Configuration
^^^^^^^^^^^^^^^^^^^^^^

The best way to validate the configuration you've added is correct,
is to run the ``cibyl`` command. This should list the environments
and systems specified in the configuration file. If the configuration is
correct, then cibyl will print the environments and systems defined in the
configuration. Taking the minimal configuration defined in the `Format`_
section, running cibyl will print::

    Environment: production
      System: production_jenkins

If there is some problem with the configuration file, cibyl will raise one of
the following errors:

  * ``ConfigurationNotFound``: There is no configuration file in any of the default
    paths or the path specified by the user.
  * ``EmptyConfiguration``: A configuration file was found, but it's empty.
  * ``MissingEnvrionments``: The configuration file does not include any
    environments
  * ``MissingSystems``: An environment in the configuration file does not
    include any systems
  * ``MissingSystemKey``: A system in the configuration is missing a required
    key
  * ``MissingSystemType``: The type of one system in the configuration was not
    specified
  * ``NonSupportedSystemKey``: A key in the configuration of one system is not
    supported (e.g. a parameter was added to the wrong system)
  * ``MissingSystemSources``: A system in the configuration has no sources
  * ``NonSupportedSourceKey``: A key in the configuration of one source is not
    supported (e.g. a parameter was added to the wrong source)
  * ``NonSuppportedSourceType``: A source type in the configuration is not
    supported
  * ``MissingSourceKey``: The configuration of one source is incomplete and
    missing a required key
  * ``MissingSourceType``: The type of a source in the configuration is not
    specified

Full Configuration
^^^^^^^^^^^^^^^^^^

As mentioned before, the configuration file might contain many environments,
systems and sources. In the example below, a configuration consisting of two
environments is shown. The first environment `production`, contains three
systems: `production_jenkins_1`, `production_jenkins_2` and `production_zuul`.
The `production_jenkins_1` system contains two sources, a Jenkins source
called `jenkins1_api` and a Jenkins Job Builder source called
`job_definitions`. The `production_jenkins_2` and `production_zuul` systems
contain one source each, a Jenkins and Zuul source, respectively. Finally, the
`staging` environment contains a system `staging_jenkins` with a single Jenkins
source.

.. include:: config_samples/full_configuration.rst

Disabling environments, systems and sources
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It's possible to disable each type of entity in Cibyl with the directive ``enabled: false``.
For example, the following will disable the environment ``staging``` and the system ``production-2``

.. include:: config_samples/disabled_configuration.rst


.. note:: you can't use a disabled environment, even if specifying it directly with one of the following arguments: --envs, --systems and --sources.
