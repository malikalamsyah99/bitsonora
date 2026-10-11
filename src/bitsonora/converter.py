from pathlib import Path
import shutil
import subprocess


SUPPORTED_INPUTS = {".m4a", ".aac", ".wav", ".flac", ".ogg", ".opus"}


def require_tool(name: str) -> str:
    """Find an executable in PATH or common Homebrew locations."""
    path = shutil.which(name)
    if path:
        return path

    candidates = [
        Path("/opt/homebrew/bin") / name,
        Path("/usr/local/bin") / name,
    ]

    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)

    raise RuntimeError(
        f"{name} was not found. Install FFmpeg and ensure it is available."
    )


def convert_file(
    input_path,
    output_path=None,
    bitrate="192k",
    sample_rate=44100,
    channels=2,
):
    """Convert an audio file to MP3 while preserving metadata and cover art."""
    source = Path(input_path).expanduser().resolve()

    if not source.is_file():
        raise FileNotFoundError(f"Input file not found: {source}")

    if source.suffix.lower() not in SUPPORTED_INPUTS:
        raise ValueError(f"Unsupported input format: {source.suffix}")

    if output_path is None:
        destination = source.with_suffix(".mp3")
    else:
        destination = Path(output_path).expanduser().resolve()

    if source == destination:
        raise ValueError("Input and output paths must be different.")

    if destination.suffix.lower() != ".mp3":
        raise ValueError("Output file must have an .mp3 extension.")

    if destination.exists():
        raise FileExistsError(
            f"Output already exists; refusing to overwrite: {destination}"
        )

    if bitrate not in {"128k", "192k", "256k", "320k"}:
        raise ValueError("Bitrate must be 128k, 192k, 256k, or 320k.")

    if sample_rate not in {44100, 48000}:
        raise ValueError("Sample rate must be 44100 or 48000 Hz.")

    if channels not in {1, 2}:
        raise ValueError("Channels must be 1 (mono) or 2 (stereo).")

    ffmpeg = require_tool("ffmpeg")

    destination.parent.mkdir(parents=True, exist_ok=True)

    command = [
        ffmpeg,
        "-hide_banner",
        "-nostdin",
        "-n",
        "-i", str(source),
        "-map", "0:a:0",
        "-map", "0:v?",
        "-map_metadata", "0",
        "-vn",
    ]

    # -vn disables video, so explicitly map the cover art again via
    # a separate command is not appropriate. Use the audio + optional
    # picture mapping below instead.
    command = [
        ffmpeg,
        "-hide_banner",
        "-nostdin",
        "-n",
        "-i", str(source),
        "-map", "0:a:0",
        "-map", "0:v?",
        "-map_metadata", "0",
        "-c:a", "libmp3lame",
        "-b:a", bitrate,
        "-ar", str(sample_rate),
        "-ac", str(channels),
        "-c:v", "mjpeg",
        "-disposition:v:0", "attached_pic",
        "-id3v2_version", "3",
        str(destination),
    ]

    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        destination.unlink(missing_ok=True)
        details = exc.stderr.strip() if exc.stderr else str(exc)
        raise RuntimeError(f"FFmpeg conversion failed:\n{details}") from exc

    if not destination.is_file() or destination.stat().st_size == 0:
        destination.unlink(missing_ok=True)
        raise RuntimeError("FFmpeg did not produce a valid output file.")

    return destination
