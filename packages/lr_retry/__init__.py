from typing import Any, Callable

from retrying import retry


def retry_func(func: Callable, **kwargs) -> Any:
    """Retries a function using retrying.retry https://pypi.org/project/retrying/.
    Args:
        func (callable): lambda-wrapped function to run.
        **kwargs: Kwargs to pass to the retrying decorator.
    Returns:
        Any: Any expected return value of the function passed.
    Usage:
        result_of_len = retry_func(
            lambda: len('123456'),
            wait_exponential_multiplier=1000,
            wait_exponential_max=10000,
            stop_max_attempt_number=10)
    """

    @retry(**kwargs)
    def wrapper():
        return func()

    return wrapper()
