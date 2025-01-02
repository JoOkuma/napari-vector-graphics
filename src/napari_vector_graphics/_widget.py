from typing import TYPE_CHECKING

from qtpy.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from napari_vector_graphics._viewer import viewer2svg

if TYPE_CHECKING:
    import napari


class NapariVectorGraphicsWidget(QWidget):
    def __init__(
        self, viewer: "napari.viewer.Viewer", parent: QWidget | None = None
    ):
        super().__init__(parent)

        self._viewer = viewer

        self._layout = QVBoxLayout(self)
        self.setLayout(self._layout)

        self._main_label = QLabel("Vector Graphics Export Options", self)
        self._layout.addWidget(self._main_label)

        self._blend_imgs_checkbox = QCheckBox("Blend images", self)
        self._blend_imgs_checkbox.setToolTip(
            "Blend images together before exporting."
            "Otherwise, napari blending won't be applied and they will be different svg elements."
        )
        self._blend_imgs_checkbox.setChecked(True)
        self._layout.addWidget(self._blend_imgs_checkbox)

        self._combobox_label = QLabel("Labels rendering mode:", self)
        self._layout.addWidget(self._combobox_label)

        self._labels_mode_combobox = QComboBox(self)
        self._labels_mode_combobox.addItems(["auto", "raster", "vector"])
        self._labels_mode_combobox.setToolTip(
            "Choose how to export labels.\n"
            "- 'auto': render as vector if 2D, else as raster.\n"
            "- 'raster': render as raster.\n"
            "- 'vector': render as vector (polygon), 2D only."
        )
        self._layout.addWidget(self._labels_mode_combobox)

        self._fit_content_checkbox = QCheckBox("Fit content", self)
        self._fit_content_checkbox.setChecked(True)
        self._fit_content_checkbox.setToolTip(
            "Fit napari viewer to the exported content."
            "This removes the empty borders."
        )
        self._layout.addWidget(self._fit_content_checkbox)

        self._export_btn = QPushButton("Export", self)
        self._export_btn.setToolTip("Export the napari viewer to an SVG file.")
        self._export_btn.clicked.connect(self._open_file_dialog)
        self._layout.addWidget(self._export_btn)

    def _open_file_dialog(self) -> None:
        # Open a save file dialog
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            parent=self,
            caption="Save File As",
            directory="",
            filter="SVG Files (*.svg)",
            options=options,
        )

        if file_path:
            d = viewer2svg(
                viewer=self._viewer,
                blend_images=self._blend_imgs_checkbox.isChecked(),
                labels_mode=self._labels_mode_combobox.currentText(),
                fit_content=self._fit_content_checkbox.isChecked(),
            )
            d.save_svg(file_path)


if __name__ == "__main__":
    import napari
    from qtpy.QtWidgets import QApplication

    viewer = napari.Viewer()
    app = QApplication([])

    widget = NapariVectorGraphicsWidget(viewer)
    viewer.window.add_dock_widget(widget, area="right")

    napari.run()
