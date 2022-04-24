import yaml


def encrypted_constructor(loader: yaml.SafeLoader,
                          node: yaml.nodes.MappingNode):
    """
    Construct an ecrypted token.
    """
    return ""


def get_loader():
    """
    Add constructors to PyYAML loader.
    """
    loader = yaml.SafeLoader
    loader.add_constructor("!encrypted/pkcs1-oaep", encrypted_constructor)
    return loader
