import drawsvg as dw
import napari
from napari._vispy.visuals.bounding_box import BoundingBox
from napari.layers import Layer
from napari.viewer import current_viewer

from napari_vector_graphics._line import line2svg


def bounding_box2svg(
    layer: Layer,
    viewer: napari.Viewer | None,
    d: dw.Drawing | dw.Group,
) -> dw.Drawing | dw.Group:

    if not layer.visible:
        raise ValueError(
            "Bounding box is not visible. `viewer.bounding_box.visible` must be True."
        )

    if viewer is None:
        viewer = current_viewer()

    try:
        bbox: BoundingBox = (
            viewer.window._qt_viewer.canvas._layer_overlay_to_visual[layer][
                layer.bounding_box
            ].node
        )
    except Exception as e:
        raise ValueError(
            "Must have napari>=0.6.2 installed to used bounding boxes vector graphics."
        ) from e

    bbox.update()

    d = line2svg(bbox.lines, d=d)

    return d
