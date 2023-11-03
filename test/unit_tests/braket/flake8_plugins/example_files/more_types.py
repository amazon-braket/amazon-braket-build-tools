from typing import Callable, Optional, Union


class MyA:
    pass


class MyB:
    pass


def my_func(a0: int, a1: Callable[[Union[MyA, str]], MyA] | None = None, a2: Optional[MyB] = None) -> np.ndarray:
    """This is a description.
    Args:
        a2 (Optional[MyB]): This is out of order.
        a1 (Callable[[Union[MyA, str]], MyA] | None): This is out of order.
    Returns:
          This is not indented correctly, and doesn't have the return type.
    """
    pass
