"""
Extensions are a way of extending the functionality of innoConv in a modular
way. They can be enabled on a one-by-one basis.
"""

from innoconv.extensions.copy_static import CopyStatic
from innoconv.extensions.generate_toc import GenerateToc
from innoconv.extensions.join_strings import JoinStrings
from innoconv.extensions.write_manifest import WriteManifest
from innoconv.extensions.tikz2pdf import Tikz2Pdf

#: List of available extensions
EXTENSIONS = {
    'copy_static': CopyStatic,
    'generate_toc': GenerateToc,
    'join_strings': JoinStrings,
    'write_manifest': WriteManifest,
    'tikz2Pdf': Tikz2Pdf
}