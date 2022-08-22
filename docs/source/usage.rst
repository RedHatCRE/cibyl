Usage
=====

CLI
---

Basic
^^^^^

Running ``cibyl`` with no arguments, will print the environments and systems as set up in your configuration.
Cibyl supports multiple subcommands. The most common one is query, that allows
to query many environments for different CI/CD and product specific data.
Another example is the ``features`` subcommand, which allows to query whether
certain product-specific features are supported in each of the environments of
the configuration (see `features section <features.html>`_ for more details).

Jobs
^^^^

Running ``cibyl query --jobs`` will retrieve information on all the jobs for each environment specified in your configuration.

In order to retrieve jobs for a specific environment, use the ``--envs Environment`` argument.
If the environment includes multiple systems, you can also choose a specific system with the ``--systems System`` argument.
The same can be done for sources with the ``--sources Source`` argument.

This was a simple example of what you could do with cibyl, to get a more depth
overview see the `CLI usage <usage/cli.html>`_ section.

Python
------

To Do
