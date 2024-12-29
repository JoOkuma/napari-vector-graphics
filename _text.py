import drawsvg as dw

from vispy.scene.visuals import Text


def text2svg(
    text_visual: Text,
    d: dw.Drawing | None,
) -> dw.Drawing | None:
    """
    Convert a vispy TextVisual to a drawsvg Drawing.

    If the TextVisual is not visible, the Drawing is not modified and
    it will return None if it was None.

    Parameters
    ----------
    text_visual : Text
        The vispy TextVisual to convert.
    d : dw.Drawing | None
        The drawsvg Drawing to append to. If None, a new Drawing is created.
    
    Returns
    -------
    d : dw.Drawing | None
        The drawsvg Drawing.
    """

    if not text_visual.visible:
        return d
    
    text_visual.update()

    text = text_visual.text
    color = text_visual.color.hex[0].upper()
    font_size = text_visual.font_size

    pos = text_visual.get_transform(
        map_from='visual', map_to='canvas'
    ).map(text_visual.pos)

    if d is None:
        d = dw.Drawing()
    
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
