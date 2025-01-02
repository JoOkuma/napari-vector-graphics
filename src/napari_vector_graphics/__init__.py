try:
    from napari_vector_graphics._version import version as __version__
except ImportError:
    __version__ = "unknown"

from napari_vector_graphics._image import image2svg
from napari_vector_graphics._labels import labels2svg
from napari_vector_graphics._tracks import tracks2svg
from napari_vector_graphics._viewer import viewer2svg
from napari_vector_graphics._widget import NapariVectorGraphicsWidget

__all__ = [
    "image2svg",
    "labels2svg",
    "tracks2svg",
    "viewer2svg",
    "NapariVectorGraphicsWidget",
]
