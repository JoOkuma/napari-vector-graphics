from pathlib import Path
from typing import TYPE_CHECKING, Callable

import numpy as np

from napari_vector_graphics import tracks2svg

if TYPE_CHECKING:
    import napari


def _circle(r, theta):
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y


def tracks_3d_merge_split():
    """
    Create tracks with splitting and merging.
    FROM: https://github.com/napari/napari/blob/main/examples/tracks_3d_with_graph.py
    """
    timestamps = np.arange(300)

    def _trajectory(t, r, track_id):
        theta = t * 0.1
        x, y = _circle(r, theta)
        z = np.zeros(x.shape)
        tid = np.ones(x.shape) * track_id
        return np.stack([tid, t, z, y, x], axis=1)

    trackA = _trajectory(timestamps[:100], 30.0, 0)
    trackB = _trajectory(timestamps[100:200], 10.0, 1)
    trackC = _trajectory(timestamps[100:200], 50.0, 2)
    trackD = _trajectory(timestamps[200:], 30.0, 3)

    data = [trackA, trackB, trackC, trackD]
    tracks = np.concatenate(data, axis=0)
    tracks[:, 2:] += 50.0  # centre the track at (50, 50, 50)

    graph = {1: 0, 2: [0], 3: [1, 2]}

    features = {"time": tracks[:, 1]}

    return tracks, features, graph


def test_tracks2svg(
    make_napari_viewer: Callable[..., "napari.Viewer"],
    tmp_path: Path,
) -> None:

    tracks, features, graph = tracks_3d_merge_split()

    viewer = make_napari_viewer()
    viewer.add_tracks(tracks, features=features, graph=graph, name="tracks")

    layer = viewer.layers["tracks"]

    layer.display_id = True
    layer.tail_length = 125
    viewer.dims.set_point(0, 300)

    d = tracks2svg(layer, circle_radius=10)

    d.save_svg(tmp_path / "pic.svg")
