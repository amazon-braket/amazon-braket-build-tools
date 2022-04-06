# Copyright Amazon.com Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from unittest.mock import ANY, Mock

import astroid
import pylint.testutils
from utils_for_testing import read_file

import braket.pylint_plugins.braket_checkstyle_checker as checker

FILE_PATH = "example_files"


class TestBraketCheckstyleChecker(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = checker.BraketCheckstyleChecker

    def test_register(self):
        mock_linter = Mock()
        checker.register(mock_linter)
        mock_linter.register_checker.assert_called_once()

    def test_finds_missing_type_hints(self):
        node = astroid.extract_node(read_file(f"{FILE_PATH}/simple_functions.py"))

        with self.assertAddsMessages(
            pylint.testutils.MessageTest(
                msg_id='missing-type-hint',
                node=ANY,
                args="my_param",
                line=4,
                col_offset=9,
                end_line=None,
                end_col_offset=None
            ),
            pylint.testutils.MessageTest(
                msg_id='argument-doc-missing-type-hint',
                node=node,
                args="my_param",
                line=4,
                col_offset=0,
                end_line=4,
                end_col_offset=8
            ),
            pylint.testutils.MessageTest(
                msg_id='argument-doc-type-hint-mismatch',
                node=node,
                args=("my_param_3", "int", "bool"),
                line=4,
                col_offset=0,
                end_line=4,
                end_col_offset=8
            ),
            pylint.testutils.MessageTest(
                msg_id='return-doc-type-hint-missing',
                node=node,
                args=("test", "int"),
                line=4,
                col_offset=0,
                end_line=4,
                end_col_offset=8
            ),
        ):
            self.checker.visit_functiondef(node)

    def test_class_functions(self):
        node, func_node = astroid.extract_node(read_file(f"{FILE_PATH}/class_functions.py"))

        with self.assertAddsMessages(
                pylint.testutils.MessageTest(
                    msg_id='missing-type-hint',
                    node=func_node.args.args[1],
                    args="my_param",
                    line=5,
                    col_offset=19,
                    end_line=None,
                    end_col_offset=None
                ),
                pylint.testutils.MessageTest(
                    msg_id='argument-doc-missing-type-hint',
                    node=func_node,
                    args="my_param",
                    line=5,
                    col_offset=4,
                    end_line=5,
                    end_col_offset=12
                ),
                pylint.testutils.MessageTest(
                    msg_id='unknown-argument-in-doc',
                    node=func_node,
                    args="my_param_4",
                    line=5,
                    col_offset=4,
                    end_line=5,
                    end_col_offset=12
                ),
                pylint.testutils.MessageTest(
                    msg_id='argument-doc-type-hint-mismatch',
                    node=func_node,
                    args=("my_param_3", "int", "bool"),
                    line=5,
                    col_offset=4,
                    end_line=5,
                    end_col_offset=12
                ),
                pylint.testutils.MessageTest(
                    msg_id='argument-doc-missing-description',
                    node=func_node,
                    args="my_param_3",
                    line=5,
                    col_offset=4,
                    end_line=5,
                    end_col_offset=12
                ),
                pylint.testutils.MessageTest(
                    msg_id='argument-doc-multiple-times',
                    node=func_node,
                    args="my_param_2",
                    line=5,
                    col_offset=4,
                    end_line=5,
                    end_col_offset=12
                ),
                pylint.testutils.MessageTest(
                    msg_id='return-doc-type-hint-mismatch',
                    node=func_node,
                    args=("test", "int", "List"),
                    line=5,
                    col_offset=4,
                    end_line=5,
                    end_col_offset=12
                ),
                pylint.testutils.MessageTest(
                    msg_id='argument-doc-missing',
                    node=func_node,
                    args="my_param5",
                    line=5,
                    col_offset=4,
                    end_line=5,
                    end_col_offset=12
                ),
        ):
            self.checker.visit_functiondef(func_node)

    def test_complex_types(self):
        node = astroid.extract_node(read_file(f"{FILE_PATH}/complex_types.py"))

        with self.assertAddsMessages(
                pylint.testutils.MessageTest(
                    msg_id='argument-doc-type-hint-mismatch',
                    node=node,
                    args=('a2', 'Optional[Union[MyA,MyB]]', 'Optional[List[MyA,MyB]]'),
                    line=12,
                    col_offset=0,
                    end_line=12,
                    end_col_offset=11
                ),
                pylint.testutils.MessageTest(
                    msg_id='missing-function-doc-description',
                    node=node,
                    args="my_func",
                    line=12,
                    col_offset=0,
                    end_line=12,
                    end_col_offset=11
                ),
        ):
            self.checker.visit_functiondef(node)

    def test_more_complex_types(self):
        node = astroid.extract_node(read_file(f"{FILE_PATH}/more_types.py"))

        with self.assertAddsMessages(
                pylint.testutils.MessageTest(
                    msg_id='argument-doc-out-of-order',
                    node=node,
                    args='a2',
                    line=12,
                    col_offset=0,
                    end_line=12,
                    end_col_offset=11
                ),
                pylint.testutils.MessageTest(
                    msg_id='argument-doc-out-of-order',
                    node=node,
                    args='a1',
                    line=12,
                    col_offset=0,
                    end_line=12,
                    end_col_offset=11
                ),
                pylint.testutils.MessageTest(
                    msg_id='return-doc-type-hint-missing',
                    node=node,
                    args=('my_func', 'ndarray'),
                    line=12,
                    col_offset=0,
                    end_line=12,
                    end_col_offset=11
                ),
                pylint.testutils.MessageTest(
                    msg_id='argument-doc-missing',
                    node=node,
                    args='a0',
                    line=12,
                    col_offset=0,
                    end_line=12,
                    end_col_offset=11
                ),
                pylint.testutils.MessageTest(
                    msg_id='invalid-doc-indent',
                    node=node,
                    args=(1, 'This is not ind...'),
                    line=12,
                    col_offset=0,
                    end_line=12,
                    end_col_offset=11
                ),
        ):
            self.checker.visit_functiondef(node)

    def test_no_return_type(self):
        node = astroid.extract_node(read_file(f"{FILE_PATH}/no_return_type.py"))

        with self.assertAddsMessages(
                pylint.testutils.MessageTest(
                    msg_id='redundant-function-doc-return',
                    node=node,
                    args='__my_function__',
                    line=1,
                    col_offset=0,
                    end_line=1,
                    end_col_offset=19
                ),
        ):
            self.checker.visit_functiondef(node)

    def test_missing_return_type(self):
        node = astroid.extract_node(read_file(f"{FILE_PATH}/missing_return_type.py"))

        with self.assertAddsMessages(
                pylint.testutils.MessageTest(
                    msg_id='missing-return-type-hint',
                    node=node,
                    args='my_function',
                    line=1,
                    col_offset=0,
                    end_line=1,
                    end_col_offset=19
                ),
        ):
            self.checker.visit_functiondef(node)

    def test_line_formatting_in_docs(self):
        node = astroid.extract_node(read_file(f"{FILE_PATH}/line_formatting.py"))

        with self.assertAddsMessages(
                pylint.testutils.MessageTest(
                    msg_id='invalid-doc-indent',
                    node=node,
                    args=(3, 'a1'),
                    line=4,
                    col_offset=0,
                    end_line=4,
                    end_col_offset=8
                ),
        ):
            self.checker.visit_functiondef(node)

    def test_missing_function_doc(self):
        node = astroid.extract_node(read_file(f"{FILE_PATH}/missing_doc.py"))

        with self.assertAddsMessages(
                pylint.testutils.MessageTest(
                    msg_id='missing-function-doc',
                    node=node,
                    args="my_function",
                    line=1,
                    col_offset=0,
                    end_line=1,
                    end_col_offset=12
                ),
        ):
            self.checker.visit_functiondef(node)

    def test_missing_doc_parts(self):
        node = astroid.extract_node(read_file(f"{FILE_PATH}/missing_doc_parts.py"))

        with self.assertAddsMessages(
                pylint.testutils.MessageTest(
                    msg_id='missing-function-doc-args',
                    node=node,
                    args="function_0",
                    line=1,
                    col_offset=0,
                    end_line=1,
                    end_col_offset=14
                ),
                pylint.testutils.MessageTest(
                    msg_id='missing-function-doc-return',
                    node=node,
                    args="function_0",
                    line=1,
                    col_offset=0,
                    end_line=1,
                    end_col_offset=14
                ),
        ):
            self.checker.visit_functiondef(node)

    def test_redundant_doc_parts(self):
        node = astroid.extract_node(read_file(f"{FILE_PATH}/redundant_doc_parts.py"))

        with self.assertAddsMessages(
                pylint.testutils.MessageTest(
                    msg_id='unknown-argument-in-doc',
                    node=node,
                    args="my_param",
                    line=1,
                    col_offset=0,
                    end_line=1,
                    end_col_offset=14
                ),
                pylint.testutils.MessageTest(
                    msg_id='redundant-function-doc-args',
                    node=node,
                    args="function_0",
                    line=1,
                    col_offset=0,
                    end_line=1,
                    end_col_offset=14
                ),
        ):
            self.checker.visit_functiondef(node)

    def test_doc_wrong_order(self):
        node = astroid.extract_node(read_file(f"{FILE_PATH}/doc_wrong_order.py"))

        with self.assertAddsMessages(
                pylint.testutils.MessageTest(
                    msg_id='function-doc-wrong-order',
                    node=node,
                    args="function_0",
                    line=1,
                    col_offset=0,
                    end_line=1,
                    end_col_offset=14
                ),
        ):
            self.checker.visit_functiondef(node)

    def test_doc_duplicate_sections(self):
        node = astroid.extract_node(read_file(f"{FILE_PATH}/doc_duplicate_sections.py"))

        with self.assertAddsMessages(
                pylint.testutils.MessageTest(
                    msg_id='function-doc-args-duplicate',
                    node=node,
                    args="function_0",
                    line=1,
                    col_offset=0,
                    end_line=1,
                    end_col_offset=14
                ),
                pylint.testutils.MessageTest(
                    msg_id='function-doc-return-duplicate',
                    node=node,
                    args="function_0",
                    line=1,
                    col_offset=0,
                    end_line=1,
                    end_col_offset=14
                ),
                pylint.testutils.MessageTest(
                    msg_id='invalid-doc-indent',
                    node=node,
                    args=(3, 'Args'),
                    line=1,
                    col_offset=0,
                    end_line=1,
                    end_col_offset=14
                ),
        ):
            self.checker.visit_functiondef(node)

    def test_return_missing_description(self):
        node = astroid.extract_node(read_file(f"{FILE_PATH}/missing_description.py"))

        with self.assertAddsMessages(
                pylint.testutils.MessageTest(
                    msg_id='return-doc-missing-description',
                    node=node,
                    args="function_0",
                    line=1,
                    col_offset=0,
                    end_line=1,
                    end_col_offset=14
                ),
        ):
            self.checker.visit_functiondef(node)

    def test_unhandled_types(self):
        node = astroid.extract_node(read_file(f"{FILE_PATH}/unhandled_types.py"))

        with self.assertAddsMessages(
            pylint.testutils.MessageTest(
                msg_id='argument-doc-type-hint-mismatch',
                node=ANY,
                args=('a0', '', 'NewType'),
                line=4,
                col_offset=0,
                end_line=4,
                end_col_offset=14
            ),
        ):
            self.checker.visit_functiondef(node)

    def test_functions_with_no_errors(self):
        nodes = astroid.extract_node(read_file(f"{FILE_PATH}/no_error_functions.py"))

        for node in nodes:
            with self.assertAddsMessages():
                self.checker.visit_functiondef(node)
