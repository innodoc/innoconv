"""Project constants"""

import os


#: Default innoconv output directory
DEFAULT_OUTPUT_DIR_BASE = os.path.join('.', 'innoconv_output')

#: Default languages
DEFAULT_LANGUAGES = ('de', 'en')

#: Encoding used in this project
ENCODING = 'utf-8'

#: Content filename for a section folder
CONTENT_FILENAME = 'content.md'

#: Output content filename for a section folder
OUTPUT_CONTENT_FILENAME = 'content.json'

#: Manifest filename
MANIFEST_FILENAME = 'manifest.json'

#: TOC filename
TOC_FILENAME = 'toc.json'

#: Static Folder Name
STATIC_FOLDER = 'static'

#: Logo Filename
LICENSE_FOLDER = '_license'

#: Logo Filename
LICENSE_FILENAME = 'license'

#: Logo Filename
ABOUT_FOLDER = '_about'

#: Logo Filename
ABOUT_FILENAME = 'about'

#: Logo Filename
INSTITUTION_FOLDER = '_institution'

#: Logo Filename
INSTITUTION_FILENAME = 'institution'

#: Logo Filename
PAGES_FOLDER = '_pages'

#: Logo Filename
LOGO_FILENAME = 'logo.png'

#: Logo Filename
FAVICON_FILENAME = 'favicon.ico'

#: Logo Filename
GENERATE_PDF_FILENAME = 'generate_pdf'
