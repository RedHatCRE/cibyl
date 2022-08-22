Features
========

Cibyl allows users to define their own product related data in form of what is known as "features".
Features are basically blocks of code with the purpose of querying for specific product features in one or more environments.

Out of the box Cibyl supports multiple features for existing plugins and users can easily list them with ``cibyl features``

Allowing users to define their own sort of product arguments has multiple advantages:

   * Use internal project functions and mechanisms to define complex custom queries
   * Consistent approach towards querying for product data, in different environments and sources
   * Sharing product related data with other users without extending endlessly the number of product arguments supported by Cibyl

Usage
^^^^^

To list all the existing features: ``cibyl features``

Query IPv4 feature: ``cibyl features ipv6``

Query two features: ``cibyl features ipv6 ha``

Query for a feature in specific set of jobs: ``cibyl features ha --jobs production``

Development
^^^^^^^^^^^

Would like to add a new feature? Read the `features development <development/features.html>`_ section.
