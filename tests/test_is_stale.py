from pytest import fixture  # noqa: PT013

from hatch_jupyter_builder import is_stale


@fixture()
def source_dir(tmpdir):
    source = tmpdir.mkdir("source")
    source.join("file1.txt").write("original content")
    source.join("file2.txt").write("original content")
    sub = source.mkdir("sub")
    sub.join("subfile1.txt").write("original content")
    sub.join("subfile2.txt").write("original content")
    source.mkdir("node_modules")
    sub2 = source.mkdir("node_modules", "lol")
    sub2.join("index.js").write("use strict;")
    for p in source.visit():
        p.setmtime(10000)
    return source


@fixture()
def destination_dir(tmpdir):
    destination = tmpdir.mkdir("destination")
    destination.join("file1.rtf").write("original content")
    destination.join("file2.rtf").write("original content")
    sub = destination.mkdir("sub")
    sub.join("subfile1.rtf").write("original content")
    sub.join("subfile2.rtf").write("original content")
    destination.mkdir("sub2")
    sub2 = destination.mkdir("sub2", "lol")
    sub2.join("static.html").write("<html><body>original content</body></html>")
    for p in destination.visit():
        p.setmtime(20000)
    return destination


def test_destination_is_not_stale(source_dir, destination_dir):
    assert is_stale(str(destination_dir), str(source_dir)) is False


def test_root_file_causes_stale(source_dir, destination_dir):
    source_dir.join("file1.txt").setmtime(30000)
    assert is_stale(str(destination_dir), str(source_dir)) is True


def test_sub_file_causes_stale(source_dir, destination_dir):
    source_dir.join("sub", "subfile2.txt").setmtime(30000)
    assert is_stale(str(destination_dir), str(source_dir)) is True


def test_folder_mtime_does_not_prevent_stale(source_dir, destination_dir):
    source_dir.join("sub", "subfile2.txt").setmtime(30000)
    destination_dir.setmtime(40000)
    destination_dir.join("sub").setmtime(40000)
    destination_dir.setmtime(40000)
    assert is_stale(str(destination_dir), str(source_dir)) is True


def test_folder_mtime_does_not_cause_stale(source_dir, destination_dir):
    source_dir.setmtime(40000)
    source_dir.join("sub").setmtime(40000)
    source_dir.setmtime(40000)
    assert is_stale(str(destination_dir), str(source_dir)) is False


# This behavior might not always be wanted?
# The alternative is to check whether ALL files in destination is newer
# than the newest file in source (more conservative).
def test_only_newest_files_determine_stale(source_dir, destination_dir):
    source_dir.join("file1.txt").setmtime(30000)
    destination_dir.join("file1.rtf").setmtime(40000)
    assert is_stale(str(destination_dir), str(source_dir)) is False


def test_unstale_on_equal(source_dir):
    assert is_stale(str(source_dir), str(source_dir)) is False


def test_file_vs_dir(source_dir, destination_dir):
    assert is_stale(str(destination_dir.join("file1.rtf")), str(source_dir)) is False
    source_dir.join("file2.txt").setmtime(30000)
    assert is_stale(str(destination_dir.join("file1.rtf")), str(source_dir)) is True


def test_dir_vs_file(source_dir, destination_dir):
    assert is_stale(str(destination_dir), str(source_dir.join("file1.txt"))) is False
    source_dir.join("file1.txt").setmtime(30000)
    assert is_stale(str(destination_dir), str(source_dir.join("file1.txt"))) is True


def test_file_vs_file(source_dir, destination_dir):
    assert (
        is_stale(str(destination_dir.join("file1.rtf")), str(source_dir.join("file1.txt"))) is False
    )
    source_dir.join("file1.txt").setmtime(30000)
    assert (
        is_stale(str(destination_dir.join("file1.rtf")), str(source_dir.join("file1.txt"))) is True
    )


def test_empty_dir(source_dir, tmpdir):
    empty_dir = tmpdir.mkdir("empty")
    assert is_stale(str(empty_dir), str(source_dir)) is True
    assert is_stale(str(source_dir), str(empty_dir)) is False
    assert is_stale(str(empty_dir), str(empty_dir)) is False


def test_missing_dir(source_dir, destination_dir):
    assert not is_stale(destination_dir, "does_not_exist")
    assert is_stale("does_not_exist", source_dir)
