"""Convenience functions for generating AST structures."""


def get_filler_content():
    """Create simple Str element."""
    return {"t": "Str", "c": "Lorem Ipsum"}


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
