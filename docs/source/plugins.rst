Plugins
=======

Plugins allow you to extend supported models, either with your own CI models
or models that go behind CI like product related models.
A supported plugin in Cibyl has to adhere following
structure:: 

    cibyl 
    ├── plugins
    │   └── example        # Arbitrary plugin name
    │       └── plugin.py

Plugin Class
^^^^^^^^^^^^

.. code-block:: python

class ExamplePlugin:

    def extend(self, model_api: dict):
        model_api['new_attribute'] = {
            'attr_type': str,
            arguments: []
        }