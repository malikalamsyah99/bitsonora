from pathlib import Path
import sys


def resource_path(relative_path: str) -> str:
    """Find an asset in development or a PyInstaller app bundle."""
    relative = Path(relative_path)
    candidates = []

    bundle_dir = getattr(sys, "_MEIPASS", None)
    if bundle_dir:
        candidates.append(Path(bundle_dir) / relative)

    # Project root during development.
    candidates.append(
        Path(__file__).resolve().parents[2] / relative
    )

    # Common locations inside a macOS .app bundle.
    executable_dir = Path(sys.executable).resolve().parent
    candidates.extend([
        executable_dir / relative,
        executable_dir.parent / "Resources" / relative,
    ])

    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)

    raise FileNotFoundError(
        f"Asset not found: {relative_path}. "
        "Make sure the asset is included in the application build."
    )
