def function_0() -> None:
    """This is a description without a return."""
    pass


def function_1(a0: int) -> np.ndarray:
    """This is a description.
    Args:
        a0 (int): This is a parameter
    Returns:
        numpy.ndarray: This is an attribute return type that is also acceptable
    """
    pass


def function_2() -> int:
    return 1


def __function_3__():
    """This is a function with no return type."""
    pass


def function_4(a0:int, *args, **kwargs) -> np.ndarray:
    """This is a description.
    Args:
        a0 (int): This is a parameter
    Returns:
        ndarray: This is an attribute return type that is also acceptable
    """
    pass


def function_5(a0:int, *args, **kwargs) -> np.ndarray:
    """This is a description.
    Args:
        a0 (int): This is a parameter
    Returns:
        ndarray: This is an attribute return type that is also acceptable
    Raises:
        ValueError: my value error
    """
    pass


def __function6__(a0) -> str:
    pass


def function_7(some_reall_long_argument_name: areallyreallyreallyreallyreallyreallyreallyreallylongtype) -> None:
    """This is a description.
    Args:
        some_reall_long_argument_name (areallyreallyreallyreallyreallyreallyreallyreallylongtype):
            This is a parameter description on a new line.
    """
    pass


def function_8(a0:int, *a1:list) -> None:
    """This is a description.
    Args:
        a0 (int): This is a parameter
        *a1 (list): This is a parameter list
    """
    val = 1
    pass


def function_9(*my_args, **my_kwargs) -> np.ndarray:
    """This is a description.
    Args:
        *my_args: Arguments that are described here.
        **my_kwargs: Keyword arguments that are described here.
    Returns:
        ndarray: This is an attribute return type that is also acceptable
    Raises:
        ValueError: my value error
    """
    pass


def function_10(a0:int, *a1:list) -> None:
    """This is a description.
    Args:
        a0 (int): This is a parameter
        `*a1` (list): This is a parameter list
    """
    val = 1
    pass


def function_11(*my_args, **my_kwargs) -> np.ndarray:
    """This is a description.
    Args:
        `*my_args`: Arguments that are described here.
        `**my_kwargs`: Keyword arguments that are described here.
    Returns:
        ndarray: This is an attribute return type that is also acceptable
    Raises:
        ValueError: my value error
    """
    pass

class MyClass:
    def __init__(self, a0:int):
        """
        Args:
            a0 (int): First param.
        """
        hey = 1
        pass

    def function_6(self) -> int:
        """This function has does not document any arguments
        Returns:
            int: This function returns an int
        """
        pass

    def cancel(self) -> None:
        raise NotImplementedError("Cannot cancel completed local task")
