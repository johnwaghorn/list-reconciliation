from functools import wraps
from inspect import getmembers, isclass, isfunction
from types import ModuleType
from typing import Callable, Dict, Tuple, List, Any

import textwrap

from comparison_engine.schema import LeftRecord, RightRecord, ConfigurationError

DecoratedFuncs = Tuple[str, str, Callable]
ComparisonResult = Dict[str, Dict[str, str]]
RecordPair = Tuple[LeftRecord, RightRecord]


def module_from_string(name: str, source: str) -> ModuleType:
    """Creates a module object from code as a string.

    Args:
        name (str): Name of module
        source (str): Code, as string, to add to module object

    Returns:
        ModuleType: Module
    """

    module = ModuleType(name, source)
    exec(textwrap.dedent(source), module.__dict__)
    return module


def _parametrized(func: Callable) -> Callable:
    """Decorator to allow action and comparison decorators to be implemented
    with parameters.

    Args:
        func: Decorator to pass parameters to.

    Returns:
        Decorated decorator with parameters applied.

    Raises:
        ConfigurationError: If an id is not provided to the decorator.
    """

    def outer_func(*args, **kwargs):
        if not isinstance(args[0], str):
            raise ConfigurationError("Requires an id string parameter.")

        @wraps(func)
        def inner_func(outer_func):
            return func(outer_func, *args, **kwargs)

        return inner_func

    return outer_func


@_parametrized
def comparison(func: Callable, id: str) -> Callable:
    """Decorator for identifying functions intended to compare left and right records.

    Usage:
        @comparison("CMP123")
        def date_of_birth_not_equal(left, right):
            return left["DATE_OF_BIRTH"] != right["DATE_OF_BIRTH"]

    Args:
        func (Callable): Decorated function.
        id (str): ID of the function, must be unique.

    Returns:
        Callable
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    wrapper.__wrapped__ = comparison
    wrapper.__id__ = id

    return wrapper


@_parametrized
def action(func: Callable, id: str, comparison_id: str) -> Callable:
    """Decorator for identifying functions intended to run as a result of the
    comparison left and right records. The linked comparison id is the comparison
    for which the action is run.

    Usage:
        @action("ACT123", "CMP123")
        def date_of_birth_update(left, right):
            call_api_to_update_record(left['date_of_birth'])

    Args:
        func (Callable): Decorated function.
        id (str): ID of the function, must be unique.
        comparison_id (str): Comparison function id associated with the action. (default: {None})

    Returns:
        Callable
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    wrapper.__wrapped__ = action
    wrapper.__id__ = id
    wrapper.__comparison__ = comparison

    return wrapper


def apply_comparisons(
    comparisons: DecoratedFuncs, left: LeftRecord, right: RightRecord
) -> ComparisonResult:
    """Run comparison functions on left and right records.

    Args:
        comparisons (DecoratedFuncs): (id, name, comparison_function).
        left (LeftRecord): Left hand side of record to compare.
        right (RightRecord): Right hand side of record to compare.

    Returns:
        ComparisonResult: Result of all comparisons made. The absence of an item
            indicates that the comparison function returned a truthy result and
            requires no more processing. {record_id: {comparison_id: comparison_name}}
    """

    return [id for id, name, func in comparisons if func(left, right)]


def get_records(module: ModuleType) -> RecordPair:
    """Get left and right records from a module.

    Args:
        module (ModuleType): Module to search for LeftRecord and RightRecord.

    Returns:
        RecordPair: Tuple containing LeftRecord and RightRecord.

    Raises:
        ConfigurationError: If not exactly 1 each of LeftRecord and RightRecord is defined.
    """

    left = None
    right = None
    for _, member in getmembers(module, isclass):
        if issubclass(member, LeftRecord) and member != LeftRecord:
            if left:
                raise ConfigurationError("A LeftRecord object has already been defined.")
            left = member

        elif issubclass(member, RightRecord) and member != RightRecord:
            if right:
                raise ConfigurationError("A RightRecord object has already been defined.")
            right = member

    if not all([left, right]):
        raise ConfigurationError("Exactly one LeftRecord and RightRecord object must be defined.")

    return left, right


def get_decorated_funcs(module: ModuleType, decorator: Callable) -> DecoratedFuncs:
    """Get decorated functions from a module, filtered by decorator type.

    Args:
        module (ModuleType): Module to search for decorated functions.
        decorator (Callable): Decorator function to filter.

    Returns:
        DecoratedFuncs: (id, name, comparison_function).

    Raises:
        ConfigurationError: If the id's of the decorated functions are not unique.
    """

    funcs = []

    for func in getmembers(module, isfunction):
        if getattr(func[1], "__wrapped__", None) == decorator:
            if func[1].__id__ in [f[2].__id__ for f in funcs]:
                raise ConfigurationError(
                    f"{decorator.__name__} function id's must be unique ({func[1].__id__})"
                )
            funcs.append((func[1].__id__, *func))

    return funcs


def compare_records(
    module: ModuleType, left: Dict[str, Any], right: Dict[str, Any]
) -> ComparisonResult:
    """Apply comparisons to objects defined in module to the left and right records.

    Args:
        module (ModuleType):
        left (Dict[str, Any]):
        right (Dict[str, Any]):

    Returns:
        List[str]: List of comparison id's which return True from the comparison implementation.
    """

    comparison_funcs = get_decorated_funcs(module, comparison)
    LeftRecord, RightRecord = get_records(module)
    return apply_comparisons(comparison_funcs, LeftRecord(left), RightRecord(right))
