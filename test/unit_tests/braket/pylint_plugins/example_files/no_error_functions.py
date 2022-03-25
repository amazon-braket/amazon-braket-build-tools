def function_0() -> None: #@
    """This is a description without a return."""
    pass


def function_1(a0: int) -> np.ndarray: #@
    """This is a description.
    Args:
        a0 (int): This is a parameter
    Returns:
        numpy.ndarray: This is an attribute return type that is also acceptable
    """
    pass


def function_2() -> int: #@
    return 1


def __function_3__(): #@
    """This is a function with no return type."""
    pass


def function_4(a0:int, *args, **kwargs) -> np.ndarray: #@
    """This is a description.
    Args:
        a0 (int): This is a parameter
    Returns:
        ndarray: This is an attribute return type that is also acceptable
    """
    pass


def function_5(a0:int, *args, **kwargs) -> np.ndarray: #@
    """This is a description.
    Args:
        a0 (int): This is a parameter
    Returns:
        ndarray: This is an attribute return type that is also acceptable
    Raises:
        ValueError: my value error
    """
    pass


class MyClass:
    def function_6(self) -> int:  #@
        """This function has does not document any arguments
        Returns:
            int: This function returns an int
        """
        pass
