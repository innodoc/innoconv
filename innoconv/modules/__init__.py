"""modloader Modules"""

from .abstract_module import AbstractModule
from .copystatic import Copystatic
from .demo import Demo

MODULES = {
    'copystatic': Copystatic,
    'demo': Demo
}

ALL_EVENTS = [
    'load_languages',
    'pre_conversion',
    'pre_language',
    'pre_processing_veto',
    'pre_content_file',
    'process_ast',
    'post_content_file',
    'post_language',
    'post_conversion'
]

__all__ = ['MODULES', 'ALL_EVENTS', 'Demo', 'Copystatic', 'AbstractModule']
