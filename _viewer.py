
import drawsvg as dw
import napari

from napari.layers import Image, Tracks

from _image import image2svg
from _tracks import tracks2svg
from _scaler_bar import scaler_bar2svg

# TODO:
# - iterate through layres
# - create scale bar as SVG object

def viewer2svg(
    viewer: napari.Viewer,
    d: dw.Drawing | dw.Group | None = None,
    fit_content: bool = False,
) -> dw.Drawing | dw.Group:

    if fit_content:
        raise NotImplementedError("`fit_content` is not implemented yet.")

    if d is None:
        height, width = viewer._canvas_size
        d = dw.Drawing(width, height, id_prefix="napari_")
    
    for layer in viewer.layers:
        if layer.visible is False:
            continue

        if isinstance(layer, Image):
            d = image2svg(layer, dw=d, viewer=viewer)

        elif isinstance(layer, Tracks):
            d = tracks2svg(layer, dw=d, viewer=viewer)
        
        else:
            raise ValueError(f"Layer type {type(layer)} not supported yet.")
        
    if viewer.scale_bar.visible:
        scaler_bar2svg(viewer, d=d)
        
    return d


def _main() -> None:
    import napari

    viewer = napari.Viewer()
    viewer.scale_bar.visible = True

    d = viewer2svg(viewer)
    d.save_svg("napari.svg")


if __name__ == "__main__":
    _main()
