from typing import IO as _IO
from collections.abc import Callable, Generator
from importlib.resources import Anchor
from contextlib import contextmanager
import importlib.resources as pkg

__all__ = (
    "make_file_opener",
    "make_string_opener",
    "make_binary_opener",
    "make_path_finder"
)

type IO = _IO[bytes] | _IO[str]

def make_file_opener(
        anchor: Anchor,
        data_extension: str,
        _mode: str = "r",
        _buffering: int = -1,
        _encoding: str | None = None,
        _errors: str | None = None,
        _newline: str | None = None,
        _closefd: bool = True,
        _opener: Callable[[str, int], int] | None = None
        ) -> Callable[[str, tuple[str, ...], str, int, str | None, str | None, str | None, bool, Callable[[str, int], int] | None], Generator[IO, None, None]]:
    """
    Create a reusable function for opening files of a particular type at a particular location
    Can also set new defaults for the `open` function used internally.

    See `open` for other arguments

    :param anchor: the location to open at, as a package str.
    :param data_extension: The file extension expected to open. can be `.<extension>` or just `<extension>`.
    :return: A function which creates a context manager around an opened file
    """

    # Add the dot to the extension. We expect people to not add one, but its easier to add then remove
    if not data_extension.startswith('.'):
        data_extension = '.'+data_extension
    root = pkg.files(anchor)

    @contextmanager
    def _open_file(
        name: str,
        sub_directories: tuple[str, ...] = (),
        mode: str = _mode,
        buffering: int = _buffering,
        encoding: str | None = _encoding,
        errors: str | None = _errors,
        newline: str | None = _newline,
        closefd: bool = _closefd,
        opener: Callable[[str, int], int] | None = _opener
        ):
            """
            Open a file with a predetermined type and location with given name.
            Also has the arguments for `open` available. Custom defaults can be provided
            at the same time as the type and location

            See `open` for other arguments

            :param name: The name of the file to open (without .type) at the end.
            :param sub_directory: Any sub directories from the root WITHOUT seperators ('<subdir1>', '<subdir2>')
            """
            file_name = f'{name}{data_extension}'
            path = root.joinpath(*sub_directories).joinpath(file_name)
            try:
                fp = path.open(mode, buffering, encoding, errors, newline, closefd, opener)
                yield fp
            finally:
                fp.close()

