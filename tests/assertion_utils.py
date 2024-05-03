import os
import re
from datetime import datetime
from enum import Enum

import dateutil

ignore = object()


def safe_get_attr(obj, key):
    if isinstance(key, str):
        attr = getattr(obj, key, None)
        if attr is not None:
            return attr
    try:
        return obj.get(key, None)
    except Exception:  # noqa: BLE001
        return None


def _collect_callable_result_differences(actual, expected, path, differences):
    if isinstance(expected, tuple) and len(expected) == 2 and callable(expected[0]):
        return _collect_differences(expected[0](actual), expected[1], path=path, differences=differences)
    return None


def _collect_precicate_differences(actual, expected, path, differences):
    if callable(expected) and not callable(actual):
        if not expected(actual):
            differences.append(
                {"path": f"{path}", "actual": actual, "expected": "predicate evaluates to trutthy value"}
            )
        return differences
    return None


def _collect_dict_differences(actual, expected, path, differences):
    if isinstance(expected, dict):
        for key, expected_value in expected.items():
            actual_value = safe_get_attr(actual, key)
            _collect_differences(actual_value, expected_value, path=f"{path}.{key}", differences=differences)
        return differences
    return None


def _collect_collection_differences(actual, expected, path, differences):
    if isinstance(expected, list | tuple):
        for index, expected_item in enumerate(expected):
            try:
                _collect_differences(actual[index], expected_item, path=f"{path}[{index}]", differences=differences)
            except IndexError:
                differences.append(
                    {"path": f"{path}[{index}]", "actual": f"index {index} not found", "expected": expected_item}
                )
        return differences
    return None


def _collect_regex_differences(actual, expected, path, differences):
    if isinstance(expected, re.Pattern):
        if not expected.match(str(actual)):
            differences.append({"path": path, "actual": actual, "expected": expected})
        return differences
    return None


def _collect_datetime_differences(actual, expected, path, differences):
    if isinstance(actual, datetime) and isinstance(expected, str):
        # parse date to ISO8601 format and do compare
        return _collect_differences(actual, dateutil.parser.parse(expected), path=f"{path}", differences=differences)
    return None


def _collect_enum_differences(actual, expected, path, differences):
    if isinstance(actual, Enum) and (isinstance(expected, str | int)):
        return _collect_differences(actual.value, expected, path=f"{path}", differences=differences)
    return None


def _collect_differences(actual, expected, path, differences):
    if expected == ignore:
        return differences

    for collector in [
        _collect_callable_result_differences,
        _collect_precicate_differences,
        _collect_dict_differences,
        _collect_collection_differences,
        _collect_regex_differences,
        _collect_datetime_differences,
        _collect_enum_differences,
    ]:
        if collector(actual, expected, path, differences) is not None:
            return differences

    if expected != actual:
        differences.append({"path": path, "actual": actual, "expected": expected})
    return differences


def assert_similar(actual, expected):
    """Assert loose equality of an actual (nested) object, list, tuple or dict and an expected structure.

    All paths to a values inside actual that are not present in expected, are ignored.
    Types with special meaning within expected:
        - callable: the callable will be applied to the value at the same path in
         actual and the result is asserted to be truthy
        - tuple(callable, expected_value): the callable will be applied to the value at the same path in
         actual and the result is asserted to be equal to expected_value
         - re.Pattern: the value at the same path in actual is asserted to match the pattern
         - ignore: the actual value at the same path is ignored
         (usefull to ignore values at certain positions in a list or tuple)
    :param actual: the actual value
    :param expected: the partialy expected value expressed as a (nested) list, tuple or dict.
    :return: None
    :raise: AssertionError if there differences were found.
    """
    differences = [
        f'expected{diff["path"]}: "{diff["expected"]}", actual{diff["path"]}: "{diff["actual"]}"'
        for diff in _collect_differences(actual, expected, path="", differences=[])
    ]
    assert not differences, f"found {len(differences)} differences:\n{os.linesep.join(differences)}"
