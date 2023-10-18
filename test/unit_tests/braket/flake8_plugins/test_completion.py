import ast
from unittest.mock import Mock

import pytest

from braket.flake8_plugins.braket_checkstyle_plugin import (
    _return_type_requires_documentation,
    _Visitor,
)


def test_check_annotation_invalid_annotation_type():
    visitor = _Visitor()
    visitor._check_annotation("test", "test", 0, None, Mock())
    assert visitor.problems == []


def test_annotation_to_doc_str_subscript_annotation_index():
    annotation = Mock(spec=ast.Subscript)
    annotation.value = Mock(spec=ast.Name)
    annotation.value.id = "Annotation ID"
    annotation.slice = Mock(spec=ast.Index)
    annotation.slice.value = Mock(spec=ast.Name)
    annotation.slice.value.id = "Slice ID"
    visitor = _Visitor()
    result = visitor._annotation_to_doc_str(annotation)
    assert result == "Annotation ID[Slice ID]"


def test_annotation_to_doc_str_subscript_backward_compatibility():
    annotation = Mock(spec=ast.Subscript)
    annotation.value = Mock(spec=ast.Name)
    annotation.value.id = "Annotation ID"
    annotation.slice = Mock(spec=ast.Name)
    annotation.slice.id = "Slice ID"
    visitor = _Visitor()
    result = visitor._annotation_to_doc_str(annotation)
    assert result == "Annotation ID[Slice ID]"


def test_annotation_to_doc_str_subscript_unhandled():
    annotation = Mock(spec=ast.Subscript)
    annotation.value = Mock(spec=ast.Attribute)
    visitor = _Visitor()
    with pytest.raises(NotImplementedError):
        visitor._annotation_to_doc_str(annotation)


def test_annotation_to_doc_str_binop_unhandled():
    annotation = Mock(spec=ast.BinOp)
    annotation.op = Mock(spec=ast.BitXor)
    visitor = _Visitor()
    with pytest.raises(NotImplementedError):
        visitor._annotation_to_doc_str(annotation)


def test_return_type_requires_documentation():
    return_type = Mock()
    return_type.returns = None
    result = _return_type_requires_documentation(return_type)
    assert not result
