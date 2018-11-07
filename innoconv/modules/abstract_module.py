"""Abstract class from which all Modules descend"""


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
