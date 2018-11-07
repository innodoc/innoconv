"""loads modules for innoconv"""

import importlib

MODULES = [
    'copystatic',
    'demo'
]


def run_mods(modlist, event, **kwargs):
    """triggers the given event for all modules handling it"""
    for mod in modlist:
        if event in mod.events:
            if mod.handle(event, **kwargs):
                return True
    return False


def load_module(name):
    """Loads a module with the given name"""
    classname = name.capitalize()
    try:
        mod = importlib.import_module(
            'innoconv.modules.{}.{}'.format(name, name))
        modclass = getattr(mod, classname)
        obj = modclass()
    except ImportError as exc:
        raise RuntimeError("module {} not found".format(name)) from exc
    return obj


class AbstractModule():
    """Abstract class for Modules"""

    def __init__(self):
        self.events = []

    def handle(self, event, **kwargs):
        """Handles any given event
        by default calls a method named after the event"""
        try:
            return getattr(self, event)(**kwargs)
        except AttributeError:
            raise NotImplementedError
