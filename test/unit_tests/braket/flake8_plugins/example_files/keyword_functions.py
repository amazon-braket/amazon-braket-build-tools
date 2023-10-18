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