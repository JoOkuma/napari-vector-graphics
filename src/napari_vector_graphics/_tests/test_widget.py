from unittest.mock import MagicMock, patch

from qtpy.QtCore import Qt

from napari_vector_graphics._widget import NapariVectorGraphicsWidget


def test_export_svg(qtbot, make_napari_viewer) -> None:
    """
    This test ensures:
    1) The file dialog is opened (mocked).
    2) viewer2svg is called with the correct arguments.
    3) The final .save_svg call uses the returned file path.
    """
    # 1) Create a napari viewer using the fixture
    viewer = make_napari_viewer()

    # 2) Instantiate your widget
    widget = NapariVectorGraphicsWidget(viewer=viewer)
    qtbot.addWidget(widget)

    # 3) Patch 'QFileDialog.getSaveFileName' so it does not open a real dialog
    #    and patch 'viewer2svg' so we can assert calls without doing real I/O.
    with patch(
        "napari_vector_graphics._widget.QFileDialog.getSaveFileName",
        return_value=("test_output.svg", "SVG Files (*.svg)"),
    ) as mock_dialog, patch(
        "napari_vector_graphics._widget.viewer2svg"
    ) as mock_viewer2svg:

        # viewer2svg returns some object with a .save_svg method,
        # so let's make sure that's also a mock to track calls.
        mock_svg_obj = MagicMock()
        mock_viewer2svg.return_value = mock_svg_obj

        # 4) Simulate a user click on the "Export" button
        qtbot.mouseClick(widget._export_btn, Qt.LeftButton)

        # 5) Assert the file dialog was indeed called
        mock_dialog.assert_called_once()

        # 6) Check that viewer2svg was called with the expected arguments
        blend_checked = widget._blend_imgs_checkbox.isChecked()
        labels_mode = widget._labels_mode_combobox.currentText()
        fit_content = widget._fit_content_checkbox.isChecked()

        mock_viewer2svg.assert_called_once_with(
            viewer=viewer,
            blend_images=blend_checked,
            labels_mode=labels_mode,
            fit_content=fit_content,
        )

        # 7) Ensure that save_svg was called on the returned object with the chosen path
        mock_svg_obj.save_svg.assert_called_once_with("test_output.svg")
