from typing import List, Optional, Tuple, Union


class MyA:
    pass


class MyB:
    pass


def my_func(a0: int, a1: Tuple[int, ...], a2: Optional[Union[MyA, MyB]] = None, a3: Optional[Union[MyA, MyB]] = None) -> List[List[int]]: #@
    """
    Args:
        a0 (int): This is an int.
        a1 (Tuple[int, ...]): This is an tuple with ints.
        a2 (Optional[List[MyA, MyB]]): This is inconsistent with parameter.
        a3 (Optional[Union[MyA, MyB]]): This is correct. Default: None
    Returns:
        List[List[int]]: This is a complex return
    """
    pass