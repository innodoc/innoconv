"""
Extensions are a way of extending the functionality of innoConv in a modular
way. They can be enabled on a one-by-one basis.
"""

from innoconv.extensions.copystatic import CopyStatic
from innoconv.extensions.join_strings import JoinStrings
from innoconv.extensions.tikz2pdf import Tikz2Pdf

#: List of available extensions
EXTENSIONS = {
    'copystatic': CopyStatic,
    'join_strings': JoinStrings,
    'tikz2pdf': Tikz2Pdf
}
