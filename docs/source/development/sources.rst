Sources
=======

To add/develop a new type of source, follow the following guidelines:

* A source should be added to cibyl/sources/<SOURCE_NAME>

* The source class you develop should inherit from the Source class (``cibyl/sources/source.py``)

* For a source to support an argument, it should implement the function name associated with that argument

* Each source method that implements a method of an argument, should be returning an AttributeDict value of the top level entity associated with the CI systems (e.g. ``AttributeDictValue("jobs", attr_type=Job, value=job_objects)``)

* A source should handle only CI/CD related data. If you would like a certain source to pull a product related data, you should add a source class (with the same name as the CI/CD source) to corresponding plugin (``cibyl/plugin/<PLUGIN_NAME>/sources/<SOURCE_DIR/FILE>``)
