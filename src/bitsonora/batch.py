from pathlib import Path
from typing import Callable, Optional

from .converter import SUPPORTED_INPUTS, convert_file
from .validator import validate_mp3


def collect_audio_files(inputs, recursive=False):
    """Collect supported audio files from files and folders."""
    collected = []
    seen = set()

    for item in inputs:
        path = Path(item).expanduser().resolve()

        if not path.exists():
            continue

        if path.is_file():
            candidates = [path]
        elif path.is_dir():
            iterator = path.rglob("*") if recursive else path.iterdir()
            candidates = sorted(iterator)
        else:
            continue

        for candidate in candidates:
            if not candidate.is_file():
                continue

            if candidate.suffix.lower() not in SUPPORTED_INPUTS:
                continue

            resolved = candidate.resolve()

            if resolved not in seen:
                seen.add(resolved)
                collected.append(resolved)

    return sorted(collected, key=lambda p: str(p).lower())


def batch_convert(
    inputs,
    output_dir,
    bitrate="192k",
    sample_rate=44100,
    channels=2,
    recursive=False,
    progress_callback: Optional[Callable] = None,
):
    """Convert files and validate each resulting MP3."""
    files = collect_audio_files(inputs, recursive=recursive)
    destination = Path(output_dir).expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)

    # Avoid accidentally converting files already inside the output tree.
    output_resolved = destination.resolve()
    files = [
        source for source in files
        if not source.is_relative_to(output_resolved)
    ]

    results = []
    total = len(files)

    for index, source in enumerate(files, start=1):
        output = destination / f"{source.stem}.mp3"

        try:
            converted = convert_file(
                source,
                output,
                bitrate=bitrate,
                sample_rate=sample_rate,
                channels=channels,
            )

            validation = validate_mp3(
                converted,
                sample_rate=sample_rate,
                channels=channels,
                bitrate=bitrate,
            )

            result = {
                "status": "success",
                "source": str(source),
                "output": str(converted),
                "validation": validation,
                "error": None,
            }

        except Exception as exc:
            result = {
                "status": "failed",
                "source": str(source),
                "output": str(output),
                "validation": None,
                "error": str(exc),
            }

        results.append(result)

        if progress_callback is not None:
            progress_callback(index, total, result)

    return results
