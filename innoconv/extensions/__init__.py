"""
Extensions are a way of extending the functionality of innoConv in a modular
way. They can be enabled on a one-by-one basis.
"""

from innoconv.extensions.copystatic import CopyStatic

#: List of available extensions
EXTENSIONS = {
    'copystatic': CopyStatic,
}


def add_extension(name):
    """Instantiates an extension.

    :param name: Extension name
    :type name: str
    """
    try:
        obj = EXTENSIONS[name]()
    except (ImportError, KeyError) as exc:
        raise RuntimeError("Extension {} not found".format(name)) from exc
    return obj
