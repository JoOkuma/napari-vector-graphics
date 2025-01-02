from pathlib import Path
from typing import TYPE_CHECKING, Callable

from skimage.data import cells3d

from napari_vector_graphics import viewer2svg

if TYPE_CHECKING:
    import napari


def test_viewer2svg(
    make_napari_viewer: Callable[..., "napari.Viewer"],
    tmp_path: Path,
) -> None:

    viewer = make_napari_viewer()
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
    d.save_svg(tmp_path / "pic.svg")
