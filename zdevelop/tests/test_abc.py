import pytest

from perfsprocket import FileABC, FileBase, NameABC


@pytest.mark.parametrize(
    "class_type,method,args,kwargs",
    [
        # FileABC
        (FileABC, "__iter__", tuple(), dict()),
        (FileABC, "__len__", tuple(), dict()),
        (FileABC, "__repr__", tuple(), dict()),
        (FileABC, "move_iter", ("/path/file.txt",), dict()),
        (FileABC, "move", ("/path/file.txt",), dict()),
        (FileABC, "copy_iter", ("/path/file.txt",), dict()),
        (FileABC, "copy", ("/path/file.txt",), dict()),
        (FileABC, "rename_iter", ("file.txt",), dict()),
        (FileABC, "rename", ("file.txt",), dict()),
        (FileABC, "delete_iter", tuple(), dict()),
        (FileABC, "delete", tuple(), dict()),
        (FileABC, "chmod_iter", (0o777,), dict()),
        (FileABC, "chmod", (0o777,), dict()),
        # FileBase
        (FileBase, "__iter__", tuple(), dict()),
        (FileBase, "__len__", tuple(), dict()),
        (FileBase, "init_new", ("/path/file.txt",), dict()),
        (FileBase, "rename_iter", ("file.txt",), dict()),
        # NameABC
        (NameABC, "from_path", ("/path/file.txt",), dict()),
        (NameABC, "alter", tuple(), dict()),
        (NameABC, "formatted", tuple(), dict()),
    ],
)
def test_not_implemented(class_type, method, args, kwargs):
    class NonImplemented(class_type):
        def __init__(self):
            pass

    test_object = NonImplemented()

    with pytest.raises(NotImplementedError):
        getattr(test_object, method)(*args, **kwargs)
