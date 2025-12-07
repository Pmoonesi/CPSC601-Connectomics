import os
import sys
import contextlib

@contextlib.contextmanager
def suppress_c_stdout():
    with open(os.devnull, "w") as fnull:

        original_stdout_fd = os.dup(sys.stdout.fileno())

        try:
            # Redirect the stdout file descriptor to the null device
            sys.stdout.flush()
            os.dup2(fnull.fileno(), sys.stdout.fileno())
            yield
        finally:
            # Restore the original stdout file descriptor
            sys.stdout.flush()
            os.dup2(original_stdout_fd, sys.stdout.fileno())
            os.close(original_stdout_fd)


