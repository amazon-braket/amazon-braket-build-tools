import os


def read_file(path: str) -> str:
    local_dir = os.path.dirname(__file__)
    source_file = os.path.join(local_dir, path)
    with open(source_file) as file:
        return file.read()

