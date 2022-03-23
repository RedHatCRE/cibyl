..  documentation master file

=====
Cibyl
=====

Cibyl is a command-line interface and REST API for querying CI environments and systems.

Currently it supports out-of-the-box the following CI systems:

  * Jenkins
  * Zuul

The project originated from Red Hat OpenStack DevOps team that looked for a solution to provide an "easier" method
for inspecting multiple different CI environments and systems.
The name Cibyl, a form of Sybil, derived from the Greek sybilla or sibilla. Like a prophetess, Cibyl delve into depths of CI systems
for "hidden" info revelation. CI-byl is also a wordplay that reflects the relation to CI.

Welcome to Cibyl's documentation!
====================================

.. toctree::
   :maxdepth: 2
   :caption: Quickstart

   bootstrap
   usage

.. toctree::
   :maxdepth: 2
   :caption: Setup

   installation
   configuration

.. toctree::
   :maxdepth: 2
   :caption: Usage

   usage/cli
   usage/api

.. toctree::
   :maxdepth: 2
   :caption: Core

   configuration
   terminology
   parser
   plugins

.. toctree::
   :maxdepth: 2
   :caption: Sources

   sources/jenkins
   sources/zuul
   sources/jenkins-job-builder
   sources/elasticsearch
   sources/zuul.d

.. toctree::
   :maxdepth: 2
   :caption: Models

   models/core
   models/plugin

.. toctree::
   :maxdepth: 2
   :caption: Plugins

   plugins/openstack

.. toctree::
   :maxdepth: 2
   :caption: Developers

   development/tests
   development/contribute


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
