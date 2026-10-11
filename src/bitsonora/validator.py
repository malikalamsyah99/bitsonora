import json
import subprocess
from pathlib import Path

from .converter import require_tool
from .metadata import inspect_mp3


def validate_mp3(
    path,
    sample_rate=44100,
    channels=2,
    bitrate="192k",
):
    """Validate MP3 audio properties, ID3 metadata, and artwork."""
    file_path = Path(path)

    if not file_path.is_file() or file_path.stat().st_size == 0:
        raise ValueError("Output file is missing or empty.")

    result = subprocess.run(
        [
            require_tool("ffprobe"),
            "-v", "error",
            "-show_streams",
            "-show_format",
            "-of", "json",
            str(file_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    data = json.loads(result.stdout)

    audio_streams = [
        stream for stream in data.get("streams", [])
        if stream.get("codec_type") == "audio"
    ]

    if not audio_streams:
        raise ValueError("No audio stream found.")

    audio = audio_streams[0]

    if audio.get("codec_name") != "mp3":
        raise ValueError("Output codec is not MP3.")

    actual_rate = int(audio.get("sample_rate", 0))
    actual_channels = int(audio.get("channels", 0))
    duration = float(data.get("format", {}).get("duration", 0))

    if actual_rate != sample_rate:
        raise ValueError(
            f"Expected {sample_rate} Hz, got {actual_rate} Hz."
        )

    if actual_channels != channels:
        raise ValueError(
            f"Expected {channels} channels, got {actual_channels}."
        )

    if duration <= 0:
        raise ValueError("Invalid audio duration.")

    # MP3 stream bitrate can be unavailable in some files.
    actual_bitrate = int(audio.get("bit_rate") or 0)
    target_bitrate = int(bitrate.lower().replace("k", "")) * 1000

    if actual_bitrate and abs(actual_bitrate - target_bitrate) > 16000:
        raise ValueError(
            f"Expected approximately {target_bitrate} bps, "
            f"got {actual_bitrate} bps."
        )

    metadata = inspect_mp3(file_path)

    return {
        "valid": True,
        "codec": audio["codec_name"],
        "sample_rate": actual_rate,
        "channels": actual_channels,
        "bitrate_bps": actual_bitrate,
        "duration_seconds": duration,
        "size_bytes": file_path.stat().st_size,
        "metadata": metadata,
    }
