"""
Extensions are a way of extending the functionality of innoConv in a modular
way. They can be enabled on a one-by-one basis.
"""

from innoconv.extensions.copystatic import CopyStatic
from innoconv.extensions.join_strings import JoinStrings

#: List of available extensions
EXTENSIONS = {
    'copystatic': CopyStatic,
    'join_strings': JoinStrings
}
