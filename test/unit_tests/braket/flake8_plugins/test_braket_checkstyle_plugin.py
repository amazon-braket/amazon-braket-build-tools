import ast
from typing import Set

import pytest
from utils_for_testing import read_file

from braket.flake8_plugins.braket_checkstyle_plugin import BraketCheckstylePlugin

FILE_PATH = "example_files"


def _results(text: str) -> Set[str]:
    tree = ast.parse(text)
    plugin = BraketCheckstylePlugin(tree)
    return {f"{line}:{col} {msg}" for line, col, msg, _ in plugin.run()}


def test_no_error_functions() -> None:
    """Test various functions which should not cause any errors."""
    file = read_file(f"{FILE_PATH}/no_error_functions.py")
    assert _results(file) == set()


@pytest.mark.parametrize(
    "filename, error_set",
    [
        (
            "simple_functions.py",
            {
                "4:0 BCS004 - Argument 'my_param' documentation is missing the type hint.",
                "4:0 BCS005 - Argument 'my_param_4' type hint doesn't match documentation. expected: 'int', documented as: 'bool'.",  # noqa
                "4:0 BCS006 - Function 'test' doesn't specify a return type in the documentation. expected: 'int'.",  # noqa
                "4:19 BCS001 - Argument 'my_param_2' is missing a type hint.",
                "4:9 BCS001 - Argument 'my_param' is missing a type hint.",
            },
        ),
        (
            "missing_return_type.py",
            {"1:0 BCS002 - Function 'my_function' is missing a type hint for the return value."},
        ),
        (
            "missing_doc.py",
            {
                "4:0 BCS003 - Function 'my_function' is missing documentation.",
                "9:0 BCS023 - Argument 'a2' defaults to None but type hint doesn't end with '| None'.",  # noqa
            },
        ),
        (
            "class_functions.py",
            {
                "5:19 BCS001 - Argument 'my_param' is missing a type hint.",
                "5:4 BCS004 - Argument 'my_param' documentation is missing the type hint.",
                "5:4 BCS005 - Argument 'my_param_3' type hint doesn't match documentation. expected: 'int', documented as: 'bool'.",  # noqa
                "5:4 BCS007 - Unknown documented argument 'my_param_4'.",
                "5:4 BCS008 - Argument 'my_param_3' is missing a description.",
                "5:4 BCS009 - Argument 'my_param_2' is specified more than once.",
                "5:4 BCS010 - Function 'test' return type hint doesn't match documentation. expected: 'int', documented as: 'List'.",  # noqa
                "5:4 BCS011 - Argument 'my_param5' is missing type hint documentation.",
            },
        ),
        (
            "unhandled_types.py",
            {
                "4:0 BCS005 - Argument 'a0' type hint doesn't match documentation. expected: '', documented as: 'NewType'."  # noqa
            },  # noqa
        ),
        (
            "complex_types.py",
            {
                "12:0 BCS005 - Argument 'a2' type hint doesn't match documentation. expected: 'Optional[Union[MyA,MyB]]', documented as: 'Optional[List[MyA,MyB]]'.",  # noqa
                "12:0 BCS017 - Function 'my_func' is missing function description documentation.",
            },
        ),
        (
            "doc_duplicate_sections.py",
            {
                "1:0 BCS012 - Function 'function_0' argument and return documentation has duplicate argument definitions.",  # noqa
                "1:0 BCS014 - Function 'function_0' argument and return documentation has duplicate return definitions.",  # noqa
                "1:0 BCS022 - Found '3' invalid indents starting with line ('Args').",
            },
        ),
        (
            "doc_wrong_order.py",
            {"1:0 BCS013 - Function 'function_0' has documented sections in the wrong order"},
        ),
        (
            "more_types.py",
            {
                "12:0 BCS006 - Function 'my_func' doesn't specify a return type in the documentation. expected: 'ndarray'.",  # noqa
                "12:0 BCS011 - Argument 'a0' is missing type hint documentation.",
                "12:0 BCS015 - Argument 'a1' is out of order.",
                "12:0 BCS015 - Argument 'a2' is out of order.",
                "12:0 BCS022 - Found '1' invalid indents starting with line ('This is not ind...').",  # noqa
            },
        ),
        (
            "missing_description.py",
            {"1:0 BCS016 - Return doc for function 'function_0' is missing the description."},
        ),
        (
            "missing_doc_parts.py",
            {
                "1:0 BCS018 - Function 'function_0' is missing argument documentation.",
                "1:0 BCS021 - Function 'function_0' is missing return documentation.",
            },
        ),
        (
            "redundant_doc_parts.py",
            {
                "1:0 BCS007 - Unknown documented argument 'my_param'.",
                "1:0 BCS019 - Function 'function_0' has argument documentation but no arguments.",
            },
        ),
        (
            "no_return_type.py",
            {
                "1:0 BCS020 - Function '__my_function__' has return documentation but no return type."  # noqa
            },
        ),
        (
            "line_formatting.py",
            {"4:0 BCS022 - Found '3' invalid indents starting with line ('a1')."},
        ),
        (
            "keyword_functions.py",
            {
                "13:29 BCS001 - Argument 'arg1' is missing a type hint.",
                "1:0 BCS004 - Argument 'arg3' documentation is missing the type hint.",
                "1:0 BCS005 - Argument 'arg2' type hint doesn't match documentation. expected: 'int', documented as: 'bool'.",  # noqa
                "1:0 BCS011 - Argument 'arg1' is missing type hint documentation.",
                "1:0 BCS015 - Argument 'arg2' is out of order.",
                "26:0 BCS023 - Argument 'a2' defaults to None but type hint doesn't end with '| None'.",  # noqa
            },
        ),
    ],
)
def test_functions(filename: str, error_set: Set[str]) -> None:
    """Test various files and validate the expected error set.
    Args:
        filename (str): The file name containing the functions to test.
        error_set (Set[str]): The expected errors.
    """
    file = read_file(f"{FILE_PATH}/{filename}")
    assert _results(file) == error_set
