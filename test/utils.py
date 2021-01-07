"""Convenience functions for generating AST structures."""


def get_empty_ica():
    """Create empty id, class, attributes info."""
    return ["", [], []]


def get_filler_content():
    """Create simple Str element."""
    return {"t": "Str", "c": "Lorem Ipsum"}


def get_bullet_list_ast():
    """Create BulletList element."""
    return {"t": "BulletList", "c": [[get_para_ast()], [get_para_ast()]]}


def get_definitionlist_ast():
    """Create DefinitionList element."""
    return {
        "t": "DefinitionList",
        "c": [
            [[get_filler_content()], [[get_para_ast()]]],
            [[get_filler_content()], [[get_para_ast()]]],
        ],
    }


def get_div_ast(content=None, classes=None, div_id=""):
    """Create Div element with content."""
    if content is None:
        content = [get_filler_content()]
    return {"t": "Div", "c": [[div_id, classes if classes else [], []], content]}


def get_question_ast(points="1"):
    """Create question element."""
    return {"t": "Span", "c": [["", ["question"], [["points", points]]], []]}


def get_exercise_ast(content=None, div_id="FOO_ID"):
    """Create exercise element with content."""
    if content is None:
        content = [get_question_ast("1")]
    return get_div_ast(content, classes="exercise", div_id=div_id)


def get_header_ast(content=None):
    """Create Header element with content."""
    if content is None:
        content = [get_filler_content()]
    return {"t": "Header", "c": [1, get_empty_ica(), content]}


def get_para_ast(content=None):
    """Create Para element with content."""
    if content is None:
        content = [get_filler_content()]
    return {"t": "Para", "c": content}


def get_image_ast(path, title="", description=""):
    """Create Image element."""
    return {
        "t": "Image",
        "c": [get_empty_ica(), [{"t": "Str", "c": title}], [path, description]],
    }


def get_plain_ast(content):
    """Create Plain element."""
    return {"t": "Plain", "c": [{"t": "Str", "c": content}]}


def get_table_cell_ast(content):
    """Create Table cell."""
    return [
        get_empty_ica(),
        {"t": "AlignDefault"},
        1,
        1,
        [get_plain_ast(content)],
    ]


def get_table_ast():
    """Create Table element."""
    return {
        "t": "Table",
        "c": [
            get_empty_ica(),
            [None, get_plain_ast("caption")],
            [
                [{"t": "AlignDefault"}, {"t": "ColWidthDefault"}],
                [{"t": "AlignDefault"}, {"t": "ColWidthDefault"}],
            ],
            # header
            [
                get_empty_ica(),
                [
                    [
                        get_empty_ica(),
                        [
                            get_table_cell_ast("H1"),
                            get_table_cell_ast("H2"),
                        ],
                    ],
                ],
            ],
            # body
            [
                [
                    get_empty_ica(),
                    0,
                    [],
                    # rows
                    [
                        [
                            get_empty_ica(),
                            # cols
                            [
                                get_table_cell_ast("A1"),
                                get_table_cell_ast("A2"),
                            ],
                        ],
                        [
                            get_empty_ica(),
                            # cols
                            [
                                get_table_cell_ast("B1"),
                                get_table_cell_ast("B2"),
                            ],
                        ],
                    ],
                ],
            ],
            # footer
            [get_empty_ica(), []],
        ],
    }


def get_ordered_list_ast():
    """Create OrderedList element."""
    return {
        "t": "OrderedList",
        "c": [
            [1, {"t": "Decimal"}, {"t": "Period"}],
            [[get_para_ast()], [get_para_ast()]],
        ],
    }


def get_video_ast(path, title=""):
    """Create Video element."""
    return get_generic_link_ast(
        [{"t": "Str", "c": title}], path, title, ["video", "video-static"]
    )


def get_youtube_ast(url, title=""):
    """Create YouTube video element."""
    return get_generic_link_ast(
        [{"t": "Str", "c": title}], url, title, ["video", "video-youtube"]
    )


def get_generic_link_ast(content, link, title="", classes=None):
    """Create generic link element."""
    if classes is None:
        classes = []
    return {"t": "Link", "c": [["", classes, []], content, [link, title]]}


def get_index_term(content, term):
    """Create an index term."""
    return {"t": "Span", "c": [["", [], [["data-index-term", term]]], content]}


def get_complex_ast():
    """Create a somewhat complex AST."""
    return [
        get_para_ast(),
        get_para_ast([get_image_ast("/present.png", "Image Present")]),
        get_para_ast([get_para_ast([get_image_ast("/subfolder/present.mp4")])]),
        get_para_ast(
            [
                get_para_ast(get_para_ast()),
                get_para_ast([get_filler_content()]),
                get_image_ast("/localizable.gif", "", "Description!"),
                get_image_ast("example_video.ogv"),
            ]
        ),
        get_image_ast("https://www.example.com/example.png"),
        get_para_ast(
            [
                get_generic_link_ast(
                    [get_image_ast("example_image.jpg")],
                    "http://www.tu-berlin.de",
                )
            ]
        ),
    ]
