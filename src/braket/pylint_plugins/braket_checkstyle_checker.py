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

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Set

from astroid import Attribute, Const, List, Name, NodeNG, Return, Subscript, Tuple, nodes
from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker
from pylint.lint import PyLinter


def register(linter: PyLinter) -> None:
    """This required method auto registers the checker during initialization.

    Args:
        linter(PyLinter): The linter to register the checker to.
    """
    linter.register_checker(BraketCheckstyleChecker(linter))


class DocSection(str, Enum):
    DESCRIPTION = "DESCRIPTION"
    ARGUMENTS = "ARGUMENTS"
    RETURN_FIRST_LINE = "RETURN_FIRST_LINE"
    RETURN_REST = "RETURN_REST"
    MISC = "MISC"


@dataclass
class DocContext:
    """
    This is the context object for parsing the function definition. We record all the information
    we need about the function and the current state of parsing.
    """

    # pylint: disable=too-many-instance-attributes
    found_args: bool = False
    found_return: bool = False
    found_description: bool = False
    current_section: DocSection = DocSection.DESCRIPTION
    current_arg: int = 0
    found_arg_list: Set = None
    args_indent: int = 0
    return_indent: int = 0
    invalid_indents: int = 0
    first_invalid_indent_line: str = None


class BraketCheckstyleChecker(BaseChecker):
    """
    This is a pylint checker for Braket code style guidelines. For more informaiton about
    pylint checkers, see: https://pylint.pycqa.org/en/latest/how_tos/custom_checkers.html
    """

    # pylint: disable=line-too-long
    __implements__ = IAstroidChecker

    name = "braket-documentation"
    priority = -1
    msgs = {
        "W0001": (
            "parameter '%s' is missing a type hint.",
            "missing-type-hint",
            "All parameters should have a type hint.",
        ),
        "W0002": (
            "function '%s' is missing a type hint for the return value.",
            "missing-return-type-hint",
            "Function should have a type hint for the return value.",
        ),
        "W0003": (
            "function '%s' is missing documentation.",
            "missing-function-doc",
            "All public functions should have documentation.",
        ),
        "W0004": (
            "function '%s' is missing function description documentation.",
            "missing-function-doc-description",
            "All public functions should have function description documentation.",
        ),
        "W0005": (
            "function '%s' is missing argument documentation.",
            "missing-function-doc-args",
            "All public functions should have argument documentation.",
        ),
        "W0006": (
            "function '%s'  has argument documentation but no arguments.",
            "redundant-function-doc-args",
            "Functions with no arguments should not have argument documentation.",
        ),
        "W0007": (
            "function '%s' is missing return documentation.",
            "missing-function-doc-return",
            "All public functions should have return documentation.",
        ),
        "W0008": (
            "function '%s' has return documentation but no return type.",
            "redundant-function-doc-return",
            "Functions with no return should not have return documentation.",
        ),
        "W0009": (
            "function '%s' has documented sections in the wrong order.",
            "function-doc-wrong-order",
            "Argument documentation should be specified before return documentation.",
        ),
        "W0010": (
            "function '%s' argument and return documentation has duplicate argument definitions.",
            "function-doc-args-duplicate",
            "All public functions should only document the arguments in one place.",
        ),
        "W0011": (
            "function '%s' argument and return documentation has duplicate return definitions.",
            "function-doc-return-duplicate",
            "All public functions should only document the return values in one place.",
        ),
        "W0012": (
            "unknown documented argument '%s'.",
            "unknown-argument-in-doc",
            "Documented arguments should be in the function signature.",
        ),
        "W0013": (
            "argument '%s' is out of order.",
            "argument-doc-out-of-order",
            "Documented arguments should be specified in the same order as the function definition.",  # noqa
        ),
        "W0014": (
            "argument '%s' is missing the type hint.",
            "argument-doc-missing-type-hint",
            "Documented arguments should contain type hints.",
        ),
        "W0015": (
            "argument '%s' is missing the description.",
            "argument-doc-missing-description",
            "Documented arguments should contain descriptions.",
        ),
        "W0016": (
            "argument '%s' is specified more than once.",
            "argument-doc-multiple-times",
            "Arguments should only be documented once.",
        ),
        "W0017": (
            "argument '%s' is not documented.",
            "argument-doc-missing",
            "All arguments should be documented.",
        ),
        "W0018": (
            "argument '%s' type hint doesn't match documentation. expected: '%s', documented as: '%s'.",  # noqa
            "argument-doc-type-hint-mismatch",
            "Documented arguments should contain type hints matching function arguments.",
        ),
        "W0019": (
            "return doc for function '%s' is missing the description.",
            "return-doc-missing-description",
            "Functions should have documented return types when they return data.",
        ),
        "W0020": (
            "function '%s' return type hint doesn't match documentation. expected: '%s', documented as: '%s'.",  # noqa
            "return-doc-type-hint-mismatch",
            "Documented return type should contain type hints matching function return type.",
        ),
        "W0021": (
            "function '%s' doesn't specify a return in the documentation. expected: '%s'.",
            "return-doc-type-hint-missing",
            "Functions should document the return type.",
        ),
        "W0022": (
            "found '%d' invalid indents starting with line ('%s').",
            "invalid-doc-indent",
            "Functions that document a return type should specify a return type hint.",
        ),
    }

    ARGS_REGEX = re.compile(r"^(\s*)Args\s*:\s*$")
    RETURN_REGEX = re.compile(r"^(\s*)(Returns|Yields)\s*:\s*$")
    MISC_REGEX = re.compile(r"^(\s*)(Throws|Raises|See also|Example|Examples)\s*:\s*$")
    ARG_INFO_REGEX = re.compile(r"^(\s*)(\w*)\s*(\([^:]*\))?\s*:\s*(.*)")
    RETURN_INFO_REGEX = re.compile(r"^(\s*)([^:]*)\s*(:)?\s*(.*)")
    INDENT_REGEX = re.compile(r"^(\s*)\S+.*")
    RESERVED_ARGS = {"self", "cls"}

    def __init__(self, linter: PyLinter = None) -> None:
        super().__init__(linter)
        self._function_stack = []

    def visit_functiondef(self, node: nodes.FunctionDef) -> None:
        """Handle visiting a function definition.
        Args:
            node (FunctionDef): The astroid AST node for a function definition.
        """
        self._check_arguments(node.args)
        self._check_return(node)
        self._check_documentation(node)

    def _check_arguments(self, args: nodes.Arguments) -> None:
        for index, argument in enumerate(args.annotations):
            if argument is None:
                arg_name = args.args[index].name
                if arg_name not in self.RESERVED_ARGS:
                    self.add_message("missing-type-hint", node=args.args[index], args=arg_name)

    def _check_return(self, node: nodes.FunctionDef) -> None:
        if not node.returns and not node.name.startswith("__") and node.name != "_":
            self.add_message("missing-return-type-hint", node=node, args=node.name)

    def _check_documentation(self, node: nodes.FunctionDef) -> None:
        if node.doc_node is None or not isinstance(node.doc_node, Const):
            if _function_requires_documentation(node):
                self.add_message("missing-function-doc", node=node, args=node.name)
            return
        doc_lines = node.doc_node.value.split("\n")
        context = DocContext()
        for doc_line in doc_lines:
            self._check_doc_line(doc_line, context, node)
        self._verify_context(context, node)

    def _check_doc_line(self, doc_line: str, context: DocContext, node: nodes.FunctionDef) -> None:
        if self._check_doc_args(doc_line, context, node):
            return
        if self._check_doc_return(doc_line, context, node):
            return
        if self._check_doc_misc(doc_line, context, node):
            return
        self._check_doc_section(doc_line, context, node)

    def _verify_context(self, context: DocContext, node: nodes.FunctionDef) -> None:
        self._verify_description(context, node)
        self._verify_args(context, node)
        self._verify_return(context, node)
        self._verify_indents(context, node)

    def _check_doc_args(self, doc_line: str, context: DocContext, node: nodes.FunctionDef) -> bool:
        match = self.ARGS_REGEX.match(doc_line)
        if match:
            if context.found_args:
                self.add_message("function-doc-args-duplicate", node=node, args=node.name)
                return False
            if context.found_return:
                self.add_message("function-doc-wrong-order", node=node, args=node.name)
            context.found_args = True
            context.args_indent = 4 if match.groups()[0] is None else len(match.groups()[0]) + 4
            context.current_section = DocSection.ARGUMENTS
            return True
        return False

    def _check_doc_return(
        self, doc_line: str, context: DocContext, node: nodes.FunctionDef
    ) -> bool:
        match = self.RETURN_REGEX.match(doc_line)
        if match:
            if context.found_return:
                self.add_message("function-doc-return-duplicate", node=node, args=node.name)
                return False
            context.found_return = True
            context.return_indent = 4 if match.groups()[0] is None else len(match.groups()[0]) + 4
            context.current_section = DocSection.RETURN_FIRST_LINE
            return True
        return False

    def _check_doc_misc(self, doc_line: str, context: DocContext, _: nodes.FunctionDef) -> bool:
        if self.MISC_REGEX.match(doc_line):
            context.current_section = DocSection.MISC
            return True
        return False

    def _check_doc_section(
        self, doc_line: str, context: DocContext, node: nodes.FunctionDef
    ) -> None:
        if context.current_section == DocSection.DESCRIPTION:
            if len(doc_line.strip()) > 1:
                context.found_description = True
        elif context.current_section == DocSection.ARGUMENTS:
            matches = self.ARG_INFO_REGEX.match(doc_line)
            if matches:
                self._check_argument_info(matches, context, node)
            else:
                self._check_indent(context.args_indent + 4, doc_line, context)
        elif context.current_section == DocSection.RETURN_FIRST_LINE:
            matches = self.RETURN_INFO_REGEX.match(doc_line)
            self._check_return_info(matches, context, node)
            context.current_section = DocSection.RETURN_REST
        elif context.current_section == DocSection.RETURN_REST:
            self._check_indent(context.return_indent, doc_line, context)

    def _check_argument_info(
        self, regex_matches: re.Match, context: DocContext, node: nodes.FunctionDef
    ) -> None:
        arg_indent, arg_name, arg_type, arg_description = regex_matches.groups()
        arg_index = _get_argument_with_name(arg_name, node)
        self._check_argument_indent(arg_indent, arg_name, arg_index, context, node)
        if arg_index is None:
            return
        self._check_argument_docs(arg_name, arg_type, arg_description, arg_index, context, node)
        context.current_arg = arg_index + 1

    def _check_argument_indent(
        self,
        arg_indent: str,
        arg_name: str,
        arg_index: int,
        context: DocContext,
        node: nodes.FunctionDef,
    ) -> None:
        if len(arg_indent) == context.args_indent:
            if arg_index is None:
                self.add_message("unknown-argument-in-doc", node=node, args=arg_name)
        elif len(arg_indent) != context.args_indent + 4:
            _invalid_indent_found(arg_name, context)

    def _check_argument_docs(
        self,
        arg_name: str,
        arg_type: str,
        arg_description: str,
        arg_index: int,
        context: DocContext,
        node: nodes.FunctionDef,
    ) -> None:
        if context.found_arg_list is None:
            context.found_arg_list = {arg_index}
        elif arg_index in context.found_arg_list:
            self.add_message("argument-doc-multiple-times", node=node, args=arg_name)
            return
        else:
            context.found_arg_list.add(arg_index)
        if context.current_arg == 0 and arg_index != context.current_arg:
            if node.args.args[0].name in self.RESERVED_ARGS:
                context.current_arg = 1
        if arg_index != context.current_arg:
            self.add_message("argument-doc-out-of-order", node=node, args=arg_name)
        if arg_type is None:
            self.add_message("argument-doc-missing-type-hint", node=node, args=arg_name)
        elif node.args.annotations[arg_index]:
            documented_type = _remove_all_spaces(arg_type[1:-1])
            annotation_doc = _remove_all_spaces(
                self._annotation_to_doc_str(node.args.annotations[arg_index])
            )
            if not _are_type_strings_same(annotation_doc, documented_type):
                self.add_message(
                    "argument-doc-type-hint-mismatch",
                    node=node,
                    args=(arg_name, annotation_doc, documented_type),
                )

        if arg_description is None or len(arg_description.strip()) < 2:
            self.add_message("argument-doc-missing-description", node=node, args=arg_name)

    # flake8: noqa: C901
    def _annotation_to_doc_str(self, annotation: NodeNG) -> str:
        if isinstance(annotation, Name):
            return annotation.name
        if isinstance(annotation, Attribute):
            return annotation.attrname
        if isinstance(annotation, Subscript):
            if isinstance(annotation.value, Name):
                slice_name = self._annotation_to_doc_str(annotation.slice)
                return annotation.value.name + f"[{slice_name}]"
        elif isinstance(annotation, (List, Tuple)):
            values = []
            for elt in annotation.elts:
                if isinstance(elt, Name):
                    values.append(elt.name)
                else:
                    values.append(self._annotation_to_doc_str(elt))
            result = ",".join(values)
            if isinstance(annotation, List):
                return f"[{result}]"
            return result
        elif isinstance(annotation, Const):
            if annotation.value == Ellipsis:
                return "..."
        return ""

    def _check_return_info(
        self, regex_matches: re.Match, context: DocContext, node: nodes.FunctionDef
    ) -> None:
        return_indent, documented_type, colon, return_description = regex_matches.groups()
        if return_indent is not None and len(return_indent) != context.return_indent:
            _invalid_indent_found(documented_type, context)
        if colon is None:
            return_description = documented_type
            documented_type = None
        has_documentation = return_description is not None and len(return_description.strip()) > 1
        if node.returns and not has_documentation:
            self.add_message("return-doc-missing-description", node=node, args=(node.name))
        if node.returns:
            return_doc = _remove_all_spaces(self._annotation_to_doc_str(node.returns))
            if documented_type is None:
                self.add_message(
                    "return-doc-type-hint-missing", node=node, args=(node.name, return_doc)
                )
            else:
                documented_type = _remove_all_spaces(documented_type)
                if not _are_type_strings_same(return_doc, documented_type):
                    self.add_message(
                        "return-doc-type-hint-mismatch",
                        node=node,
                        args=(node.name, return_doc, documented_type),
                    )

    def _verify_description(self, context: DocContext, node: nodes.FunctionDef) -> None:
        if not context.found_description and _function_requires_documentation(node):
            self.add_message("missing-function-doc-description", node=node, args=node.name)

    def _verify_args(self, context: DocContext, node: nodes.FunctionDef) -> None:
        if not context.found_args:
            if self._function_has_arguments_to_document(node):
                self.add_message("missing-function-doc-args", node=node, args=node.name)
            return
        if not self._function_has_arguments_to_document(node):
            self.add_message("redundant-function-doc-args", node=node, args=node.name)
            return
        if context.found_arg_list:
            for index, arg in enumerate(node.args.args):
                if index not in context.found_arg_list and arg.name not in self.RESERVED_ARGS:
                    self.add_message("argument-doc-missing", node=node, args=arg.name)

    def _verify_return(self, context: DocContext, node: nodes.FunctionDef) -> None:
        if context.found_return:
            if not node.returns:
                self.add_message("redundant-function-doc-return", node=node, args=node.name)
        else:
            if _function_requires_documentation(node) and _return_type_requires_documentation(node):
                self.add_message("missing-function-doc-return", node=node, args=node.name)

    def _verify_indents(self, context: DocContext, node: nodes.FunctionDef) -> None:
        if context.invalid_indents > 0:
            self.add_message(
                "invalid-doc-indent",
                node=node,
                args=(context.invalid_indents, context.first_invalid_indent_line),
            )

    def _function_has_arguments_to_document(self, node: nodes.FunctionDef) -> bool:
        if not node.args or not node.args.args:
            return False
        for args in node.args.args:
            if args.name not in self.RESERVED_ARGS:
                return True
        return False

    def _check_indent(self, expected_indent: int, line: str, context: DocContext) -> None:
        match = self.INDENT_REGEX.match(line)
        if match:
            indent = match.groups()[0]
            if indent is not None and len(indent) != expected_indent:
                _invalid_indent_found(line, context)


def _get_argument_with_name(arg_name: str, node: nodes.FunctionDef) -> Optional[int]:
    for index, arg in enumerate(node.args.args):
        if arg_name == arg.name:
            return index
    return None


def _function_requires_documentation(node: nodes.FunctionDef) -> bool:
    if node.name.startswith("_"):
        return False
    if node.body is not None and len(node.body) == 1 and isinstance(node.body[0], Return):
        return False
    return True


def _return_type_requires_documentation(node: nodes.FunctionDef) -> bool:
    if not node.returns:
        return False
    if isinstance(node.returns, Const):
        return node.returns.value is not None
    return True


def _invalid_indent_found(line: str, context: DocContext) -> None:
    if context.invalid_indents == 0:
        line = line.strip()
        if len(line) > 18:
            line = line[:15] + "..."
        context.first_invalid_indent_line = line
    context.invalid_indents = context.invalid_indents + 1


def _remove_all_spaces(string: str) -> str:
    return re.sub(r"\s+", "", string)


def _are_type_strings_same(annotated_type: str, documented_type: str) -> bool:
    if annotated_type == documented_type:
        return True
    param_split = documented_type.split(".")
    if len(param_split) > 1:
        return annotated_type == param_split[-1]
    return False
