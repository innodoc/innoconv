from click import BadOptionUsage

from innoconv.ext import EXTENSIONS


def parse_extensions(_, __, value):
    extensions = value.split(",")
    for ext in extensions:
        if ext not in EXTENSIONS.keys():
            raise BadOptionUsage("-e", "Extension not found: {}".format(ext))
    return extensions
