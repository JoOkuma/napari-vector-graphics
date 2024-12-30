import drawsvg as dw
import napari

from napari._vispy.visuals.scale_bar import ScaleBar
from napari.viewer import current_viewer

from _text import text2svg


def scaler_bar2svg(
    viewer: napari.Viewer | None,
    d: dw.Drawing | dw.Group,
) -> dw.Drawing | dw.Group:

    if not viewer.scale_bar.visible:
        raise ValueError("Scale bar is not visible. `viewer.scale_bar.visible` must be True.")

    if viewer is None:
        viewer = current_viewer()
    
    scale_bar: ScaleBar = viewer.window.qt_viewer.canvas._overlay_to_visual[viewer.scale_bar].node
    scale_bar.update()

    text2svg(scale_bar._subvisuals[1], d=d)

