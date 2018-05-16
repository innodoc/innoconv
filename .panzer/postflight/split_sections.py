#!/usr/bin/env python3
"""
Split JSON doc into separate files according to header structure.
"""
import os
import sys
import json
import re
from base64 import urlsafe_b64encode
from slugify import slugify

sys.path.append(os.path.join(os.environ['PANZER_SHARED'], 'python'))
try:
    import panzertools  # pylint: disable=import-error
except Exception:
    raise

MAX_LEVELS = 3


def concatenate_strings(elems):
    """Concatenate Str and Space elements into a string."""
    string = ''
    for elem in elems:
        if elem['t'] == 'Str':
            string += elem['c']
        elif elem['t'] == 'Space':
            string += ' '
    return string


def generate_id(content):
    """Generate ID from content. If there's no content, create random ID."""
    string = concatenate_strings(content)
    if not string:
        string = urlsafe_b64encode(os.urandom(6))
    return slugify(string)


def create_doc_tree(tree, level):
    """Generate section tree from a flat document structure."""
    sections = []
    section = {}
    await_header = True
    content = []
    children = []

    def create_section(sections, section, children):
        """Save a section."""
        if level <= MAX_LEVELS:
            subsections, subcontent = create_doc_tree(children, level + 1)
            if subsections:
                section['children'] = subsections
            if subcontent:
                section['content'] = subcontent
        elif children:
            section['content'] = children
        sections.append(section)

    for node in tree:
        if node['t'] == 'Header' and node['c'][0] == level:
            await_header = False
            if 'title' in section:
                create_section(sections, section, children)
                children = []
                section = {}
            section['title'] = node['c'][2]
            section_id = node['c'][1][0]
            # auto-generate section ID if necessary
            if not section_id:
                section_id = generate_id(section['title'])
            section['id'] = section_id
        else:
            if await_header:
                content.append(node)
            else:
                children.append(node)

    if 'title' in section:
        create_section(sections, section, children)

    return sections, content


def write_sections(sections, outdir_base):
    """Write sections to individual files and remove content from TOC tree."""

    def write_section(section, outdir, depth):
        """Write a single section to a JSON file."""
        if depth > MAX_LEVELS:
            return
        outdir_section = os.path.join(outdir, section['id'])
        os.makedirs(outdir_section, exist_ok=True)
        if 'content' in section:
            filename = os.path.join(outdir_section, 'content.json')
            with open(filename, 'w') as sfile:
                json.dump(section['content'], sfile)
            del section['content']
        try:
            for subsection in section['children']:
                write_section(subsection, outdir_section, depth + 1)
        except KeyError:
            pass

    for section in sections:
        write_section(section, outdir_base, 1)

    return sections


def print_sections(sections):
    """Debug print TOC tree."""

    def print_section(section, depth):
        """Print a single section."""
        if depth > MAX_LEVELS:
            return
        title = concatenate_strings(section['title'])
        indent = ' ' * depth
        msg = '{}{} ({})'.format(indent, title, section['id'])
        panzertools.log('INFO', msg)
        try:
            for subsection in section['children']:
                print_section(subsection, depth + 1)
        except KeyError:
            pass

    panzertools.log('INFO', 'TOC TREE:')
    for section in sections:
        print_section(section, 1)


def main(debug=False):
    """main entry point"""
    options = panzertools.read_options()
    filepath = options['pandoc']['output']

    if options['pandoc']['write'] != 'json':
        panzertools.log(
            'WARNING', 'skipping split_sections for non-json output')

    # extract lang
    lang = None
    for key in options['pandoc']['options']['r']['metadata']:
        match = re.match(r'^lang:([a-z]{2})$', key[0])
        if match:
            lang = match.group(1)
    if not lang:
        raise RuntimeError('Error: Unable to extract lang key from metadata!')

    # load pandoc output
    with open(filepath, 'r') as doc_file:
        doc = json.load(doc_file)

    # extract sections from headers
    sections, _ = create_doc_tree(doc['blocks'], level=1)
    panzertools.log('INFO', 'Extracted table of contents.')

    # output directory
    outdir = os.path.normpath(os.path.dirname(filepath))
    if os.path.basename(outdir) != lang:  # append lang if necessary
        outdir = os.path.join(outdir, lang)
    os.makedirs(outdir, exist_ok=True)

    # write sections to file
    sections = write_sections(sections, outdir)

    # write metadata toc file
    tocpath = os.path.join(outdir, 'toc.json')
    with open(tocpath, 'w') as toc_file:
        json.dump(sections, toc_file)
    panzertools.log('INFO', 'Wrote: {}'.format(tocpath))

    # print toc tree
    if debug:
        print_sections(sections)

    # removing pandoc output file
    os.unlink(filepath)
    panzertools.log(
        'INFO', 'Removed original pandoc output: {}'.format(filepath))


if __name__ == '__main__':
    main(debug=True if os.environ.get('INNOCONV_DEBUG') else False)
