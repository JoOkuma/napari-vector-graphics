import drawsvg as dw
import numpy as np

from vispy.scene.visuals import Line


def line2svg(
    line_visual: Line,
    d: dw.Drawing | dw.Group | None,
) -> dw.Drawing | dw.Group | None:
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
    return d
    # TODO: Implement this function

    if not line_visual.visible:
        return d
    
    line_visual.update()

    text = line_visual.text
    color = line_visual.color.hex[0]
    font_size = line_visual.font_size

    pos = line_visual.get_transform(
        map_from='visual', map_to='canvas'
    ).map(line_visual.pos)

    if d is None:
        d = dw.Drawing()
    
    if isinstance(text, str):
        text = [text]
        pos = np.atleast_2d(pos)

    for i in range(len(text)):
        d.append(
            dw.Text(
                text[i],
                font_size,
                x=pos[i, 0],
                y=pos[i, 1],
                stroke=color,
            )
        )

    return d
