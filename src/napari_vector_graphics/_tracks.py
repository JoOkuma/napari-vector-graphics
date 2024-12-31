import drawsvg as dw
import napari
import numpy as np
from napari._vispy.filters.tracks import TracksFilter
from napari._vispy.visuals.tracks import TracksVisual
from napari.layers import Tracks
from napari.viewer import current_viewer
from vispy.visuals.line import LineVisual

from napari_vector_graphics._text import text2svg
from napari_vector_graphics._utils import color2rgba


def _get_track_filter(line_visual: LineVisual) -> TracksFilter:
    filters = line_visual._subvisuals[0]._filters
    for f in filters:
        if isinstance(f, TracksFilter):
            return f
    raise ValueError(f"No 'TracksFilter' found in {filters}")


def tracks2svg(
    layer: Tracks,
    circle_radius: int = 0,
    d: dw.Drawing | dw.Group | None = None,
    viewer: napari.Viewer | None = None,
) -> dw.Drawing | dw.Group:
    """
    Convert a napari Tracks layer to a drawsvg Drawing.

    Parameters
    ----------
    layer : Tracks
        The napari Tracks layer to convert.
    circle_radius : int
        The radius of the circle to add at the current time of each visible track.
        This is an extra feature not present in default napari.
    d : dw.Drawing | None
        The drawsvg Drawing to append to. If None, a new Drawing is created.

    Returns
    -------
    d : dw.Drawing
        The drawsvg Drawing.
    """
    if viewer is None:
        viewer = current_viewer()

    node: TracksVisual = viewer.window._qt_viewer.canvas.layer_to_visual[
        layer
    ].node

    track_visual: LineVisual = node._subvisuals[0]
    track_visual.update()

    # Mapping to canvas coordinates
    data2canvas = track_visual.get_transform(
        map_from="visual", map_to="canvas"
    )
    canvas_data = data2canvas.map(track_visual._pos)
    pos = canvas_data[:, :2]

    # Find where the line stops/starts
    connex = track_visual._connect
    line_stops = np.where(~connex)[0] + 1

    # Computing opacity
    track_filter = _get_track_filter(track_visual)
    current_t = track_filter.current_time
    time = track_filter.vertex_time.ravel()
    # Replace _head_length with head_length after https://github.com/napari/napari/pull/7474 is merged
    opacity = (track_filter._head_length + current_t - time) / (
        track_filter.tail_length + track_filter._head_length
    )
    opacity = np.clip(1 - opacity, 0, 1)
    opacity[time > current_t + track_filter._head_length] = 0

    # Binary mask for adding circles
    if circle_radius > 0:
        add_circle = np.abs(time - track_filter.current_time) < 1.0
    else:
        add_circle = np.ones_like(opacity, dtype=bool)

    # Auxiliary structure for track IDs and graph
    track_ids = layer._manager.track_ids
    graph = layer._manager.graph if layer.display_graph else None

    if d is None:
        height, width = viewer._canvas_size
        d = dw.Drawing(width, height, id_prefix="tracks_")

    start = 0
    for stop in line_stops:
        g = None
        for i in range(start, stop - 1):

            # Discard invisible segments
            if opacity[i] < 1e-6:
                continue

            # Create a new group for each track
            if g is None:
                g = dw.Group(id=f"track_{track_ids[i]}")

            # Convert color to RGB
            # NOTE: unlike napari these aren't interpolated between vertices
            rgb_color = color2rgba(track_visual.color[i])

            # Add the line segment if visible
            # I don't really know why people would want to draw invisible lines
            if track_visual.visible:
                g.append(
                    dw.Line(
                        *pos[i],
                        *pos[i + 1],
                        stroke=rgb_color,
                        stroke_width=track_visual.width,
                        stroke_opacity=opacity[i],
                    )
                )

            # Add division if there is a graph
            if i == start and graph is not None:
                for parent_track_id in graph.get(track_ids[i], []):
                    p = layer._manager._vertex_indices_from_id(
                        parent_track_id
                    )[-1]
                    g.append(
                        dw.Line(
                            *pos[p],
                            *pos[i],
                            stroke=rgb_color,
                            stroke_width=track_visual.width,
                            stroke_opacity=opacity[i],
                        )
                    )

            # Add circle at the current time if requested
            if add_circle[i]:
                g.append(
                    dw.Circle(
                        *pos[i + 1],
                        r=circle_radius,
                        stroke=rgb_color,
                        stroke_width=track_visual.width,
                        stroke_opacity=opacity[i],
                        fill="none",
                    )
                )

        d.append(g)
        start = stop

    # Add text if visible
    if node._subvisuals[1].visible:
        d = text2svg(node._subvisuals[1], d)

    return d


def _main() -> None:
    # from tracks_3d_with_graph import viewer
    from tracks_3d import viewer

    layer: Tracks = viewer.layers["tracks"]

    layer.display_id = True
    layer.tail_length = 125
    viewer.dims.set_point(0, 300)

    d = tracks2svg(layer, circle_radius=10)

    d.save_svg("pic.svg")


if __name__ == "__main__":
    _main()
