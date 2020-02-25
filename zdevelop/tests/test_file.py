import pytest
import stat
import os
from perfsprocket import File
from pathlib import Path, PurePath


class TestDunder:
    def test_init_path(self):
        path = Path("/Volumes/disk/folder/file.txt")
        file = File(path)

        assert file.path == path

    def test_init_str(self):
        path = "/Volumes/disk/folder/file.txt"
        file = File(path)

        assert file.path == Path(path)

    def test_init_pure_path(self):
        path = PurePath("/Volumes/disk/folder/file.txt")
        file = File(path)

        assert isinstance(file.path, Path)

    def test_init_os_path(self, concrete_path):
        path = concrete_path("/Volumes/disk/folder/file.txt")
        file = File(path)

        assert isinstance(file.path, concrete_path)

    def test_len(self):
        path = Path("/Volumes/disk/folder/file.txt")
        file = File(path)

        assert len(file) == 1

    def test_iter(self):
        path = Path("/Volumes/disk/folder/file.txt")
        file = File(path)

        for i, path in enumerate(file):
            assert isinstance(path, Path)

        assert i == 0

    def test_repr(self):
        path = Path("/Volumes/disk/folder/file.txt")
        file = File(path)
        print(repr(file))
        if os.name != "nt":
            assert repr(file) == "<File: '/Volumes/disk/folder/file.txt'>"
        else:
            assert repr(file) == "<File: '\\Volumes\\disk\\folder\\file.txt'>"


class TestDisk:
    @pytest.mark.parametrize(
        "file_method,src_remains", [(File.move_iter, False), (File.copy_iter, True)]
    )
    def test_copy_move_iter(self, file_method, single_file_for_operation, src_remains):
        src: File
        dst: Path

        src, dst = single_file_for_operation

        paths = list()

        for item in file_method(src, dst):
            paths.append(item)

        assert len(paths) == 2

        new_file = paths.pop(-1)
        result = paths[0]

        assert isinstance(new_file, File)
        assert isinstance(result, Path)

        assert new_file.path is result
        assert new_file.path == dst / src.path.name

        assert src.path.exists() if src_remains else not src.path.exists()
        assert new_file.path.exists()

        print("Source Dir ls:")
        for i, x in enumerate(src.path.parent.iterdir(), 1):
            print(f"{i}: {x}")

        print("-----------")

        print("Destination Dir ls:")
        for i, x in enumerate(dst.iterdir(), 1):
            print(f"{i}: {x}")

    @pytest.mark.parametrize(
        "file_method,src_remains", [(File.move, False), (File.copy, True)]
    )
    def test_copy_move(self, file_method, single_file_for_operation, src_remains):
        src: File
        dst: Path

        src, dst = single_file_for_operation

        new_file = file_method(src, dst)

        assert isinstance(new_file, File)
        assert new_file.path == dst / src.path.name

        assert src.path.exists() if src_remains else not src.path.exists()
        assert new_file.path.exists()

        print("Source Dir ls:")
        for i, x in enumerate(src.path.parent.iterdir(), 1):
            print(f"{i}: {x}")

        print("-----------")

        print("Destination Dir ls:")
        for i, x in enumerate(dst.iterdir(), 1):
            print(f"{i}: {x}")

    @pytest.mark.parametrize("use_iter", [True, False])
    def test_rename(self, single_file_for_operation, use_iter):
        src: File
        dst: Path

        src, dst = single_file_for_operation

        print("Original Dir List")
        for x in src.path.parent.iterdir():
            print(x)

        print("------------------")

        assert src.path.exists()

        if use_iter:
            for item in src.rename_iter("new_name.dpx"):
                try:
                    path_old, path_new = item
                    print(f"{path_old} -> {path_new}")
                except ValueError:
                    file_new = item
                else:
                    assert isinstance(path_old, Path)
                    assert isinstance(path_new, Path)
                    assert path_old.name != "new_name.dpx"
                    assert path_new.name == "new_name.dpx"
                    assert path_new.parent == path_old.parent

                    assert not path_old.exists()
                    assert path_new.exists()

            assert file_new.path is path_new
            assert src.path is path_old
        else:
            file_new = src.rename("new_name.dpx")

        print("------------------")

        print("Post-rename Dir List")
        for x in src.path.parent.iterdir():
            print(x)

        assert file_new.path.parent == src.path.parent
        assert file_new.path.name == "new_name.dpx"

        assert not src.path.exists()
        assert file_new.path.exists()

    @pytest.mark.parametrize("use_iter", [True, False])
    def test_delete(self, single_file_for_operation, use_iter):
        src: File
        dst: Path

        src, dst = single_file_for_operation
        assert src.path.exists()

        if use_iter:
            for item in src.delete_iter():
                print(f"deleted: {item}")
                assert isinstance(item, Path)
        else:
            src.delete()

        assert not src.path.exists()
        assert len([x for x in src.path.parent.iterdir()]) == 0

        print("--------")

        print("Source Dir ls:")
        for i, x in enumerate(src.path.parent.iterdir(), 1):
            print(f"{i}: {x}")

    @pytest.mark.parametrize("use_iter", [True, False])
    def test_chmod(self, single_file_for_operation, use_iter):
        src: File
        dst: Path

        src, dst = single_file_for_operation
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
            assert src.path.stat().st_mode != original_mode
            for path in src:
                assert stat.S_IMODE(path.stat().st_mode) == 0o777
