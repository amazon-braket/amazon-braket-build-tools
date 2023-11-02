def function_0(arg0: str, *, arg1: int = 0, arg2: int = 1, arg3: int = 1) -> int:
    """This is a description.
    Args:
        arg0 (str): This is a parameter
        arg2 (bool): This is another parameter
        arg3: This is yet another parameter
    Returns:
        int: value of the function.
    """
    pass


def function_1(arg0: str, *, arg1 = 0, arg2: int = 1, arg3: int = 1) -> int:
    """This is a description.
    Args:
        arg0 (str): This is a parameter
        arg1 (bool): This is missing a type hint
        arg2 (int): This is another parameter
        arg3 (int): This is yet another parameter
    Returns:
        int: value of the function.
    """
    pass


def function_2(arg0: str, *, a0: int, a1: str | None = None, a2: str = None, a3: str | None = None) -> int:  # noqa
    """This is a description.
    Args:
        arg0 (str): This is a parameter
        a0 (int): This is a parameter
        a1 (str|None): This is an optional parameter
        a2 (str): This is an optional parameter missing optional type hint
        a3 (str|None): This is an optional parameter
    Returns:
        int: value of the function
    """
    pass


def function_3(arg0: str, *, a0: int, a1: str) -> int:
    """This is a description.
    Args:
        arg0 (str): This is a parameter
        a0 (int): This is a keyword parameter
        a1 (str): This is a keyword parameter
    Returns:
        int: value of the function
    """
    pass