import pytest
from pathlib import Path
from unittest import mock
from dataclasses import fields, Field

from perfsprocket import ARROW, PAREN, BRACKET, CURLY, SeqName, Braces, FileName, KEEP
from perfsprocket._file_name import (
    _num_end_from_match,
    _padding_from_match,
    _brackets_from_match,
    _format_range_pieces,
    _format_file_nums,
    _run_filename_regex,
    _extract_pieces_from_str,
    _post_init_start_end,
)


@pytest.mark.parametrize(
    "bracket,open_char,close_char,enclosed",
    [
        (ARROW, "<", ">", "<text>"),
        (PAREN, "(", ")", "(text)"),
        (BRACKET, "[", "]", "[text]"),
        (CURLY, "{", "}", "{text}"),
    ],
)
def test_brackets(bracket: Braces, open_char: str, close_char: str, enclosed: str):
    assert bracket.open == open_char
    assert bracket.close == close_char
    assert bracket.enclose("text") == enclosed


class TestHelpers:
    @pytest.mark.parametrize(
        "group_dict,answer", [({"end": None}, None), ({"end": "10"}, 10)]
    )
    def test_num_end_from_match(self, group_dict, answer):
        assert _num_end_from_match(group_dict) == answer

    @pytest.mark.parametrize(
        "group_dict,answer",
        [
            ({"start": "010", "end": "012"}, 3),
            ({"start": "010", "end": None}, 3),
            ({"start": "10", "end": "100"}, 2),
        ],
    )
    def test_padding_from_match(self, group_dict, answer):
        assert _padding_from_match(group_dict) == answer

    @pytest.mark.parametrize(
        "group_dict,answer",
        [
            ({"open": "[", "close": "]"}, BRACKET),
            ({"open": "{", "close": "}"}, CURLY),
            ({"open": "<", "close": ">"}, ARROW),
            ({"open": "(", "close": ")"}, PAREN),
        ],
    )
    def test_brackets_from_match(self, group_dict, answer):
        assert _brackets_from_match(group_dict) == answer

    @pytest.mark.parametrize(
        "group_dict",
        [
            {"open": "#", "close": "#"},
            {"open": "(", "close": "]"},
            {"open": "(", "close": None},
            {"open": None, "close": "}"},
        ],
    )
    def test_brackets_from_match_raises(self, group_dict):
        with pytest.raises(ValueError):
            _brackets_from_match(group_dict)

    @pytest.mark.parametrize(
        "brackets,end_num,answer_open,answer_close,answer_range_sep",
        [
            (None, None, "", "", ""),
            (BRACKET, None, "", "", ""),
            (None, 100, "", "", "-"),
            (BRACKET, 100, "[", "]", "-"),
            (PAREN, 100, "(", ")", "-"),
        ],
    )
    def test_format_range_pieces(
        self, brackets, end_num, answer_open, answer_close, answer_range_sep
    ):
        mock_name = mock.Mock()
        mock_name.configure_mock(brackets=brackets, end=end_num)

        open_bracket, close_bracket, range_sep = _format_range_pieces(mock_name)
        assert open_bracket == answer_open
        assert close_bracket == answer_close
        assert range_sep == answer_range_sep

    @pytest.mark.parametrize(
        "start,end,padding,answer_start,answer_end",
        [
            (100, None, 0, "100", ""),
            (1, 100, 0, "1", "100"),
            (1, 100, 4, "0001", "0100"),
            (1, 10000, 4, "0001", "10000"),
        ],
    )
    def test_format_file_nums(self, start, end, padding, answer_start, answer_end):
        mock_name = mock.Mock()
        mock_name.configure_mock(start=start, end=end, pad=padding)

        start_str, end_str = _format_file_nums(mock_name)
        assert start_str == answer_start
        assert end_str == answer_end

    @pytest.mark.parametrize(
        "text",
        [
            "file.10.exr",
            "file.#.exr",
            "file.#######.exr",
            "file_10.exr",
            "file.001",
            "file.010.exr",
            "file_010.exr",
            "file.000010.exr",
            "file_000010.exr",
            "file_#.exr",
            "file_#######.exr",
            "file.10-11.exr",
            "file_10-11.exr",
            "file.010-011.exr",
            "file_010-011.exr",
            "file_#-#.exr",
            "file_#######-#######.exr",
            "file.000010-000011.exr",
            "file.#-#.exr",
            "file.#######-#######.exr",
            "file.[010-011].exr",
            "file.[#-#].exr",
            "file.[#######-#######].exr",
            "file_[010-011].exr",
            "file_[#-#].exr",
            "file_[#######-#######].exr",
            "file.{010-011}.exr",
            "file_{010-011}.exr",
            "file.(010-011).exr",
            "file_(010-011).exr",
            "file.<010-011>.exr",
            "file_<010-011>.exr",
        ],
    )
    def test_regex_passes(self, text):
        mock_path = mock.Mock()
        mock_path.configure_mock(name=text)
        result = _run_filename_regex(mock_path)
        print(result)
        assert isinstance(result, dict)

    @pytest.mark.parametrize(
        "text",
        [
            "file.mov",
            "file001",
            "file10.exr",
            "file010.exr",
            "file.#thing.exr",
            "file.##010.exr",
            "file.####-##thing.exr",
            "file.[####-##thing].exr",
        ],
    )
    def test_regex_fails(self, text):
        mock_path = mock.Mock()
        mock_path.configure_mock(name=text)
        with pytest.raises(ValueError):
            result = _run_filename_regex(mock_path)
            print(result)

    @pytest.mark.parametrize(
        "text,piece_name,answer",
        [
            # name
            ("file.001.exr", "name", "file"),
            ("file.001.exr", "sep", "."),
            ("file.001.exr", "start", 1),
            ("file.001.exr", "num_end", None),
            ("file.001.exr", "padding", 3),
            ("file.001.exr", "brackets", None),
            ("file.001.exr", "extension", ".exr"),
            # name
            ("file.#.exr", "name", "file"),
            ("file.#.exr", "sep", "."),
            ("file.#.exr", "start", "#"),
            ("file.#.exr", "num_end", None),
            ("file.#.exr", "padding", 1),
            ("file.#.exr", "brackets", None),
            ("file.#.exr", "extension", ".exr"),
            # name
            ("file.###.exr", "name", "file"),
            ("file.###.exr", "sep", "."),
            ("file.###.exr", "start", "#"),
            ("file.###.exr", "num_end", None),
            ("file.###.exr", "padding", 3),
            ("file.###.exr", "brackets", None),
            ("file.###.exr", "extension", ".exr"),
            # name
            ("file_001.exr", "name", "file"),
            ("file_001.exr", "sep", "_"),
            ("file_001.exr", "start", 1),
            ("file_001.exr", "num_end", None),
            ("file_001.exr", "padding", 3),
            ("file_001.exr", "brackets", None),
            ("file_001.exr", "extension", ".exr"),
            # name
            ("file_001", "name", "file"),
            ("file_001", "sep", "_"),
            ("file_001", "start", 1),
            ("file_001", "num_end", None),
            ("file_001", "padding", 3),
            ("file_001", "brackets", None),
            ("file_001", "extension", None),
            # name
            ("file_thing.test.010.exr", "name", "file_thing.test"),
            ("file_thing.test.010.exr", "sep", "."),
            ("file_thing.test.010.exr", "start", 10),
            ("file_thing.test.010.exr", "num_end", None),
            ("file_thing.test.010.exr", "padding", 3),
            ("file_thing.test.010.exr", "brackets", None),
            ("file_thing.test.010.exr", "extension", ".exr"),
            # name
            ("file_thing.test.010", "name", "file_thing.test"),
            ("file_thing.test.010", "sep", "."),
            ("file_thing.test.010", "start", 10),
            ("file_thing.test.010", "num_end", None),
            ("file_thing.test.010", "padding", 3),
            ("file_thing.test.010", "brackets", None),
            ("file_thing.test.010", "extension", None),
            # name
            ("file.001-010.exr", "name", "file"),
            ("file.001-010.exr", "sep", "."),
            ("file.001-010.exr", "start", 1),
            ("file.001-010.exr", "num_end", 10),
            ("file.001-010.exr", "padding", 3),
            ("file.001-010.exr", "brackets", None),
            ("file.001-010.exr", "extension", ".exr"),
            # name
            ("file.###-###.exr", "name", "file"),
            ("file.###-###.exr", "sep", "."),
            ("file.###-###.exr", "start", "#"),
            ("file.###-###.exr", "num_end", "#"),
            ("file.###-###.exr", "padding", 3),
            ("file.###-###.exr", "brackets", None),
            ("file.###-###.exr", "extension", ".exr"),
            # name
            ("file.[001-010].exr", "name", "file"),
            ("file.[001-010].exr", "sep", "."),
            ("file.[001-010].exr", "start", 1),
            ("file.[001-010].exr", "num_end", 10),
            ("file.[001-010].exr", "padding", 3),
            ("file.[001-010].exr", "brackets", BRACKET),
            ("file.[001-010].exr", "extension", ".exr"),
            # name
            ("file.[###-###].exr", "name", "file"),
            ("file.[###-###].exr", "sep", "."),
            ("file.[###-###].exr", "start", "#"),
            ("file.[###-###].exr", "num_end", "#"),
            ("file.[###-###].exr", "padding", 3),
            ("file.[###-###].exr", "brackets", BRACKET),
            ("file.[###-###].exr", "extension", ".exr"),
            # name
            ("file.[001-010]", "name", "file"),
            ("file.[001-010]", "sep", "."),
            ("file.[001-010]", "start", 1),
            ("file.[001-010]", "num_end", 10),
            ("file.[001-010]", "padding", 3),
            ("file.[001-010]", "brackets", BRACKET),
            ("file.[001-010]", "extension", None),
            # name
            ("file_[100-110].dpx.[001-010].exr", "name", "file_[100-110].dpx"),
            ("file_[100-110].dpx.[001-010].exr", "sep", "."),
            ("file_[100-110].dpx.[001-010].exr", "start", 1),
            ("file_[100-110].dpx.[001-010].exr", "num_end", 10),
            ("file_[100-110].dpx.[001-010].exr", "padding", 3),
            ("file_[100-110].dpx.[001-010].exr", "brackets", BRACKET),
            ("file_[100-110].dpx.[001-010].exr", "extension", ".exr"),
            # name
            ("file_100.dpx.[001-010].exr", "name", "file_100.dpx"),
            ("file_100.dpx.[001-010].exr", "sep", "."),
            ("file_100.dpx.[001-010].exr", "start", 1),
            ("file_100.dpx.[001-010].exr", "num_end", 10),
            ("file_100.dpx.[001-010].exr", "padding", 3),
            ("file_100.dpx.[001-010].exr", "brackets", BRACKET),
            ("file_100.dpx.[001-010].exr", "extension", ".exr"),
        ],
    )
    def test_extract_pieces(self, text, piece_name, answer):
        mock_path = mock.Mock()
        mock_path.configure_mock(name=text)

        pieces = "name", "sep", "start", "num_end", "padding", "brackets", "extension"
        index = pieces.index(piece_name)

        result = _extract_pieces_from_str(mock_path)
        assert result[index] == answer

    @pytest.mark.parametrize(
        "value,answer", [(1, 1), (342, 342), ("#", "#"), ("##", "#"), (None, None)]
    )
    def test_post_init_start_end(self, value, answer):
        assert _post_init_start_end(value) == answer


class TestFileName:
    @pytest.mark.parametrize(
        "base,ext,answer",
        [
            ("file", "txt", "file.txt"),
            ("file", ".txt", "file.txt"),
            ("file", None, "file"),
        ],
    )
    def test_print(self, base, ext, answer):
        assert str(FileName(base, ext)) == answer

    @pytest.mark.parametrize(
        "base,ext,answer_base,answer_ext",
        [
            ("new", ".txt", "new", ".txt"),
            ("new", None, "new", None),
            ("new", KEEP, "new", ".ext"),
            (KEEP, KEEP, "base", ".ext"),
            (KEEP, "txt", "base", ".txt"),
        ],
    )
    def test_alter(self, base, ext, answer_base, answer_ext):
        name = FileName("base", ".ext").alter(base=base, extension=ext)
        assert name.base == answer_base
        assert name.extension == answer_ext


class TestSequenceName:
    def test_init_defaults(self):
        seq_name = SeqName("file_name", ".exr")
        assert seq_name.base == "file_name"
        assert seq_name.extension == ".exr"
        assert seq_name.delim == "."
        assert seq_name.start == "#"
        assert seq_name.end is None
        assert seq_name.pad == 0
        assert seq_name.brackets is None

    def test_add_extension_period(self):
        assert SeqName("file_name", "exr").extension == ".exr"

    def test_extension_none(self):
        assert SeqName("file_name", None).extension is None

    @pytest.mark.parametrize(
        "path, start, end, brackets",
        [
            ("file_name.[01-20].exr", 1, 20, BRACKET),
            ("file_name.01.exr", 1, None, None),
            ("file_name.##.exr", "#", None, None),
            (Path("/Volumes/drive/folder/file_name.[01-20].exr"), 1, 20, BRACKET),
            (Path("/Volumes/drive/folder/file_name.[##-##].exr"), "#", "#", BRACKET),
        ],
    )
    def test_from_path(self, path, start, end, brackets):
        seq_name = SeqName.from_path(path)
        assert seq_name.base == "file_name"
        assert seq_name.delim == "."
        assert seq_name.start == start
        assert seq_name.end == end
        assert seq_name.pad == 2
        assert seq_name.brackets is brackets
        assert seq_name.extension == ".exr"

    def from_path_override_padding(self):
        seq_name = SeqName.from_path("file_name.1234567.exr")
        assert seq_name.pad == 7

        seq_name = SeqName.from_path("file_name.1234567.exr", pad=0)
        assert seq_name.pad == 0

    @pytest.mark.parametrize(
        "answer,base,ext,delim,start,end,pad,brackets",
        [
            ("file.001.exr", "file", ".exr", ".", 1, None, 3, None),
            ("file.###.exr", "file", ".exr", ".", "#", None, 3, None),
            ("file_001.exr", "file", ".exr", "_", 1, None, 3, None),
            ("file_0000001.exr", "file", ".exr", "_", 1, None, 7, None),
            ("file.1.exr", "file", ".exr", ".", 1, None, 0, None),
            ("file.001", "file", None, ".", 1, None, 3, None),
            ("file.001-010.exr", "file", ".exr", ".", 1, 10, 3, None),
            ("file.###-###.exr", "file", ".exr", ".", "#", "#", 3, None),
            ("file.[001-010].exr", "file", ".exr", ".", 1, 10, 3, BRACKET),
            ("file.<001-010>.exr", "file", ".exr", ".", 1, 10, 3, ARROW),
        ],
    )
    def test_format_string(self, answer, base, ext, delim, start, end, pad, brackets):
        seq_name = SeqName(
            base=base,
            extension=ext,
            delim=delim,
            start=start,
            end=end,
            pad=pad,
            brackets=brackets,
        )
        assert seq_name.formatted() == answer
        assert str(seq_name) == answer

    @pytest.mark.parametrize(
        "changes_dict",
        [
            {"start": 200},
            {"start": 200, "end": 210},
            {"base": "file2"},
            {"base": "file2", "extension": None},
        ],
    )
    def test_alter_seq_name(self, changes_dict):
        this_field: Field

        original = SeqName(base="file", extension="exr", start=100)
        new = original.alter(**changes_dict)

        print(f"org: {original}\nnew: {new}\nchanges:{changes_dict}")

        for this_field in fields(original):
            try:
                value = changes_dict[this_field.name]
            except KeyError:
                value = getattr(original, this_field.name)

            assert getattr(new, this_field.name) == value

    def test_alter_extension_adds_period(self):
        original = SeqName(base="file", extension="exr", start=100)
        new = original.alter(extension="dpx")
        print(f"new_extension: {new.extension}")
        assert new.extension == ".dpx"

    def test_is_frozen(self):
        seq_name = SeqName("name", "exr")
        with pytest.raises(AttributeError):
            seq_name.base = "file"
