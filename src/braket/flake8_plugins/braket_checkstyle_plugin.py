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

import ast
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Generator, Optional, Set, Tuple, Type

import braket._build_tools._version as build_tools_version


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


class _Visitor(ast.NodeVisitor):
    ARGS_REGEX = re.compile(r"^(\s*)Args\s*:\s*$")
    RETURN_REGEX = re.compile(r"^(\s*)(Returns|Yields)\s*:\s*$")
    MISC_REGEX = re.compile(
        r"^(\s*)(Throws|Raises|See Also|Note|Example|Examples|Warnings)\s*:\s*$"
    )
    ARG_INFO_REGEX = re.compile(r"^(\s*)(`?\*{0,2}\w*`?)\s*(\([^:]*\))?\s*:\s*(.*)")
    RETURN_INFO_REGEX = re.compile(r"^(\s*)([^:]*)\s*(:)?\s*(.*)")
    INDENT_REGEX = re.compile(r"^(\s*)\S+.*")
    RESERVED_ARGS = {"self", "cls"}

    MESSAGES = {
        "BCS001": "Argument '%s' is missing a type hint.",
        "BCS002": "Function '%s' is missing a type hint for the return value.",
        "BCS003": "Function '%s' is missing documentation.",
        "BCS004": "Argument '%s' documentation is missing the type hint.",
        "BCS005": "Argument '%s' type hint doesn't match documentation. expected: '%s', documented as: '%s'.",  # noqa
        "BCS006": "Function '%s' doesn't specify a return type in the documentation. expected: '%s'.",  # noqa
        "BCS007": "Unknown documented argument '%s'.",
        "BCS008": "Argument '%s' is missing a description.",
        "BCS009": "Argument '%s' is specified more than once.",
        "BCS010": "Function '%s' return type hint doesn't match documentation. expected: '%s', documented as: '%s'.",  # noqa
        "BCS011": "Argument '%s' is missing type hint documentation.",
        "BCS012": "Function '%s' argument and return documentation has duplicate argument definitions.",
        "BCS013": "Function '%s' has documented sections in the wrong order",
        "BCS014": "Function '%s' argument and return documentation has duplicate return definitions.",
        "BCS015": "Argument '%s' is out of order.",
        "BCS016": "Return doc for function '%s' is missing the description.",
        "BCS017": "Function '%s' is missing function description documentation.",
        "BCS018": "Function '%s' is missing argument documentation.",
        "BCS019": "Function '%s' has argument documentation but no arguments.",
        "BCS020": "Function '%s' has return documentation but no return type.",
        "BCS021": "Function '%s' is missing return documentation.",
        "BCS022": "Found '%d' invalid indents starting with line ('%s').",
    }

    def __init__(self) -> None:
        self.problems = []

    def add_problem(self, node: ast.AST, code: str, arguments: Any):
        message = self.MESSAGES[code] % arguments
        self.problems.append([node.lineno, node.col_offset, f"{code} - {message}"])

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self._check_arguments(node.name, node.args)
        self._check_return(node)
        self._check_documentation(node)
        self.generic_visit(node)

    def _check_arguments(self, name: str, args: ast.arguments) -> None:
        if name.startswith("__") or name == "_":
            return
        for argument in args.args:
            if argument.annotation is None:
                if argument.arg not in self.RESERVED_ARGS:
                    self.add_problem(node=argument, code="BCS001", arguments=argument.arg)

    def _check_return(self, node: ast.FunctionDef) -> None:
        if not node.returns and not node.name.startswith("__") and node.name != "_":
            self.add_problem(node=node, code="BCS002", arguments=node.name)

    def _check_documentation(self, node: ast.FunctionDef) -> None:
        doc = _get_first_doc(node)
        if doc is None:
            if _function_requires_documentation(node):
                self.add_problem(node=node, code="BCS003", arguments=node.name)
            return
        doc_lines = doc.s.split("\n")
        context = DocContext()
        for doc_line in doc_lines:
            self._check_doc_line(doc_line, context, node)
        self._verify_context(context, node)

    def _check_doc_line(self, doc_line: str, context: DocContext, node: ast.FunctionDef) -> None:
        if self._check_doc_args(doc_line, context, node):
            return
        if self._check_doc_return(doc_line, context, node):
            return
        if self._check_doc_misc(doc_line, context, node):
            return
        self._check_doc_section(doc_line, context, node)

    def _verify_context(self, context: DocContext, node: ast.FunctionDef) -> None:
        self._verify_description(context, node)
        self._verify_args(context, node)
        self._verify_return(context, node)
        self._verify_indents(context, node)

    def _check_doc_args(self, doc_line: str, context: DocContext, node: ast.FunctionDef) -> bool:
        match = self.ARGS_REGEX.match(doc_line)
        if match:
            if context.found_args:
                self.add_problem(node=node, code="BCS012", arguments=node.name)
                return False
            if context.found_return:
                self.add_problem(node=node, code="BCS013", arguments=node.name)
            context.found_args = True
            context.args_indent = 4 if match.groups()[0] is None else len(match.groups()[0]) + 4
            context.current_section = DocSection.ARGUMENTS
            return True
        return False

    def _check_doc_return(self, doc_line: str, context: DocContext, node: ast.FunctionDef) -> bool:
        match = self.RETURN_REGEX.match(doc_line)
        if match:
            if context.found_return:
                self.add_problem(node=node, code="BCS014", arguments=node.name)
                return False
            context.found_return = True
            context.return_indent = 4 if match.groups()[0] is None else len(match.groups()[0]) + 4
            context.current_section = DocSection.RETURN_FIRST_LINE
            return True
        return False

    def _check_doc_misc(self, doc_line: str, context: DocContext, _: ast.FunctionDef) -> bool:
        if self.MISC_REGEX.match(doc_line):
            context.current_section = DocSection.MISC
            return True
        return False

    def _check_doc_section(self, doc_line: str, context: DocContext, node: ast.FunctionDef) -> None:
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
        self, regex_matches: re.Match, context: DocContext, node: ast.FunctionDef
    ) -> None:
        arg_indent = regex_matches.group(1)
        arg_name = regex_matches.group(2).strip("`") if regex_matches.group(2) else None
        arg_type = regex_matches.group(3) if regex_matches.group(3) else None
        arg_description = regex_matches.group(4)
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
        node: ast.FunctionDef,
    ) -> None:
        if len(arg_indent) == context.args_indent:
            if arg_index is None and arg_name and not arg_name.startswith("*"):
                self.add_problem(node=node, code="BCS007", arguments=arg_name)
        elif len(arg_indent) != context.args_indent + 4:
            _invalid_indent_found(arg_name, context)

    def _check_argument_docs(
        self,
        arg_name: str,
        arg_type: str,
        arg_description: str,
        arg_index: int,
        context: DocContext,
        node: ast.FunctionDef,
    ) -> None:
        if context.found_arg_list is None:
            context.found_arg_list = {arg_index}
        elif arg_index in context.found_arg_list:
            self.add_problem(node=node, code="BCS009", arguments=arg_name)
            return
        else:
            context.found_arg_list.add(arg_index)
        if context.current_arg == 0 and arg_index != context.current_arg:
            if node.args.args[0].arg in self.RESERVED_ARGS:
                context.current_arg = 1
        if arg_index != context.current_arg:
            self.add_problem(node=node, code="BCS015", arguments=arg_name)
        if arg_type is None:
            self.add_problem(node=node, code="BCS004", arguments=arg_name)
        elif node.args.args[arg_index].annotation:
            documented_type = _remove_all_spaces(arg_type[1:-1])
            annotation_doc = _remove_all_spaces(
                self._annotation_to_doc_str(node.args.args[arg_index].annotation)
            )
            if not _are_type_strings_same(annotation_doc, documented_type):
                self.add_problem(
                    node=node,
                    code="BCS005",
                    arguments=(arg_name, annotation_doc, documented_type),
                )

        if (arg_description is None or len(arg_description.strip()) < 2) and (
            len(arg_name) + len(arg_type) < 70
        ):
            self.add_problem(node=node, code="BCS008", arguments=arg_name)

    # flake8: noqa: C901
    def _annotation_to_doc_str(self, annotation) -> str:
        if isinstance(annotation, ast.Name):
            return annotation.id
        if isinstance(annotation, ast.Attribute):
            return annotation.attr
        if isinstance(annotation, ast.Subscript):
            if isinstance(annotation.value, ast.Name):
                if isinstance(annotation.slice, ast.Index):
                    slice_name = self._annotation_to_doc_str(annotation.slice.value)
                else:
                    # This is done to be backward compatible. May not be able to hit it with
                    # usual test coverage.
                    slice_name = self._annotation_to_doc_str(annotation.slice)
                return annotation.value.id + f"[{slice_name}]"
        elif isinstance(annotation, (ast.List, ast.Tuple)):
            values = []
            for elt in annotation.elts:
                if isinstance(elt, ast.Name):
                    values.append(elt.id)
                else:
                    values.append(self._annotation_to_doc_str(elt))
            result = ",".join(values)
            if isinstance(annotation, ast.List):
                return f"[{result}]"
            return result
        elif isinstance(annotation, ast.Ellipsis):
            return "..."
        return ""

    def _check_return_info(
        self, regex_matches: re.Match, context: DocContext, node: ast.FunctionDef
    ) -> None:
        return_indent, documented_type, colon, return_description = regex_matches.groups()
        if return_indent is not None and len(return_indent) != context.return_indent:
            _invalid_indent_found(documented_type, context)
        if colon is None:
            return_description = documented_type
            documented_type = None
        has_documentation = return_description is not None and len(return_description.strip()) > 1
        if node.returns and not has_documentation:
            self.add_problem(node=node, code="BCS016", arguments=node.name)
        if node.returns:
            return_doc = _remove_all_spaces(self._annotation_to_doc_str(node.returns))
            if documented_type is None:
                self.add_problem(node=node, code="BCS006", arguments=(node.name, return_doc))
            else:
                documented_type = _remove_all_spaces(documented_type)
                if not _are_type_strings_same(return_doc, documented_type):
                    self.add_problem(
                        node=node,
                        code="BCS010",
                        arguments=(node.name, return_doc, documented_type),
                    )

    def _verify_description(self, context: DocContext, node: ast.FunctionDef) -> None:
        if not context.found_description and _function_requires_documentation(node):
            self.add_problem(node=node, code="BCS017", arguments=node.name)

    def _verify_args(self, context: DocContext, node: ast.FunctionDef) -> None:
        if not context.found_args:
            if self._function_has_arguments_to_document(node) and _function_requires_documentation(
                node
            ):
                self.add_problem(node=node, code="BCS018", arguments=node.name)
            return
        if (
            not self._function_has_arguments_to_document(node)
            and node.args.kwarg is None
            and node.args.vararg is None
        ):
            self.add_problem(node=node, code="BCS019", arguments=node.name)
            return
        if context.found_arg_list:
            for index, arg in enumerate(node.args.args):
                if index not in context.found_arg_list and arg.arg not in self.RESERVED_ARGS:
                    self.add_problem(node=node, code="BCS011", arguments=arg.arg)

    def _verify_return(self, context: DocContext, node: ast.FunctionDef) -> None:
        if context.found_return:
            if not node.returns:
                self.add_problem(node=node, code="BCS020", arguments=node.name)
        else:
            if _function_requires_documentation(node) and _return_type_requires_documentation(node):
                self.add_problem(node=node, code="BCS021", arguments=node.name)

    def _verify_indents(self, context: DocContext, node: ast.FunctionDef) -> None:
        if context.invalid_indents > 0:
            self.add_problem(
                node=node,
                code="BCS022",
                arguments=(context.invalid_indents, context.first_invalid_indent_line),
            )

    def _function_has_arguments_to_document(self, node: ast.FunctionDef) -> bool:
        if not node.args or not node.args.args:
            return False
        for args in node.args.args:
            if args.arg not in self.RESERVED_ARGS:
                return True
        return False

    def _check_indent(self, expected_indent: int, line: str, context: DocContext) -> None:
        match = self.INDENT_REGEX.match(line)
        if match:
            indent = match.groups()[0]
            if indent is not None and len(indent) != expected_indent:
                _invalid_indent_found(line, context)


class BraketCheckstylePlugin:
    name = __name__
    version = build_tools_version.__version__
    off_by_default = True

    def __init__(self, tree: ast.AST) -> None:
        self._tree = tree

    def run(self) -> Generator[Tuple[int, int, str, Type[Any]], None, None]:
        visitor = _Visitor()
        visitor.visit(self._tree)
        for line, col, msg in visitor.problems:
            yield line, col, msg, type(self)


def _get_first_doc(node: ast.FunctionDef):
    for body_node in node.body:
        if isinstance(body_node, ast.Expr) and isinstance(body_node.value, ast.Str):
            return body_node.value
    return None


def _get_argument_with_name(arg_name: str, node: ast.FunctionDef) -> Optional[int]:
    for index, arg in enumerate(node.args.args):
        if arg_name == arg.arg:
            return index
    return None


def _function_requires_documentation(node: ast.FunctionDef) -> bool:
    if node.name.startswith("_"):
        return False
    if node.body is None or len(node.body) == 0:
        return False
    for body_node in node.body:
        if not isinstance(body_node, (ast.Expr, ast.Return, ast.Raise)):
            return True
    return False


def _return_type_requires_documentation(node: ast.FunctionDef) -> bool:
    if not node.returns:
        return False
    if isinstance(node.returns, ast.NameConstant):
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
