""" Squishes strigns and spaces """

# from innoconv.utils import log
from innoconv.modloader import AbstractModule


class Squish(AbstractModule):
    """docstring for Squish."""

    def __init__(self):
        super(Squish, self).__init__()
        self.events.extend([
            'process_ast'
        ])

    def process_ast(self, ast):
        """Squishes the spaces and strings"""
        self.squish(ast)

    def squish(self, json):
        """ Does the squishing of strings and spaces """

        if isinstance(json, list):
            # try:
            self._squish_array(json)
            # except TypeError:
            #     print(json)
            #     input()
        elif isinstance(json, dict):
            for key in json.keys():
                self.squish(json[key])

    def _squish_array(self, json_array):

        new_array = []

        current_string = ""

        for element in json_array:
            if isinstance(element, dict) and \
                    "t" in element and (element["t"] == "SoftBreak"
                                        or element["t"] == "Space"):
                if not current_string or \
                        (current_string and current_string[-1] != " "):
                    current_string += ' '
            elif isinstance(element, dict) and \
                    "t" in element and element["t"] == "Str":
                current_string += element["c"]
            else:
                if current_string != "":
                    new_array.append({"t": "Str", "c": current_string})
                    current_string = ""
                new_array.append(element)
                if isinstance(element, dict) and \
                        "c" in element:
                    self.squish(element["c"])
                elif isinstance(element, list):
                    self.squish(element)

        if current_string != "":
            new_array.append({"t": "Str", "c": current_string})

        del json_array[:]

        json_array.extend(new_array)
