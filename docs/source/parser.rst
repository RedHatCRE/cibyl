Parser
======

Cibyl provides two sources of user input, the configuration file and the command
line arguments. The configuration file details the ci environment that the user
wants to query, while the command line arguments tell Cibyl what the user wants
to query.

Cibyl's cli is divided in several subcommands. The parser is the component
responsible for bringing all the subcommands together and ensuring the
corresponding arguments are added. In the case of the ``features`` subcommands
that is simple, since it only has one argument. The case of the ``query``
sucommand is different, since the cli arguments are extended dynamically depending on the
contents of the configuration.

.. note::

    The rest of this page is relevant **only** for the ``query`` subcommand.

When running ``cibyl query -h`` only the arguments that are relevant to the user,
according to its configuration, will be shown.  If there is no configuration
file, Cibyl will just print a few general arguments when calling ``cibyl query -h``.
If the configuration is populated then arguments will be added depending on its contents.

The parser is extended using a hierarchy of CI models. This hierarchy is
Cibyl's  internal representation of the CI environments. The models are created after reading the
configuration and the hierarchy is implicitely defined in the API attribute of
said models. For example, one environment might include a Jenkins instance as
CI system, and have it also as source for information, in addition to an
ElasticSearch instance as a second source. With this environment, if the user
runs ``cibyl query -h``, it will show arguments that are relevant to a Jenkins
system, like ``--jobs``, ``--builds`` or ``--build-status``. In such a case it will
not show arguments like ``--pipelines`` which would be useful if the CI system
was a Zuul instance.

The API of a CI model is a dictionary with the following structure (extracted
from the System API)::

    API = {
        'name': {
            'attr_type': str,
            'arguments': []
        },
        'sources': {
            'attr_type': Source,
            'attribute_value_class': AttributeListValue,
            'arguments': [Argument(name='--sources', arg_type=str,
                                   nargs="*",
                                   description="Source name")]
        },
        'jobs': {'attr_type': Job,
                 'attribute_value_class': AttributeDictValue,
                 'arguments': [Argument(name='--jobs', arg_type=str,
                                        nargs='*',
                                        description="System jobs",
                                        func='get_jobs')]}
    }

each key corresponds to the name of an attribute, and the value is another
dictionary with attribute-related information. At this point we need to
distinguish between arguments and attributes. In Cibyl an ``Argument`` is the object
that is obtained from parsing the user input. The values passed to each option
like ``--debug`` or ``--jobs`` are stored in an ``Argument``. Attributes correspond to the actual
key-value pairs in the API. An attribute has an ``attribute_value_class`` which
by default is ``AttributeValue``, but can also be ``AttributeDictValue`` and ``AttributeListValue``.
The difference between the three is the how they store the arguments. The first
is intended to hold a single option (things like name, type, etc.). While the
other two hold a collection of values either in a dictionary or a list (hence
the name). The information provided by the user is accessible throgh the
``value`` field of any ``Attribute`` class.

Each API element has also an `attr_type`, which describes what kind of object
will it hold. In the example above `name` will hold a string, while `jobs`
will hold a dictonary of Job objects. This allows us to establish the
hierarchy mentioned previously, by checking if the `attr_type` field is not
a builtin type. Finally, there is an `arguments` field, which associates the
actual options that will be shown in the cli with an attribute. An attribute may
have no arguments, one argument or multiple arguments associated with it.

``Argument`` objects have a set of options to configure the behavior of the
cli. The `name` determines the option that will be shown, `arg_type` specifies
the type used to store the user input (str, int, etc.), `nargs` and
`description` have the same meaning as they do in the arparse module.
The `level` argument, measures how deep in the hierarchy
a given model is. Finally, we see the `func` argument, which points to the
method a source must implement in order to provide information about a certain
model. In the example shown here, only jobs has an argument with `func`
defined, as it is the only CI model present. If the user runs a query like::

    cibyl query --jobs

then Cibyl will look at the sources defined and check whether any has a method
``get_jobs``, and if it finds one it will use it to get all the jobs available
in that source.

Arguments are added to the application parser in the ``extend_parser`` method
of the ``Orchestrator`` class.  This method loops through the API of a model
(in the first call it will be an ``Environment`` model) and adds its arguments. If any
of the API elements is a CI model, the element's API is recursively used to
augment the parser. As the ``extend_parser`` method iterates through the model
hierarchy, it creates a graph of the relationships between query methods (the
sources' methods that are added to the arguments' `func` attribute). The edges
of the graph are created when a new recursive call is made. As an example, when
exploring the API for the Job model, we know that the arguments will call
``get_jobs``, so when a new call is made for the Build API, a new edge wil be
created from ``get_jobs`` to all the new query methods that are found, in this
case it will be ``get_builds``.

For each recursive call, the **level** is increased.
The level parameter is key to identify the source of information for the query
that the user sends. In the Jenkins environment example mentioned before,
we may have a hierarchy like::

    Environment => System => Job => Build

where each at each step we increase the level by 1. We can then parse the cli
arguments and sort by decreasing level. To select which query method should be
called, cibyl relies on the graph constructed during the call to
``extend_parser``. It iterates over the sorted list of arguments and for each
of them constructs a path to the root of the graph. The intermediate nodes in
this path are removed from the list of arguments to query, since by the
hierarchical nature of the relationship between the models, calling an
argument's `func` makes the call to the argument's parent `func` redundant.

In the example above, *Build* is the model with the largest level. If we assume that
user has made a call like ``cibyl --jobs --builds``, we want to query the sources for builds,
but we known that each build will be associated with a job, and each job will be associated with
a system, etc. We also know that after calling ``get_builds``, we will not need
to call ``get_jobs``. Thus we get a sorted list of arguments, which is [`builds`, `jobs`].
We create a path from `builds` to the root of the graph, which in the case of
a Jenkins systems is `jobs` (for a zuul system this would be more complex).
After iterating over the path, we remove `jobs` from the list of arguments to
query, since `builds` already will provide the `jobs` information.
