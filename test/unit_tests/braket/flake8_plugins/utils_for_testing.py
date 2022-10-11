import os


def read_file(path: str) -> str:
    """Reads a file from a path and returns the contents as a string
    Args:
        path (str): The file name to read.
    Returns:
        str: The contents of the file.
    """
    local_dir = os.path.dirname(__file__)
    source_file = os.path.join(local_dir, path)
    with open(source_file) as file:
        return file.read()
