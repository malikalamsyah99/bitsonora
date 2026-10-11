from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from .resources import resource_path


def show_about_dialog(parent=None):
    dialog = QDialog(parent)
    dialog.setWindowTitle("About Bitsonora")
    dialog.setMinimumWidth(400)

    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(12)

    logo = QLabel()
    logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
    logo.setFixedSize(112, 112)

    pixmap = QPixmap(resource_path("assets/bitsonora.png"))
    if pixmap.isNull():
        raise RuntimeError("Could not load Bitsonora logo.")

    logo.setPixmap(
        pixmap.scaled(
            104,
            104,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
    )
    layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)

    title = QLabel("Bitsonora")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title.setStyleSheet("font-size: 26px; font-weight: bold;")

    version = QLabel("Version 0.1.0")
    version.setAlignment(Qt.AlignmentFlag.AlignCenter)
    version.setStyleSheet("color: #888;")

    description = QLabel(
        "A cross-platform batch audio converter that helps preserve "
        "metadata and embedded album artwork."
    )
    description.setWordWrap(True)
    description.setAlignment(Qt.AlignmentFlag.AlignCenter)

    developer = QLabel("Developed by Malik Alamsyah")
    developer.setAlignment(Qt.AlignmentFlag.AlignCenter)
    developer.setStyleSheet("font-weight: bold;")

    layout.addWidget(title)
    layout.addWidget(version)
    layout.addSpacing(4)
    layout.addWidget(description)
    layout.addSpacing(8)
    layout.addWidget(developer)

    links = [
        ("GitHub Profile", "https://github.com/malikalamsyah99"),
        (
            "Bitsonora Source Code",
            "https://github.com/malikalamsyah99/bitsonora",
        ),
        ("Developer Website", "https://malikalamsyah99.github.io/"),
    ]

    for label, url in links:
        button = QPushButton(label)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(
            lambda checked=False, target=url:
                QDesktopServices.openUrl(QUrl(target))
        )
        layout.addWidget(button)

    copyright_label = QLabel("© 2026 Malik Alamsyah")
    copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    copyright_label.setStyleSheet("color: #888; font-size: 11px;")
    layout.addSpacing(6)
    layout.addWidget(copyright_label)

    close_button = QPushButton("Close")
    close_button.clicked.connect(dialog.accept)

    close_row = QHBoxLayout()
    close_row.addStretch()
    close_row.addWidget(close_button)
    layout.addLayout(close_row)

    dialog.exec()
