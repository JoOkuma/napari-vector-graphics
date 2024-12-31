import tempfile
from typing import Sequence

import drawsvg as dw
import imageio
import napari
from napari.layers import Image, Labels
from napari.viewer import current_viewer

from napari_vector_graphics._utils import hide_all


def image2svg(
    layers: Image | Labels | Sequence[Image | Labels],
    d: dw.Drawing | dw.Group | None = None,
    viewer: napari.Viewer | None = None,
) -> dw.Drawing | dw.Group | None:
    """
    Convert a napari image layer to an SVG drawing.

    Parameters
    ----------
    layers : Image | Labels | Sequence[Image | Labels]
        The image layer(s) to convert.
        All images from the sequence are blended together.
    d : dw.Drawing | dw.Group | None
        The SVG drawing to append to. If None, a new drawing is created.
    viewer : napari.Viewer | None
        The napari viewer to convert from.

    Returns
    -------
    dw.Drawing | dw.Group | None
        The SVG drawing.
    """

    if viewer is None:
        viewer = current_viewer()

    if d is None:
        height, width = viewer._canvas_size
        d = dw.Drawing(width, height, id_prefix="image_")

    with hide_all(viewer, layers):
        image = viewer.window._qt_viewer.canvas._scene_canvas.render(
            bgcolor="transparent"
        )

    with tempfile.NamedTemporaryFile(suffix=".png") as f:
        imageio.imwrite(f.name, image)
        d.append(
            dw.Image(
                0,
                0,
                width=image.shape[1],
                height=image.shape[0],
                path=f.name,
                embed=True,
            )
        )

    return d


def _main() -> None:
    import napari
    from skimage.data import cells3d

    viewer = napari.Viewer()
    viewer.add_image(cells3d(), channel_axis=1)

    viewer.dims.ndisplay = 3
    viewer.camera.angles = (15, -30, 145)

    d = image2svg(viewer.layers[0])
    d.save_svg("image.svg")

    napari.run()


if __name__ == "__main__":
    _main()
