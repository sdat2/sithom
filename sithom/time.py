"""Time Utilities Module."""
from typing import Callable
import time
from functools import wraps
import signal
from contextlib import contextmanager


class TimeoutException(Exception):
    pass


@contextmanager
def time_limit(seconds: int) -> None:
    """Time limit manager.

    Function taken from:

    https://stackoverflow.com/questions/366682/
    how-to-limit-execution-time-of-a-function-call

    Args:
        seconds (int): how  many seconds to wait until timeout.

    Example:
        Call a function which will take longer than the time limit::

            import time
            from sithom.utils import time_limit, TimeoutException

            def long_function_call():
                for t in range(5):
                    print("t=", t, "seconds")
                    time.sleep(1)
            try:
                with time_limit(3):
                    long_function_call()
                    assert False
            except TimeoutException as e:
                print("Timed out!")
            except:
                print("A different exception")

    """

    def _signal_handler(signum, frame):
        raise TimeoutException("Timed out!")

    signal.signal(signal.SIGALRM, _signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


def time_stamp() -> str:
    """
    Return the current local time.

    Returns:
        str: Time string format "%Y-%m-%d %H:%M:%S".
    """
    current_time = time.localtime()
    return time.strftime("%Y-%m-%d %H:%M:%S", current_time)


def hr_time(time_in: float) -> str:
    """
    Return human readable time as string.

    I got fed up with converting the number in my head.
    Probably runs very quickly.

    Args:
        time (float): time in seconds

    Returns:
        str: string to print.

    Example:
        120 seconds to human readable string::

            >>> from sithom.utils import hr_time
            >>> hr_time(120)
                "2 min 0 s"
    """
    if time_in < 60:
        return "%2.5f s" % time_in
    elif 60 < time_in < 60 * 60:
        return time.strftime("%M min %S s", time.gmtime(time_in))
    elif 60 * 60 < time_in < 24 * 60 * 60:
        return time.strftime("%H hr %M min %S s", time.gmtime(time_in))
    else:
        return "%2.5f s" % time_in


def timeit(method: Callable) -> Callable:
    """`sithom.timeit` is a wrapper for performance analysis.

    It should return the time taken for a function to run. Alters `log_time` `dict`
    if fed in. Add @timeit to the function you want to time. Function needs
    `**kwargs` if you want it to be able to feed in `log_time` `dict`.

    Args:
        method (Callable):  the function that it takes as an input

    Examples:
        Here is an example with the tracking functionality and without::

            >>> from sithom.utils import timeit
            >>> @timeit
            ... def loop(**kwargs):
            ...     total = 0
            ...     for i in range(int(10e2)):
            ...         for j in range(int(10e2)):
            ...             total += 1
            >>> tmp_log_d = {}
            >>> loop(log_time=tmp_log_d)
            >>> print(tmp_log_d["loop"])
            >>> loop()

    """

    @wraps(method)
    def timed(*args, **kw):
        ts = time.perf_counter()
        result = method(*args, **kw)
        te = time.perf_counter()
        # time.gmtime()
        if "log_time" in kw:
            name = kw.get("log_name", method.__name__.lower())
            kw["log_time"][name] = te - ts
            print("%r " % method.__name__, hr_time(te - ts), "\n")
        else:
            print("%r " % method.__name__, hr_time(te - ts), "\n")
        return result

    return timed
