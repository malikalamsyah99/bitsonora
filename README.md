# Bitsonora

**A cross-platform desktop audio converter with metadata and album artwork preservation.**

Bitsonora is a desktop application built with Python, PySide6, and FFmpeg. It provides a graphical interface for batch-converting audio files to MP3, configuring output audio properties, and checking converted files.

> **Project status:** Early development. The macOS app has been built and tested locally. Windows and Linux builds, self-contained FFmpeg packaging, and a public release have not yet been verified.

## Contents

- [Features](#features)
- [Supported Formats](#supported-formats)
- [Requirements](#requirements)
- [Installation](#installation)
- [Run from Source](#run-from-source)
- [How to Use](#how-to-use)
- [Output Settings](#output-settings)
- [PSPMAN Preset](#pspman-preset)
- [Metadata and Album Artwork](#metadata-and-album-artwork)
- [Output Validation](#output-validation)
- [Project Structure](#project-structure)
- [Development and Testing](#development-and-testing)
- [Build for macOS](#build-for-macos)
- [Troubleshooting](#troubleshooting)
- [Known Limitations](#known-limitations)
- [Roadmap](#roadmap)
- [Developer](#developer)
- [License](#license)

## Features

- Batch conversion of multiple audio files or files discovered in a selected folder.
- Graphical desktop interface built with PySide6.
- Configurable MP3 bitrate, sample rate, and mono/stereo output.
- Metadata mapping during conversion, where supported by the source and output formats.
- Embedded album artwork mapping, where supported by FFmpeg and the involved formats.
- Output inspection using FFprobe.
- Per-file conversion status and a final success/failure summary.
- Continues processing remaining files when an individual conversion fails.
- Avoids intentionally overwriting an existing output file.
- PSPMAN preset for MP3 at 44.1 kHz stereo.
- About dialog with developer profile, source repository, and website links.
- Custom Bitsonora branding for the macOS application.

## Supported Formats

### Input formats

| Format | Extensions |
|---|---|
| MPEG-4 Audio | `.m4a` |
| Advanced Audio Coding | `.aac` |
| Waveform Audio | `.wav` |
| Free Lossless Audio Codec | `.flac` |
| Ogg audio | `.ogg` |
| Opus audio | `.opus` |

Actual decoding support depends on the installed FFmpeg build and the codecs used by a source file.

### Output format

The current conversion engine outputs **MP3**. Other output formats are not implemented in the current GUI.

## Requirements

- Python 3.9 or newer
- FFmpeg and FFprobe available to the application
- PySide6
- Mutagen
- PyInstaller for packaging the macOS application

### Install FFmpeg

#### macOS (Homebrew)

```bash
brew install ffmpeg
```

#### Windows

Install an FFmpeg build for Windows and make sure `ffmpeg` and `ffprobe` are available through `PATH`. See the official FFmpeg download page:

https://ffmpeg.org/download.html

#### Debian/Ubuntu Linux

```bash
sudo apt update
sudo apt install ffmpeg
```

Other Linux distributions may use different package managers or package names.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/malikalamsyah99/bitsonora.git
cd bitsonora
```

### 2. Create and activate a virtual environment

macOS and Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Bitsonora and development dependencies

From the repository root, run:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### 4. Verify dependencies

```bash
python -c "import PySide6, mutagen; print('Python dependencies OK')"
ffmpeg -version
ffprobe -version
```

The Python import test and both FFmpeg commands should complete successfully.

## Run from Source

Activate the virtual environment and run this from the repository root:

```bash
python -m bitsonora.main
```

The Bitsonora desktop window should open.

## How to Use

1. **Add files:** Select **Add Files** to choose one or more supported audio files.
2. **Add a folder:** Select **Add Folder** to scan a directory. Enable the subfolder option if nested directories should also be scanned.
3. **Choose output:** Select the destination folder for converted MP3 files.
4. **Configure audio:** Select bitrate, sample rate, and channel configuration, or choose the PSPMAN preset.
5. **Convert:** Click **Convert to MP3** and follow the progress bar and conversion log.
6. **Review:** Check the final success/failure summary and inspect the output folder.

Use a separate output folder from the source whenever practical. Existing output files are not intentionally overwritten.

## Output Settings

### Bitrate

The GUI offers these MP3 bitrate settings:

- 128 kbps
- 192 kbps
- 256 kbps
- 320 kbps

A higher bitrate generally creates a larger file. Upscaling a lossy source to a higher bitrate does not restore audio information already lost in the source.

### Sample rate

- 44,100 Hz
- 48,000 Hz

### Channels

- Stereo
- Mono

The selected sample rate and channel configuration are applied during conversion.

## PSPMAN Preset

The GUI includes **PSPMAN - MP3 44.1 kHz Stereo**, which selects:

| Setting | Value |
|---|---|
| Output format | MP3 |
| Default bitrate | 192 kbps |
| Sample rate | 44,100 Hz |
| Channels | Stereo |

You can change the bitrate after selecting the preset. This preset targets the audio configuration used during PSPMAN compatibility testing; playback should still be verified on the target device because player and metadata support can vary.

## Metadata and Album Artwork

The conversion engine asks FFmpeg to map source metadata and optional image streams into the output. Mutagen is used to inspect common MP3 ID3 fields such as:

- Title
- Artist
- Album
- Album artist
- Track number
- Date
- Genre
- Embedded cover artwork

Preservation depends on the source file, metadata format, image format, and FFmpeg's ability to map the relevant streams. The current implementation inspects common ID3 tags and reports whether cover artwork is detected. It does not yet compare every metadata field against the source automatically.

## Output Validation

After conversion, Bitsonora uses FFprobe to inspect the generated MP3. Checks include:

- Output file exists and is not empty.
- An audio stream is present.
- The codec is MP3.
- Sample rate matches the selected setting.
- Channel count matches the selected setting.
- Duration is positive.
- Reported bitrate is approximately within the configured target range, when the stream reports a bitrate.

Metadata inspection is also returned by the validator. These checks help detect common conversion issues but do not replace listening tests or compatibility checks on a target device.

## Project Structure

```text
bitsonora/
├── assets/
│   ├── bitsonora.png
│   ├── bitsonora.icns
│   └── Bitsonora.iconset/
├── src/
│   └── bitsonora/
│       ├── __init__.py
│       ├── main.py
│       ├── converter.py
│       ├── batch.py
│       ├── metadata.py
│       ├── validator.py
│       ├── resources.py
│       └── about.py
├── tests/
├── .github/
│   └── workflows/
├── pyproject.toml
├── Bitsonora.spec
├── run_bitsonora.py
├── README.md
└── .gitignore
```

### Main modules

| File | Purpose |
|---|---|
| `main.py` | PySide6 desktop GUI and application entry point |
| `converter.py` | Single-file FFmpeg conversion |
| `batch.py` | Input discovery, batch processing, and per-file results |
| `metadata.py` | Inspection of MP3 ID3 tags and artwork |
| `validator.py` | Validation of converted audio properties |
| `resources.py` | Resource path lookup in source and bundled app contexts |
| `about.py` | About dialog and developer links |
| `pyproject.toml` | Project metadata and Python dependencies |
| `Bitsonora.spec` | PyInstaller build configuration |

## Development and Testing

### Run the application

```bash
python -m bitsonora.main
```

### Run automated tests

```bash
python -m pytest
```

The test suite is still being developed. A successful pytest run does not imply that every input format, metadata variant, or operating system has been tested.

## Build for macOS

Install PyInstaller into the active virtual environment:

```bash
python -m pip install pyinstaller
```

Run the following command from the repository root:

```bash
python -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name Bitsonora \
  --icon assets/bitsonora.icns \
  --add-data "assets/bitsonora.png:assets" \
  --paths src \
  --collect-all PySide6 \
  --collect-all shiboken6 \
  run_bitsonora.py
```

The application bundle should be created at:

```text
dist/Bitsonora.app
```

Open it on macOS with:

```bash
open dist/Bitsonora.app
```

This is a development build, not a signed and notarized public release. The current bundle does not yet include a fully managed, self-contained FFmpeg/FFprobe distribution; those executables must still be available to the application.

## Troubleshooting

### `ModuleNotFoundError: No module named 'bitsonora'`

From the repository root with the virtual environment active, run:

```bash
python -m pip install -e .
python -c "import bitsonora; print(bitsonora.__file__)"
```

### `ffmpeg: command not found`

Check whether FFmpeg and FFprobe are installed and accessible through `PATH`.

macOS/Linux:

```bash
which ffmpeg
which ffprobe
```

Windows Command Prompt or PowerShell:

```powershell
where.exe ffmpeg
where.exe ffprobe
```

After changing `PATH`, restart the terminal or application.

### Output file already exists

Bitsonora refuses to overwrite an existing output file. Select a different output directory or handle the existing file before retrying.

### A file fails to convert

Read the specific error in the conversion log. Confirm that the input file is readable, its extension is supported, and FFmpeg can decode its codec.

### macOS still shows the old icon

Confirm that the latest build was generated and that you are opening `dist/Bitsonora.app`, not an older copy. Finder and Dock can temporarily cache application icons.

## Known Limitations

- MP3 is the only implemented output format.
- FFmpeg and FFprobe are external dependencies and are not yet fully bundled for distribution.
- Signed and notarized macOS distribution is not configured.
- Windows and Linux builds have not yet been verified.
- Automated tests still need broader coverage for conversion, metadata, artwork, and error handling.
- Metadata inspection focuses on common ID3 tags.
- Cancellation of an active batch is not implemented.
- Duplicate output names from separate input directories can conflict when saved to one destination folder.
- Successful validation does not guarantee playback on every audio player or target device.

## Roadmap

- [ ] Bundle or reliably manage FFmpeg and FFprobe for distribution.
- [ ] Expand tests for audio conversion, metadata, and cover art.
- [ ] Add safe cancellation for active conversions.
- [ ] Handle duplicate output filenames from different source directories.
- [ ] Build and test Windows packages.
- [ ] Build and test Linux packages.
- [ ] Prepare signed and notarized macOS distribution.
- [ ] Publish application packages through GitHub Releases.

## Developer

**Malik Alamsyah**

- **GitHub profile:** https://github.com/malikalamsyah99
- **Source repository:** https://github.com/malikalamsyah99/bitsonora
- **Developer website:** https://malikalamsyah99.github.io/

For bug reports and feature requests, use [GitHub Issues](https://github.com/malikalamsyah99/bitsonora/issues).

## License

No license has been added to this repository yet. Until a license is added, permissions for reuse and redistribution have not been explicitly granted. Choose and add an appropriate license before inviting the public to reuse the code.
