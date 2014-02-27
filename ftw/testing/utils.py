from contextlib import contextmanager
import sys


@contextmanager
def capture_streams(stdout=None, stderr=None):
    """A context manager for temporary capturing strdout and / or stderr
    streams.
    """
    ori_stdout = sys.stdout
    ori_stderr = sys.stderr

    if stdout is not None:
        sys.stdout = stdout
    if stderr is not None:
        sys.stderr = stderr

    try:
        yield
    finally:
        if stdout is not None:
            sys.stdout = ori_stdout
        if stderr is not None:
            sys.stderr = ori_stderr
