import drawsvg as dw
import tempfile
import imageio
from typing import Sequence

import napari
from napari.layers import Labels
from napari.viewer import current_viewer

from _utils import hide_all

def labels2svg(
    layer: Labels,
    d: dw.Drawing | dw.Group | None = None,
    viewer: napari.Viewer | None = None,
) -> dw.Drawing | dw.Group | None:
    raise NotImplementedError

    if viewer is None:
        viewer = current_viewer()

    if d is None:
        height, width = viewer._canvas_size
        d = dw.Drawing(width, height, id_prefix="image_")
    
    with hide_all(viewer, layer):
        image = viewer.window._qt_viewer.canvas._scene_canvas.render(bgcolor="transparent")

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

    d = labels2svg(viewer.layers[0])
    d.save_svg("image.svg")

    napari.run()


if __name__ == '__main__':
    _main()