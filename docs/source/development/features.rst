Features
========

In cibyl we define *features*, which are classes containing a query method that
can run a custom query using python code. A feature is defined as a class that
inherits from the *FeatureDefinition* class, defined in
cibyl/features/__init__.py.

There is a FeatureTemplate class that can be used to quickly define simple features.
The query method of this class
will select the most appropiate source considering the speed_index and the
method to query in the source. To define a new feature using this template, one
only needs to define a class that inherits from FeatureTemplate, set the
attribute *method_to_query* to the method of choice for the source and include
in the *args* attribute the arguments that should be passed to the source's
method  to perform the query (see for example the HA, IPV4, IPV6 features as
a sample).

One could define a feature without using the
FeatureTemplate code at all, the only requirements would be that the class
should provide a query method that accepts a system and returns an
AttributeDictValue object, and should define a name attribute for the feature.
This way of implementing a feature gives the developer total freedom, but does
not provide some functionality like selecting the best sources given the input
arguments. There could be a mixed implementation, that relies on the
FeatureTemplate query method but provided a bit more flexibility. Let's say for
example that one wanted a feature called Example that wants to check whether
a system has any job called 'example' with at least 3 passing builds and runs
a test called 'test_example'. Such a feature could be implemented for example
like:

.. code-block:: python

   class Example(FeatureTemplate, FeatureDefinition):
       def __init__(self):
           self.name = "Example"

       def get_template_args(self):
           """Get the arguments necessary to obtain the information that defines
           the feature."""
           args = {}
           args['jobs'] = Argument("jobs",  arg_type=str,
                                   description="jobs",
                                   value=["example"])
           args['builds'] = Argument("build", arg_type=str,
                                     description="build",
                                     value=[])
           args['jobs'] = Argument("tests",  arg_type=str,
                                   description="tests",
                                   value=["test_example"])
           return args

       def query(self, system, **kwargs):

           def get_method_to_query(self):
               return "get_builds"
            self.get_method_to_query = get_method_to_query
           return_builds = super().query(system, **self.args, **kwargs)

           def get_method_to_query(self):
               return "get_tests"
           self.get_method_to_query = get_method_to_query
           return_tests = super().query(system, **self.args, **kwargs)
           # more code to combine the the returns and apply the desired
           # conditions

Features are classes that inherit from the FeatureDefinition class.
The name of the module where the feature is defined is
used as a category for the features it contains. Features are loaded in the
orchestrator, in the load_features method. There, cibyl will go through
the paths that are registered by the plugins and
the default location to look for features. If features are found and requested
by the user, the the run_features method is executed. If not, a normal query is
executed.

As mentioned before, the query method should return an AttributeDictValue with
the appropiate CI model according to the system and source used. These models
are added to the system in the run_features method. If more than one feature is
run, the output is combined to filter the returned models to add only those
that satisfy all features. In addition, for each feature that runs, a Feature
model is added to the system. This model (which is a CI model, akin to a System
or Job) has only two attributes, the feature name and a boolean marking whether
the feature is present in the system or not.

After all features run, the publisher is used to print all the output. The same
publisher is used for both normal queries and feature queries. The printers for
all systems will print the Feature models added to each system, and after that
it will continue printing other information found in the system if the user ran
cibyl with other arguments like --jobs. In order to handle the different cases,
there are two kind of queries added to the QueryType class: *FEATURES* and
*FEATURES_JOBS*. The first will signal the case when the user has called the
features subcommand, while the second will mark the case where the user has
called the features subcommand with the ``--jobs`` argument.
