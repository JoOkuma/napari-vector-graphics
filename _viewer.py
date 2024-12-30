
from contextlib import nullcontext

import drawsvg as dw
import napari

from napari.layers import Image, Tracks

from _image import image2svg
from _tracks import tracks2svg
from _scaler_bar import scaler_bar2svg
from _utils import fit_canvas_to_content


def viewer2svg(
    viewer: napari.Viewer,
    d: dw.Drawing | dw.Group | None = None,
    blend_rasterized: bool = True,
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
    blend_rasterized : bool
        Whether to blend rasterized layers (Image, Labels).
    fit_content : bool
        Whether to fit the canvas to the content.

    Returns
    -------
    dw.Drawing | dw.Group
        The SVG drawing.
    """

    with fit_canvas_to_content(viewer) if fit_content else nullcontext():

        if d is None:
            height, width = viewer._canvas_size
            d = dw.Drawing(width, height, id_prefix="napari_")
        
        if blend_rasterized:
            blending_layers = [
                l for l in viewer.layers if isinstance(l, Image) and l.visible
            ]
            image2svg(blending_layers, d=d, viewer=viewer)

        for layer in viewer.layers:
            if not layer.visible:
                continue

            if isinstance(layer, Image):
                if not blend_rasterized:
                    d = image2svg(layer, d=d, viewer=viewer)

            elif isinstance(layer, Tracks):
                d = tracks2svg(layer, d=d, viewer=viewer)

            else:
                raise ValueError(f"Layer type {type(layer)} not supported yet.")

        if viewer.scale_bar.visible:
            scaler_bar2svg(viewer, d=d)

    return d


def _main() -> None:
    import napari
    from skimage.data import cells3d

    viewer = napari.Viewer()
    viewer.add_image(cells3d(), channel_axis=1)

    viewer.scale_bar.visible = True

    d = viewer2svg(viewer, fit_content=True)
    d.save_png("pic.png")


if __name__ == "__main__":
    _main()