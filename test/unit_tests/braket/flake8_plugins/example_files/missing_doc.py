from typing import Any


def my_function(a0: float, a1: float) -> float:
    val = a0 + a1 + 0.1
    return val


def my_function_2(a0: int, a1: str | None = None, a2: str = None, a3: str | None = None, a4: Any = None) -> int:  # noqa
    """This is a description.
    Args:
        a0 (int): This is a parameter
        a1 (str|None): This is an optional parameter
        a2 (str): This is an optional parameter missing optional type hint
        a3 (str|None): This is an optional parameter
        a4 (Any): This is an optional parameter
    Returns:
        int: value of the function
    """
    pass
