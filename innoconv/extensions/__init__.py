"""
innoConv extensions.

Extensions are a way of separating concerns of the conversion process into
independent modules. They can be enabled on a one-by-one basis as not all
features are needed in all cases.

Extensions interface with
:class:`InnoconvRunner <innoconv.runner.InnoconvRunner>` through a set of
methods defined in
:class:`AbstractExtension <innoconv.extensions.abstract.AbstractExtension>`.
"""

from innoconv.extensions.copy_static import CopyStatic
from innoconv.extensions.generate_toc import GenerateToc
from innoconv.extensions.join_strings import JoinStrings
from innoconv.extensions.write_manifest import WriteManifest

#: List of available extensions
EXTENSIONS = {
    "copy_static": CopyStatic,
    "generate_toc": GenerateToc,
    "join_strings": JoinStrings,
    "write_manifest": WriteManifest,
}
