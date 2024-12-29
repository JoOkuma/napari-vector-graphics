
import numpy as np
import drawsvg as dw

from tracks_3d import viewer

from napari.layers import Tracks
from napari._vispy.filters.tracks import TracksFilter
from vispy.visuals.line import LineVisual

from napari.viewer import current_viewer


def _get_track_filter(line_visual: LineVisual) -> TracksFilter:
    filters = line_visual._subvisuals[0]._filters
    for f in filters:
        if isinstance(f, TracksFilter):
            return f
    raise ValueError(f"No 'TracksFilter' found in {filters}")


def tracks2svg(layer: Tracks) -> dw.Drawing:

    viewer = current_viewer()

    track_visual: LineVisual = viewer.window._qt_viewer.canvas.layer_to_visual[layer].node._subvisuals[0]
    track_visual.update()

    data2canvas = track_visual.get_transform(
        map_from='visual', map_to='canvas'
    )

    canvas_data = data2canvas.map(track_visual._pos)
    pos = canvas_data[:, :2]

    connex = track_visual._connect
    line_stops = np.where(~connex)[0] + 1

    track_filter = _get_track_filter(track_visual)
    current_t = track_filter.current_time
    time = track_filter.vertex_time.ravel()
    opacity = (track_filter.head_length + current_t - time) / (
        track_filter.tail_length + track_filter.head_length
    )
    opacity = np.clip(1 - opacity, 0, 1)
    opacity[time > current_t] = 0

    height, width = viewer._canvas_size

    track_ids = layer._manager.track_ids

    d = dw.Drawing(width, height, id_prefix="tracks_")

    start = 0
    for stop in line_stops:
        g = None
        for i in range(start, stop - 1):
            if opacity[i] < 1e-6:
                continue
            if g is None:
                g = dw.Group(id=f"track_{track_ids[i]}")

            rgb_color = "rgb({}, {}, {})".format(
                *(track_visual.color[start, :3] * 255)
            )
            g.append(
                dw.Line(
                    *pos[i],
                    *pos[i + 1],
                    stroke=rgb_color,
                    stroke_width=track_visual.width,
                    stroke_opacity=opacity[i],
                )
            )
        d.append(g)
        start = stop

    return d


def main() -> None:

    layer = viewer.layers['tracks']

    d = tracks2svg(layer)

    d.save_svg('pic.svg')
    import napari
    napari.run()


if __name__ == '__main__':
    main()
