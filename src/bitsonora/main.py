import sys
from pathlib import Path

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .batch import batch_convert
from .about import show_about_dialog
from .resources import resource_path


class ConversionWorker(QThread):
    progress = Signal(int, int, dict)
    completed = Signal(int, int, str)
    error = Signal(str)

    def __init__(
        self,
        inputs,
        output_dir,
        bitrate,
        sample_rate,
        channels,
        recursive,
    ):
        super().__init__()
        self.inputs = inputs
        self.output_dir = output_dir
        self.bitrate = bitrate
        self.sample_rate = sample_rate
        self.channels = channels
        self.recursive = recursive

    def run(self):
        try:
            results = batch_convert(
                inputs=self.inputs,
                output_dir=self.output_dir,
                bitrate=self.bitrate,
                sample_rate=self.sample_rate,
                channels=self.channels,
                recursive=self.recursive,
                progress_callback=self.on_progress,
            )

            success = sum(
                result["status"] == "success" for result in results
            )
            failed = sum(
                result["status"] == "failed" for result in results
            )

            self.completed.emit(success, failed, self.output_dir)

        except Exception as exc:
            self.error.emit(str(exc))

    def on_progress(self, completed, total, result):
        self.progress.emit(completed, total, result)


class BitsonoraWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bitsonora")
        self.setWindowIcon(QIcon(resource_path("assets/bitsonora.png")))
        help_menu = self.menuBar().addMenu("Help")
        about_action = help_menu.addAction("About Bitsonora")
        about_action.triggered.connect(
            lambda: show_about_dialog(self)
        )

        self.resize(820, 680)

        self.worker = None
        self.inputs = []

        root = QWidget()
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("Bitsonora")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")

        subtitle = QLabel(
            "Batch audio converter with metadata and album artwork preservation"
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #777;")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        layout.addWidget(QLabel("Input files and folders"))

        input_buttons = QHBoxLayout()

        self.add_files_button = QPushButton("Add Files")
        self.add_folder_button = QPushButton("Add Folder")
        self.remove_button = QPushButton("Remove Selected")
        self.clear_button = QPushButton("Clear")

        input_buttons.addWidget(self.add_files_button)
        input_buttons.addWidget(self.add_folder_button)
        input_buttons.addWidget(self.remove_button)
        input_buttons.addWidget(self.clear_button)

        layout.addLayout(input_buttons)

        self.input_list = QListWidget()
        self.input_list.setMinimumHeight(150)
        layout.addWidget(self.input_list)

        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output folder"))

        self.output_edit = QLineEdit(
            str(Path.home() / "Music" / "Bitsonora")
        )
        self.browse_output_button = QPushButton("Browse")
        output_layout.addWidget(self.output_edit, 1)
        output_layout.addWidget(self.browse_output_button)

        layout.addLayout(output_layout)

        settings = QGridLayout()
        settings.setHorizontalSpacing(16)
        settings.setVerticalSpacing(10)

        settings.addWidget(QLabel("Bitrate"), 0, 0)
        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems(
            ["128 kbps", "192 kbps", "256 kbps", "320 kbps"]
        )
        self.bitrate_combo.setCurrentText("192 kbps")
        settings.addWidget(self.bitrate_combo, 0, 1)

        settings.addWidget(QLabel("Sample rate"), 0, 2)
        self.sample_combo = QComboBox()
        self.sample_combo.addItems(["44100 Hz", "48000 Hz"])
        settings.addWidget(self.sample_combo, 0, 3)

        settings.addWidget(QLabel("Channels"), 1, 0)
        self.channels_combo = QComboBox()
        self.channels_combo.addItems(["Stereo", "Mono"])
        settings.addWidget(self.channels_combo, 1, 1)

        self.recursive_checkbox = QCheckBox(
            "Include subfolders when scanning folders"
        )
        self.recursive_checkbox.setChecked(False)
        settings.addWidget(self.recursive_checkbox, 1, 2, 1, 2)

        settings.addWidget(QLabel("Preset"), 2, 0)
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "Custom",
            "PSPMAN - MP3 44.1 kHz Stereo",
        ])
        settings.addWidget(self.preset_combo, 2, 1, 1, 3)

        layout.addLayout(settings)

        self.start_button = QPushButton("Convert to MP3")
        self.start_button.setMinimumHeight(42)
        self.start_button.setStyleSheet(
            "font-weight: bold; font-size: 14px;"
        )
        layout.addWidget(self.start_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        layout.addWidget(QLabel("Conversion log"))

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(130)
        layout.addWidget(self.log, 1)

        self.add_files_button.clicked.connect(self.add_files)
        self.add_folder_button.clicked.connect(self.add_folder)
        self.remove_button.clicked.connect(self.remove_selected)
        self.clear_button.clicked.connect(self.clear_inputs)
        self.browse_output_button.clicked.connect(self.browse_output)
        self.start_button.clicked.connect(self.start_conversion)
        self.preset_combo.currentIndexChanged.connect(self.apply_preset)

        self.setStyleSheet("""
            QPushButton {
                padding: 8px 12px;
            }
            QLineEdit, QListWidget, QTextEdit, QComboBox {
                padding: 6px;
            }
        """)

    def add_input(self, path):
        path = str(Path(path).expanduser().resolve())

        if path not in self.inputs:
            self.inputs.append(path)
            self.input_list.addItem(path)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select audio files",
            str(Path.home()),
            "Audio files (*.m4a *.aac *.wav *.flac *.ogg *.opus)",
        )

        for file_path in files:
            self.add_input(file_path)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select audio folder",
            str(Path.home()),
        )

        if folder:
            self.add_input(folder)

    def remove_selected(self):
        selected = self.input_list.selectedItems()

        for item in selected:
            path = item.text()
            self.inputs.remove(path)
            self.input_list.takeItem(self.input_list.row(item))

    def clear_inputs(self):
        self.inputs.clear()
        self.input_list.clear()

    def browse_output(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select output folder",
            self.output_edit.text(),
        )

        if folder:
            self.output_edit.setText(folder)

    def set_busy(self, busy):
        for widget in (
            self.add_files_button,
            self.add_folder_button,
            self.remove_button,
            self.clear_button,
            self.browse_output_button,
            self.bitrate_combo,
            self.sample_combo,
            self.channels_combo,
            self.recursive_checkbox,
            self.preset_combo,
            self.start_button,
            self.output_edit,
        ):
            widget.setEnabled(not busy)

        self.input_list.setEnabled(not busy)

    def apply_preset(self, index):
        if self.preset_combo.itemText(index).startswith("PSPMAN"):
            self.bitrate_combo.setCurrentText("192 kbps")
            self.sample_combo.setCurrentText("44100 Hz")
            self.channels_combo.setCurrentText("Stereo")

    def start_conversion(self):
        if self.worker is not None and self.worker.isRunning():
            return

        if not self.inputs:
            QMessageBox.warning(
                self,
                "No input",
                "Add at least one audio file or folder first.",
            )
            return

        output_dir = self.output_edit.text().strip()

        if not output_dir:
            QMessageBox.warning(
                self,
                "No output folder",
                "Choose an output folder first.",
            )
            return

        bitrate = self.bitrate_combo.currentText().split()[0] + "k"
        sample_rate = int(
            self.sample_combo.currentText().split()[0]
        )
        channels = (
            2 if self.channels_combo.currentText() == "Stereo" else 1
        )

        self.log.clear()
        self.progress_bar.setRange(0, 0)
        self.status_label.setText("Starting conversion...")
        self.set_busy(True)

        self.worker = ConversionWorker(
            inputs=list(self.inputs),
            output_dir=output_dir,
            bitrate=bitrate,
            sample_rate=sample_rate,
            channels=channels,
            recursive=self.recursive_checkbox.isChecked(),
        )

        self.worker.progress.connect(self.on_progress)
        self.worker.completed.connect(self.on_completed)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_progress(self, completed, total, result):
        self.progress_bar.setRange(0, max(total, 1))
        self.progress_bar.setValue(completed)

        filename = Path(result["source"]).name
        status = result["status"].upper()

        self.log.append(f"[{completed}/{total}] {status}: {filename}")

        if result["status"] == "success":
            self.log.append(f"  Output: {result['output']}")
        else:
            self.log.append(f"  Error: {result['error']}")

        self.status_label.setText(
            f"Processing: {completed}/{total}"
        )

    def on_completed(self, success, failed, output_dir):
        self.set_busy(False)
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1)

        self.status_label.setText(
            f"Finished — {success} successful, {failed} failed"
        )

        self.log.append("")
        self.log.append("========== SUMMARY ==========")
        self.log.append(f"Successful: {success}")
        self.log.append(f"Failed: {failed}")
        self.log.append(f"Output folder: {output_dir}")

        QMessageBox.information(
            self,
            "Conversion finished",
            f"Successful: {success}\n"
            f"Failed: {failed}\n\n"
            f"Output folder:\n{output_dir}",
        )

    def on_error(self, message):
        self.set_busy(False)
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)
        self.status_label.setText("Conversion error")
        self.log.append(f"ERROR: {message}")

        QMessageBox.critical(
            self,
            "Conversion error",
            message,
        )

    def closeEvent(self, event):
        if self.worker is not None and self.worker.isRunning():
            QMessageBox.warning(
                self,
                "Conversion in progress",
                "Wait for the current conversion to finish before closing.",
            )
            event.ignore()
            return

        event.accept()


def main():
    app = QApplication(sys.argv)
    window = BitsonoraWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
