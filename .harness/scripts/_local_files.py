"""Read and lock regular files at harness-managed paths."""

from collections.abc import Generator
from contextlib import contextmanager
import fcntl
import os
from pathlib import Path
from stat import S_ISREG


@contextmanager
def regular_file(path: Path, flags: int = os.O_RDONLY) -> Generator[int, None, None]:
    descriptor = os.open(path, flags | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
    try:
        if not S_ISREG(os.fstat(descriptor).st_mode):
            raise ValueError(f"Expected a regular file at {str(path)!r}")
        yield descriptor
    finally:
        os.close(descriptor)


def read_text(path: Path) -> str:
    with regular_file(path) as descriptor:
        with os.fdopen(descriptor, encoding="utf-8", closefd=False) as source:
            try:
                return source.read()
            except UnicodeError:
                raise ValueError(f"Expected UTF-8 text at {str(path)!r}") from None


@contextmanager
def exclusive_lock(path: Path) -> Generator[None, None, None]:
    with regular_file(path, os.O_WRONLY | os.O_CREAT) as descriptor:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
