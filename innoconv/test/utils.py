"""Convenience functions for generating AST structures."""

# pylint: disable=missing-docstring

from innoconv.manifest import Manifest


def get_filler_content():
    return {
        't': 'Str',
        'c': 'Lorem Ipsum'
    }


def get_para_ast(content=None):
    if content is None:
        content = [
            get_filler_content()
        ]
    return {
        't': 'Para',
        'c': content
    }


def get_image_ast(path, title='', description=''):
    return {
        't': 'Image',
        'c': [
            [
                '',
                [],
                []
            ],
            [
                {
                    't': 'Str',
                    'c': title
                }
            ],
            [
                path,
                description
            ]
        ]
    }


def get_video_ast(path, title=''):
    return get_generic_link_ast([
        {
            't': 'Str',
            'c': title
        }
    ], path, title, [
        'video',
        'video-static'
    ])


def get_youtube_ast(url, title=''):
    return get_generic_link_ast([
        {
            't': 'Str',
            'c': title
        }
    ], url, title, [
        'video',
        'video-youtube'
    ])


def get_generic_link_ast(content, link, title='', classes=None):
    if classes is None:
        classes = []
    return {
        't': 'Link',
        'c': [
            [
                '',
                classes,
                []
            ],
            content,
            [
                link,
                title
            ]
        ]
    }


def get_tricky_ast_parts():
    # Collection of simple special cases found in actual conversions
    return (
        [0, 1, 2],
        [{'t': 'InlineMath'}, '\\frac12>\\frac23']
    )


def get_manifest():
    return Manifest({
        'title': {
            'en': 'Foo Course Title',
        },
        'languages': ('en', ),
    })
