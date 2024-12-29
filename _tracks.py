
import napari
import numpy as np
import drawsvg as dw

from tracks_3d import viewer

from napari._vispy.visuals.tracks import TracksVisual
from vispy.visuals.line import LineVisual


def main() -> None:

    layer = viewer.layers['tracks']

    data = layer.data
    node: LineVisual = viewer.window._qt_viewer.canvas.layer_to_visual[layer].node._subvisuals[0]
    node.update()

    data2canvas = node.get_transform(
        map_from='visual', map_to='canvas'
    )

    canvas_data = data2canvas.map(node._pos)
    pos = np.flip(canvas_data[:, :2], axis=1).copy()

    connex = node._connect
    line_stops = np.where(~connex)[0] + 1

    print(node.color[:, -1].max())
    print(node.color[:, -1].min())

    width, height = pos.max(axis=0)

    d = dw.Drawing(width, height)

    start = 0
    for stop in line_stops:
        rgb_color = "rgb({}, {}, {})".format(
            *(node.color[start, :3] * 255)
        )
        path = dw.Path(
            fill='none',
            stroke=rgb_color,
            stroke_width=node.width,
        )
        path.M(*pos[start])
        for p in pos[start + 1:stop]:
            path.L(*p)
        d.append(path)
        start = stop

    d.save_svg('pic.svg')
    return

    print(data.shape)
    print(canvas_data)
    viewer.add_points(canvas_data[:, :-2], size=5, name='canvas')

    napari.run()
    pass


if __name__ == '__main__':
    main()
