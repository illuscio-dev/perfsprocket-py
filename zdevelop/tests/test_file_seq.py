import pytest
import stat
import os
from itertools import count
from pathlib import Path

from perfsprocket import FileSequence, SeqName, FileName


class TestSeqDunder:
    @pytest.mark.parametrize(
        "path",
        [
            "/Volumes/disk/folder/file.100.txt",
            Path("/Volumes/disk/folder/file.100.txt"),
        ],
    )
    def test_init(self, path):
        seq = FileSequence(path, start=100, end=200)

        print(f"path: {seq.path}\nstart:{seq.start}\nend:{seq.end}")

        assert seq.path == Path(path)
        assert seq.start == 100
        assert seq.end == 200

    def test_len(self, seq_theory: FileSequence):
        assert len(seq_theory) == 101

    @pytest.mark.parametrize(
        "index,answer",
        [
            (0, "/Volumes/disk/folder/file.100.txt"),
            (1, "/Volumes/disk/folder/file.101.txt"),
            (-1, "/Volumes/disk/folder/file.200.txt"),
            (-2, "/Volumes/disk/folder/file.199.txt"),
            (50, "/Volumes/disk/folder/file.150.txt"),
            (-50, "/Volumes/disk/folder/file.151.txt"),
        ],
    )
    def test_get_index(self, seq_theory: FileSequence, index: int, answer: str):
        assert seq_theory[index] == Path(answer)

    @pytest.mark.parametrize("index", [-102, 101, -300, 300])
    def test_get_index_raises(self, seq_theory: FileSequence, index: int):
        with pytest.raises(IndexError):
            path = seq_theory[index]
            print(path)

    @pytest.mark.parametrize(
        "bounds,start,end",
        [
            (slice(50, 76), 150, 175),
            (slice(None, 51), 100, 150),
            (slice(43, None), 143, 200),
            (slice(43, -1), 143, 199),
            (slice(-50, None), 151, 200),
            (slice(None, None), 100, 200),
        ],
    )
    def test_get_slice(
        self, seq_theory: FileSequence, bounds: slice, start: int, end: int
    ):
        sub_seq = seq_theory[bounds]
        assert sub_seq.start == start
        assert sub_seq.end == end

    @pytest.mark.parametrize(
        "index,answer",
        [
            (100, "/Volumes/disk/folder/file.100.txt"),
            (101, "/Volumes/disk/folder/file.101.txt"),
            (-1, "/Volumes/disk/folder/file.200.txt"),
            (-2, "/Volumes/disk/folder/file.199.txt"),
            (150, "/Volumes/disk/folder/file.150.txt"),
            (-50, "/Volumes/disk/folder/file.151.txt"),
            (-101, "/Volumes/disk/folder/file.100.txt"),
        ],
    )
    def test_get_file_num(self, seq_theory: FileSequence, index: int, answer: str):
        assert seq_theory.files[index] == Path(answer)

    @pytest.mark.parametrize("index", [99, 201, -102, -300, 300])
    def test_get_file_num_raises(self, seq_theory: FileSequence, index: int):
        with pytest.raises(IndexError):
            path = seq_theory.files[index]
            print(path)

    @pytest.mark.parametrize(
        "bounds,start,end",
        [
            (slice(150, 176), 150, 175),
            (slice(None, 151), 100, 150),
            (slice(143, None), 143, 200),
            (slice(143, -1), 143, 199),
            (slice(-50, None), 151, 200),
            (slice(None, None), 100, 200),
        ],
    )
    def test_filenum_get_slice(
        self, seq_theory: FileSequence, bounds: slice, start: int, end: int
    ):
        sub_seq = seq_theory.files[bounds]
        assert sub_seq.start == start
        assert sub_seq.end == end

    def test_iter(self, seq_theory):
        for i, path in enumerate(seq_theory, 100):
            answer = "/Volumes/disk/folder/file.###.txt".replace("###", str(i))
            print(answer)
            assert path == Path(answer)
        assert i == 200


class TestSeqDisk:
    @pytest.mark.parametrize(
        "file_method,src_remains",
        [(FileSequence.move_iter, False), (FileSequence.copy_iter, True)],
    )
    @pytest.mark.parametrize("str_dst", [False, True])
    def test_copy_move_iter(
        self, file_seq_for_operation, file_method, src_remains, str_dst
    ):
        src: FileSequence
        dst: Path

        src, dst = file_seq_for_operation
        dst_arg = str(dst) if str_dst else dst

        paths = list()

        for item in file_method(src, dst_arg):
            print(f"copied/moved: {item}")
            paths.append(item)

        assert len(paths) == 102

        new_file = paths.pop(-1)

        assert isinstance(new_file, FileSequence)
        assert all(isinstance(x, Path) for x in paths)

        assert new_file.path == dst / src.path.name

        for i_old, this_path in enumerate(src, 1):
            print(this_path.exists(), this_path)
            assert this_path.exists() if src_remains else not this_path.exists()

        for i_new, this_path in enumerate(new_file, 1):
            assert this_path.exists()
            assert this_path.read_text() == str(i_new + 99)

        assert i_new == i_old == 101

        print("Source Dir ls:")
        for i, x in enumerate(src.path.parent.iterdir(), 1):
            print(f"{i}: {x}")

        print("-----------")

        print("Destination Dir ls:")
        for i, x in enumerate(dst.iterdir(), 1):
            print(f"{i}: {x}")

    @pytest.mark.parametrize(
        "file_method,src_remains",
        [(FileSequence.move, False), (FileSequence.copy, True)],
    )
    @pytest.mark.parametrize("str_dst", [False, True])
    def test_copy_move(self, file_method, file_seq_for_operation, src_remains, str_dst):
        src: FileSequence
        dst: Path

        src, dst = file_seq_for_operation
        dst_arg = str(dst) if str_dst else dst

        new_file = file_method(src, dst_arg)

        assert isinstance(new_file, FileSequence)
        assert new_file.path == dst / src.path.name

        for i_old, this_path in enumerate(src, 1):
            print(this_path.exists(), this_path)
            assert this_path.exists() if src_remains else not this_path.exists()

        for i_new, this_path in enumerate(new_file, 1):
            assert this_path.exists()
            assert this_path.read_text() == str(i_new + 99)

        assert len(src) == len(new_file)

        print("Source Dir ls:")
        for i, x in enumerate(src.path.parent.iterdir(), 1):
            print(f"{i}: {x}")

        print("-----------")

        print("Destination Dir ls:")
        for i, x in enumerate(dst.iterdir(), 1):
            print(f"{i}: {x}")

    @pytest.mark.parametrize(
        "new_name, base_name, start_frame, padding, ext, use_iter",
        [
            ("new_name.0100.dpx", "new_name", 100, 4, "dpx", True),
            ("new_name.0100.dpx", "new_name", 100, 4, "dpx", False),
            ("new_name.####.dpx", "new_name", 100, 4, "dpx", False),
            ("new_name.0200.dpx", "new_name", 200, 4, "dpx", True),
            ("new_name.0200.dpx", "new_name", 200, 4, "dpx", False),
            (
                SeqName("new_name", "dpx", start=200, pad=4),
                "new_name",
                200,
                4,
                "dpx",
                False,
            ),
            (FileName("new_name", "dpx"), "new_name", 100, 3, "dpx", False),
            ("file.090.txt", "file", 90, 3, "txt", False),
            ("file.110.txt", "file", 110, 3, "txt", False),
            ("file.110.txt", "file", 110, 3, "txt", False),
        ],
    )
    def test_rename(
        self,
        file_seq_for_operation,
        new_name,
        base_name,
        start_frame,
        padding,
        ext,
        use_iter,
    ):
        src: FileSequence
        dst: Path

        src, dst = file_seq_for_operation

        print("Original Dir List")
        for x in sorted(list(src.path.parent.iterdir())):
            print(x)

        print("------------------")

        assert all(x.exists() for x in src)

        if use_iter:
            for item in src.rename_iter(new_name):
                try:
                    path_old, path_new = item
                    print(f"{path_old} -> {path_new}")
                except ValueError:
                    file_new = item
                else:
                    assert isinstance(path_old, Path)
                    assert isinstance(path_new, Path)
                    assert path_new.name != path_old.name
                    assert path_new.parent == path_old.parent

                    assert not path_old.exists()
                    assert path_new.exists()
        else:
            file_new = src.rename(new_name)

        print("------------------")

        print("Post-rename Dir List")
        for x in sorted(list(src.path.parent.iterdir())):
            print(x)

        for num, contents, path in zip(count(start_frame), count(100), file_new):
            assert path.name == f"{base_name}.{str(num).zfill(padding)}.{ext}"
            assert path.read_text() == str(contents)

        assert file_new.path.parent == src.path.parent
        assert file_new.path.name == (
            f"{base_name}.{str(start_frame).zfill(padding)}.{ext}"
        )

        print("------------------")
        print("Missing:")
        for x in (x for x in file_new if not x.exists()):
            print(x)

        assert not all(x.exists() for x in src)
        assert all(x.exists() for x in file_new)

    @pytest.mark.parametrize("use_iter", [True, False])
    def test_delete(self, file_seq_for_operation, use_iter):
        src: FileSequence
        dst: Path

        src, dst = file_seq_for_operation
        assert src.path.exists()

        if use_iter:
            for item in src.delete_iter():
                print(f"deleted: {item}")
                assert isinstance(item, Path)
                assert not item.exists()
        else:
            src.delete()

        assert len([x for x in src.path.parent.iterdir()]) == 0

        print("--------")

        print("Source Dir ls:")
        for i, x in enumerate(src.path.parent.iterdir(), 1):
            print(f"{i}: {x}")

    @pytest.mark.parametrize("use_iter", [True, False])
    def test_chmod(self, file_seq_for_operation, use_iter):
        src: FileSequence
        dst: Path

        src, dst = file_seq_for_operation
        original_mode = src.path.stat().st_mode

        print("Original mode list:")
        for x in src:
            print(x.stat().st_mode, str(x))

        print("--------")

        if use_iter:
            for item in src.chmod_iter(0o777):
                print(f"changed: {item}")
                assert isinstance(item, Path)
        else:
            src.chmod(0o777)

        print("--------")

        print("Changed mode list:")
        for x in src:
            print(stat.S_IMODE(x.stat().st_mode), str(x))

        if not os.name == "nt":
            for path in src:
                assert path.stat().st_mode != original_mode
                assert stat.S_IMODE(path.stat().st_mode) == 0o777
