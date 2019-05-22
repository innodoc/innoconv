"""Convenience functions for generating AST structures."""


def get_filler_content():
    """Create simple Str element."""
    return {"t": "Str", "c": "Lorem Ipsum"}


def get_bullet_list_ast():
    """Create BulletList element."""
    return {"t": "BulletList", "c": [[get_para_ast()], [get_para_ast()]]}


def get_div_ast(content=None):
    """Create Div element with content."""
    if content is None:
        content = [get_filler_content()]
    return {"t": "Div", "c": [["", [], []], content]}


def get_header_ast(content=None):
    """Create Header element with content."""
    if content is None:
        content = [get_filler_content()]
    return {"t": "Header", "c": [1, ["", [], []], content]}


def get_para_ast(content=None):
    """Create Para element with content."""
    if content is None:
        content = [get_filler_content()]
    return {"t": "Para", "c": content}


def get_image_ast(path, title="", description=""):
    """Create Image element."""
    return {
        "t": "Image",
        "c": [["", [], []], [{"t": "Str", "c": title}], [path, description]],
    }


def get_table_ast():
    """Create Table element."""
    return {
        "t": "Table",
        "c": [
            [],
            [{"t": "AlignDefault"}, {"t": "AlignDefault"}],
            [0, 0],
            [[get_para_ast()], [get_para_ast()]],
            [
                [[get_para_ast()], [get_para_ast()]],
                [[get_para_ast()], [get_para_ast()]],
            ],
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
