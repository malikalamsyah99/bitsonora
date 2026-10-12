import os
import shutil
import stat
import subprocess
from pathlib import Path

from static_ffmpeg import run


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "vendor" / "ffmpeg"


def main():
    print("Resolving platform-specific FFmpeg binaries...")

    ffmpeg_source, ffprobe_source = (
        run.get_or_fetch_platform_executables_else_raise()
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    suffix = ".exe" if os.name == "nt" else ""

    for name, source in (
        ("ffmpeg", ffmpeg_source),
        ("ffprobe", ffprobe_source),
    ):
        source_path = Path(source)
        destination = OUTPUT_DIR / f"{name}{suffix}"

        if not source_path.is_file():
            raise FileNotFoundError(
                f"Downloaded executable not found: {source_path}"
            )

        shutil.copy2(source_path, destination)

        if os.name != "nt":
            destination.chmod(
                destination.stat().st_mode
                | stat.S_IXUSR
                | stat.S_IXGRP
                | stat.S_IXOTH
            )

        subprocess.run(
            [str(destination), "-version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        print(f"Verified: {destination}")

    print("\nBoth FFmpeg executables are ready for packaging.")


if __name__ == "__main__":
    main()
