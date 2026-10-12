from bitsonora.batch import collect_audio_files


def create_file(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"test")


def test_collect_audio_files_filters_extensions_and_duplicates(tmp_path):
    folder = tmp_path / "music"

    create_file(folder / "track.m4a")
    create_file(folder / "album.FLAC")
    create_file(folder / "notes.txt")
    create_file(folder / "nested" / "hidden.wav")

    results = collect_audio_files([
        folder,
        folder / "track.m4a",
    ])

    assert len(results) == 2
    assert {path.name for path in results} == {
        "track.m4a",
        "album.FLAC",
    }


def test_collect_audio_files_can_include_subfolders(tmp_path):
    folder = tmp_path / "music"

    create_file(folder / "track.m4a")
    create_file(folder / "nested" / "hidden.wav")

    results = collect_audio_files([folder], recursive=True)

    assert len(results) == 2
    assert {path.suffix.lower() for path in results} == {
        ".m4a",
        ".wav",
    }


def test_collect_audio_files_ignores_missing_inputs(tmp_path):
    results = collect_audio_files([tmp_path / "does-not-exist.m4a"])

    assert results == []
