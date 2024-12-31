import warnings

import drawsvg as dw
import napari
import numpy as np
from napari.layers import Labels
from napari.viewer import current_viewer
from skimage.measure import regionprops
from tqdm import tqdm

from napari_vector_graphics._utils import color2rgba, hide_all


def labels2svg(
    layer: Labels,
    d: dw.Drawing | dw.Group | None = None,
    viewer: napari.Viewer | None = None,
) -> dw.Drawing | dw.Group | None:
    """
    Convert a napari Labels layer to a drawsvg Drawing.

    Parameters
    ----------
    layer : Labels
        The napari Labels layer to convert.
    d : dw.Drawing | dw.Group | None
        The drawsvg Drawing to append to. If None, a new Drawing is created.
    viewer : napari.Viewer | None
        The napari viewer to convert from.

    Returns
    -------
    d : dw.Drawing
        The drawsvg Drawing.
    """
    warnings.warn(
        "The resulting segments from this function are simplified, adjust `dp_epsilon` to change the level of simplification."
        "Set to 0 to disable simplification.",
        category=UserWarning,
        stacklevel=2,
    )

    warnings.warn(
        "This function fills holes in the labels.",
        category=UserWarning,
        stacklevel=2,
    )

    warnings.warn(
        "This removes segments with less than 3 points.",
        category=UserWarning,
        stacklevel=2,
    )

    try:
        import cv2

    except ImportError as e:
        raise ImportError(
            "The 'opencv' package is required to convert labels to SVG."
            "You can install it with 'pip install opencv-python-headless'."
        ) from e

    if viewer is None:
        viewer = current_viewer()

    if d is None:
        height, width = viewer._canvas_size
        d = dw.Drawing(width, height, id_prefix="labels_")

    prev_contour = layer.contour
    layer.contour = 0

    with hide_all(viewer, layer):
        rgb_image = viewer.window._qt_viewer.canvas._scene_canvas.render(
            bgcolor="transparent"
        )

    layer.contour = prev_contour

    label_image = (rgb_image[..., :3] * (np.arange(3) * 256)).sum(axis=-1)

    fill_ctr = prev_contour == 0
    width = max(1, prev_contour)

    for props in tqdm(
        regionprops(label_image), "Converting labels to polygons"
    ):
        mask: np.ndarray = props.image
        contours, _ = cv2.findContours(
            mask.astype(np.uint8),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
            offset=(props.bbox[1], props.bbox[0]),
        )
        color = color2rgba(
            rgb_image[props.coords[0, 0], props.coords[0, 1]], factor=1
        )
        stroke_color = color if not fill_ctr else "none"
        fill_color = color if fill_ctr else "none"

        for ctr in contours:
            ctr = ctr.squeeze(axis=1).ravel() + 0.5  # pixel center

            d.append(
                dw.Lines(
                    *ctr,
                    fill=fill_color,
                    stroke=stroke_color,
                    stroke_width=layer.contour,
                    close=True,
                    stroke_opacity=layer.opacity,
                    fill_opacity=layer.opacity,
                    stroke_linejoin="bevel",
                )
            )

    return d
