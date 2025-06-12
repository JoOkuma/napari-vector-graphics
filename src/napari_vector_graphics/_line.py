import drawsvg as dw
import numpy as np
from vispy.scene.visuals import Line

from napari_vector_graphics._utils import color2rgba


def line2svg(
    line_visual: Line,
    d: dw.Drawing | dw.Group,
) -> dw.Drawing | dw.Group:
    """
    Convert a vispy LineVisual to a drawsvg Drawing.

    If the LineVisual is not visible, the Drawing is not modified and
    it will return None if it was None.

    Parameters
    ----------
    line_visual : Line
        The vispy LineVisual to convert.
    d : dw.Drawing | dw.Group | None
        The drawsvg Drawing to append to. If None, a new Drawing is created.

    Returns
    -------
    d : dw.Drawing | dw.Group | None
        The drawsvg Drawing or Group.
    """
    if not line_visual.visible:
        return d

    if (
        isinstance(line_visual.connect, str)
        and line_visual.connect != "segments"
    ):
        raise NotImplementedError(
            f"Only 'segments' and `np.ndarray` connection is supported, got {line_visual.connect}."
        )

    line_visual.update()

    pos = line_visual.get_transform(map_from="visual", map_to="canvas").map(
        line_visual.pos
    )

    if pos.ndim == 1:
        pos = np.atleast_2d(pos)

    pos = pos[:, :2]

    if isinstance(line_visual.connect, str):
        for i in range(0, len(pos), 2):
            d.append(
                dw.Line(
                    *pos[i],
                    *pos[i + 1],
                    stroke=color2rgba(line_visual.color),
                    stroke_width=line_visual.width,
                )
            )
    else:
        for i, j in line_visual.connect:
            d.append(
                dw.Line(
                    *pos[i],
                    *pos[j],
                    stroke=color2rgba(line_visual.color),
                    stroke_width=line_visual.width,
                )
            )

    return d
