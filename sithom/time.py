"""Time Utilities Module."""
from typing import Callable
import time
from functools import wraps
import signal
from contextlib import contextmanager


class TimeoutException(Exception):
    """The function has timed out, as the time limit has been reached."""


@contextmanager
def time_limit(seconds: int) -> None:
    """Time limit manager.

    Function taken from:

    https://stackoverflow.com/a/601168

    Args:
        seconds (int): how  many seconds to wait until timeout.

    Example:
        Call a function which will take longer than the time limit::

            >>> import time
            >>> from sithom.time import time_limit, TimeoutException
            >>> def long_function_call():
            ...     for t in range(0, 5):
            ...         print("t=", t, "seconds")
            ...         time.sleep(1.1)
            >>> try:
            ...     with time_limit(3):
            ...         long_function_call()
            ...         assert False
            ... except TimeoutException as e:
            ...     print("Timed out!")
            ... except Exception as e:
            ...     print("A different exception\t", e)
            t= 0 seconds
            t= 1 seconds
            t= 2 seconds
            Timed out!

    Seems not to work for windows:
    
    https://github.com/sdat2/sithom/runs/7343392694?check_suite_focus=true

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

            >>> from sithom.time import hr_time
            >>> hr_time(120)
                '02 min 00 s'
    """
    if time_in < 60:
        output_str = "%2.5f s" % time_in
    elif 60 < time_in < 60 * 60:
        output_str = time.strftime("%M min %S s", time.gmtime(time_in))
    elif 60 * 60 < time_in < 24 * 60 * 60:
        output_str = time.strftime("%H hr %M min %S s", time.gmtime(time_in))
    else:
        output_str = "%2.5f s" % time_in
    return output_str


def timeit(method: Callable) -> Callable:
    """`sithom.timeit` is a wrapper for performance analysis.

    It should return the time taken for a function to run. Alters `log_time` `dict`
    if fed in. Add @timeit to the function you want to time. Function needs
    `**kwargs` if you want it to be able to feed in `log_time` `dict`.

    Args:
        method (Callable):  the function that it takes as an input

    Examples:
        Here is an example with the tracking functionality and without::

            from sithom.time import timeit
            @timeit
            def loop(**kwargs):
                total = 0
                for i in range(int(10e2)):
                    for j in range(int(10e2)):
                        total += 1
            tmp_log_d = {}
            loop(log_time=tmp_log_d)
            print(tmp_log_d["loop"])
            loop()

    """

    @wraps(method)
    def timed(*args, **kw):
        time_start = time.perf_counter()
        result = method(*args, **kw)
        time_end = time.perf_counter()
        # time.gmtime()
        if "log_time" in kw:
            name = kw.get("log_name", method.__name__.lower())
            kw["log_time"][name] = time_end - time_start
            print("%r " % method.__name__, hr_time(time_end - time_start), "\n")
        else:
            print("%r " % method.__name__, hr_time(time_end - time_start), "\n")
        return result

    return timed
