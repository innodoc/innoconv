"""loads modules for innoconv"""

from innoconv.modules import MODULES

__all__ = ['MODULES', 'run_mods', 'load_module']


def run_mods(modlist, event, **kwargs):
    """triggers the given event for all modules handling it"""
    for mod in modlist:
        if event in mod.events:
            if mod.handle(event, **kwargs):
                return True
    return False


def load_module(name):
    """Loads a module with the given name"""
    try:
        obj = MODULES[name]()
    except (ImportError, KeyError) as exc:
        raise RuntimeError("module {} not found".format(name)) from exc
    return obj
