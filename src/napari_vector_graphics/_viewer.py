from contextlib import nullcontext
from typing import Literal

import drawsvg as dw
import napari
from napari.layers import Image, Labels, Tracks

from napari_vector_graphics._image import image2svg
from napari_vector_graphics._labels import labels2svg
from napari_vector_graphics._scaler_bar import scaler_bar2svg
from napari_vector_graphics._tracks import tracks2svg
from napari_vector_graphics._utils import fit_canvas_to_content

_LABELS_MODES = ("auto", "raster", "vector")


def viewer2svg(
    viewer: napari.Viewer,
    d: dw.Drawing | dw.Group | None = None,
    blend_images: bool = True,
    labels_mode: Literal["auto", "raster", "vector"] = "auto",
    fit_content: bool = False,
) -> dw.Drawing | dw.Group:
    """
    Convert a napari viewer to an SVG drawing.

    Parameters
    ----------
    viewer : napari.Viewer
        The napari viewer to convert.
    d : dw.Drawing | dw.Group | None
        The SVG drawing to append to. If None, a new drawing is created.
    blend_images : bool
        Whether to blend rasterized Image layers.
    labels_mode : {"auto", "raster", "vector"}
        The mode to render labels.
        - "auto": render as vector if 2D, else as raster.
        - "raster": render as raster.
        - "vector": render as vector if 2D otherwise error.
    fit_content : bool
        Whether to fit the canvas to the content.

    Returns
    -------
    dw.Drawing | dw.Group
        The SVG drawing.
    """
    if labels_mode not in _LABELS_MODES:
        raise ValueError(
            f"Invalid labels_mode {labels_mode}. Expected {_LABELS_MODES}."
        )

    if viewer.dims.ndisplay > 2:
        if labels_mode == "vector":
            raise ValueError(
                "Labels mode 'vector' is only available in 2D mode."
            )

        elif labels_mode == "auto":
            labels_mode = "raster"

    elif labels_mode == "auto":
        labels_mode = "vector"

    with fit_canvas_to_content(viewer) if fit_content else nullcontext():

        if d is None:
            height, width = viewer._canvas_size
            d = dw.Drawing(width, height, id_prefix="napari_")

        if blend_images:
            blending_layers = [
                layer
                for layer in viewer.layers
                if isinstance(layer, Image) and layer.visible
            ]
            image2svg(blending_layers, d=d, viewer=viewer)

        for layer in viewer.layers:
            if not layer.visible:
                continue

            if isinstance(layer, Image):
                if not blend_images:
                    d = image2svg(layer, d=d, viewer=viewer)

            elif isinstance(layer, Labels):
                if labels_mode == "raster":
                    d = image2svg(layer, d=d, viewer=viewer)

                elif labels_mode == "vector":
                    d = labels2svg(layer, d=d, viewer=viewer)

                else:
                    raise ValueError(
                        f"Expected labels_mode to be 'raster' or 'vector'. Found {labels_mode}."
                    )

            elif isinstance(layer, Tracks):
                d = tracks2svg(layer, d=d, viewer=viewer)

            else:
                raise ValueError(
                    f"Layer type {type(layer)} not supported yet. Disable the layer and try again."
                )

        if viewer.scale_bar.visible:
            scaler_bar2svg(viewer, d=d)

    return d


def _main() -> None:
    import napari
    from skimage.data import cells3d

    viewer = napari.Viewer()
    viewer.add_image(cells3d(), channel_axis=1)

    image = viewer.layers[1].data
    mask = image > image.mean()
    viewer.add_labels(mask).contour = 5

    viewer.scale_bar.visible = True

    d = viewer2svg(
        viewer,
        fit_content=True,
        blend_images=True,
    )
    # d.save_png("pic.png")
    d.save_svg("pic.svg")


if __name__ == "__main__":
    _main()
