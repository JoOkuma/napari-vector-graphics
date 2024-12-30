
from typing import Any, Generator
from contextlib import contextmanager

import napari
from vispy.color import ColorArray


def color2rgba(color: ColorArray) -> str:
    """
    Convert a vispy color to an SVG-compatible RGBA string.

    Parameters
    ----------
    color : ColorArray
        The vispy color to convert.

    Returns
    -------
    str
        The SVG-compatible RGBA string.
    """
    return "rgba({}, {}, {}, {})".format(*(color[:4] * 255))


@contextmanager
def hide_all(viewer: napari.Viewer, ignore: Any | tuple[Any]) -> Generator[None, None, None]:

    elements = {}

    if not isinstance(ignore, tuple):
        ignore = (ignore,)

    for l in viewer.layers:
        if l in ignore:
            continue
        elements[l] = l.visible
        l.visible = False
    
    for l in viewer._overlays.values():
        if l in ignore:
            continue
        elements[l] = l.visible
        l.visible = False
        
    yield
    
    for l, v in elements.items():
        l.visible = v
