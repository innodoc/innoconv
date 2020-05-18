"""
innoConv extensions.

Extensions are a way of separating concerns of the conversion process into
independent modules. They can be enabled on a one-by-one basis as not all
features are needed in all cases.

Extensions interface with
:class:`InnoconvRunner <innoconv.runner.InnoconvRunner>` through a set of
methods defined in
:class:`AbstractExtension <innoconv.ext.abstract.AbstractExtension>`.
"""

from innoconv.ext.copy_static import CopyStatic
from innoconv.ext.generate_toc import GenerateToc
from innoconv.ext.index_terms import IndexTerms
from innoconv.ext.join_strings import JoinStrings
from innoconv.ext.number_boxes import NumberBoxes
from innoconv.ext.tikz2svg import Tikz2Svg
from innoconv.ext.write_manifest import WriteManifest

#: List of available extensions
EXTENSIONS = {
    "copy_static": CopyStatic,
    "generate_toc": GenerateToc,
    "index_terms": IndexTerms,
    "join_strings": JoinStrings,
    "number_boxes": NumberBoxes,
    "tikz2svg": Tikz2Svg,
    "write_manifest": WriteManifest,
}
