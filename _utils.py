
from typing import Any, Generator, Sequence
from contextlib import contextmanager

import napari
import numpy as np

from napari.layers import Layer
from vispy.color import ColorArray


def color2rgba(color: ColorArray | np.ndarray, factor: int = 255) -> str:
    """
    Convert a vispy color to an SVG-compatible RGBA string.

    Parameters
    ----------
    color : ColorArray | np.ndarray
        The vispy or array color to convert.
    factor : int
        The factor to multiply the color values by.

    Returns
    -------
    str
        The SVG-compatible RGBA string.
    """
    return "rgba({}, {}, {}, {})".format(*(color[:4] * factor))


@contextmanager
def hide_all(viewer: napari.Viewer, ignore: Any | Sequence[Any]) -> Generator[None, None, None]:

    elements = {}

    if isinstance(ignore, Layer):
        ignore = {ignore}
    else:
        ignore = set(ignore)

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


@contextmanager
def fit_canvas_to_content(viewer: napari.Viewer) -> Generator[None, None, None]:
    """
    Fit the canvas to the content of a napari viewer.

    Modified from: https://github.com/napari/napari/blob/main/napari/_qt/qt_main_window.py#L1660

    Parameters
    ----------
    viewer : napari.Viewer
        The napari viewer to fit the canvas to the content.
    """
    ndisplay = viewer.dims.ndisplay
    if ndisplay > 2:
        raise ValueError("Fit content is only available in 2D mode.")

    prev_size = viewer.window._qt_viewer.canvas.size
    prev_zoom = viewer.camera.zoom
    prev_center = viewer.camera.center

    extent_world = viewer.layers.extent.world[1][
        -ndisplay:
    ]
    extent_step = min(
        viewer.layers.extent.step[-ndisplay:]
    )
    size = extent_world / extent_step + 1
    size = np.asarray(size) / viewer.window._qt_window.devicePixelRatio()

    viewer.window._qt_viewer.canvas.size = size.astype(int)
    viewer.reset_view(margin=0)

    yield

    viewer.window._qt_viewer.canvas.size = prev_size
    viewer.camera.zoom = prev_zoom
    viewer.camera.center = prev_center
