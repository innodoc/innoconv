""" Demo for A module"""

from innoconv.modloader import AbstractModule


class Demo(AbstractModule):
    """a Demo Module"""

    def __init__(self):
        super(Demo, self).__init__()
        self.events.extend([
            'load_languages',
            'pre_conversion',
            'pre_language',
            'pre_processing_veto',
            'pre_content_file',
            'process_ast',
            'post_content_file',
            'post_language',
            'post_conversion'
        ])
