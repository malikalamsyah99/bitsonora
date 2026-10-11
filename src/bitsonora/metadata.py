from pathlib import Path
from mutagen.id3 import ID3, ID3NoHeaderError


def inspect_mp3(path):
    """Return basic ID3 metadata and embedded cover-art information."""
    file_path = Path(path)

    try:
        tags = ID3(file_path)
    except ID3NoHeaderError:
        tags = ID3()

    def first_text(frame_id):
        frames = tags.getall(frame_id)
        if not frames:
            return None

        value = getattr(frames[0], "text", None)
        if value:
            return str(value[0])

        return None

    pictures = tags.getall("APIC")

    return {
        "title": first_text("TIT2"),
        "artist": first_text("TPE1"),
        "album": first_text("TALB"),
        "album_artist": first_text("TPE2"),
        "track": first_text("TRCK"),
        "date": first_text("TDRC"),
        "genre": first_text("TCON"),
        "has_cover_art": bool(pictures),
        "cover_count": len(pictures),
        "cover_mime_types": [picture.mime for picture in pictures],
    }
