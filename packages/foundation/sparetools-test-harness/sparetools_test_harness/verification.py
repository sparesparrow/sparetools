"""
Verification Methods for SpareTools Test Harness.

Provides ngapy-compatible verification methods with proper type checking
and structured logging integration.
"""

import numbers
from typing import Any, Optional, Callable, Union


class VerificationMethods:
    """Collection of verification methods compatible with ngapy API."""

    def __init__(self, logger):
        """Initialize with logger instance."""
        self.logger = logger

    def verify(self, actual: Any, expected: Any, msg: str = "",
               test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify equality (ngapy-compatible)."""
        value = (actual == expected)
        text = [f"Verify {msg + ' ' if msg else ''}:"]
        text.append(f"\t  Expected : {expected}")
        text.append(f"\t  Actual   : {actual}")

        self.logger.log_result(value, text, test_num, actual, expected)

        if not value and on_fail:
            self._handle_on_fail(on_fail)

        return value

    def verify_tol(self, actual: Union[int, float], expected: Union[int, float],
                   tolerance: Union[int, float], msg: str = "", test_num: int = 0,
                   on_fail: Optional[Callable] = None) -> bool:
        """Verify with tolerance (ngapy-compatible)."""
        if not isinstance(tolerance, numbers.Number):
            raise ValueError("tolerance must be numeric")

        if not all(isinstance(x, numbers.Number) for x in [actual, expected]):
            raise ValueError('invalid data types for verification')

        value = ((expected + tolerance) >= actual) and ((expected - tolerance) <= actual)
        text = [f"Verify {msg + ' ' if msg else ''}:"]
        text.append(f"\t  Expected : {expected} ± {tolerance}")
        text.append(f"\t  Actual   : {actual}")
        text.append(f"\t  Difference: {abs(actual - expected)}")

        self.logger.log_result(value, text, test_num, actual, expected, tolerance)

        if not value and on_fail:
            self._handle_on_fail(on_fail)

        return value

    def verify_range(self, actual: Union[int, float], min_value: Union[int, float],
                     max_value: Union[int, float], msg: str = "", test_num: int = 0,
                     on_fail: Optional[Callable] = None) -> bool:
        """Verify value in range (ngapy-compatible)."""
        if not all(isinstance(x, numbers.Number) for x in [actual, min_value, max_value]):
            raise ValueError('invalid data types for verification')

        value = (actual >= min_value) and (actual <= max_value)
        text = [f"Verify {msg + ' ' if msg else ''}:"]
        text.append(f"\t  Expected : {min_value} <= Actual <= {max_value}")
        text.append(f"\t  Actual   : {actual}")

        self.logger.log_result(value, text, test_num, actual, f"[{min_value}, {max_value}]")

        if not value and on_fail:
            self._handle_on_fail(on_fail)

        return value

    def verify_ne(self, actual: Any, expected: Any, msg: str = "",
                  test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify values are not equal."""
        value = (actual != expected)
        text = [f"Verify {msg + ' ' if msg else ''} (not equal):"]
        text.append(f"\t  Not Expected : {expected}")
        text.append(f"\t  Actual       : {actual}")

        self.logger.log_result(value, text, test_num, actual, expected)

        if not value and on_fail:
            self._handle_on_fail(on_fail)

        return value

    def verify_lt(self, actual: Union[int, float], expected: Union[int, float],
                  msg: str = "", test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify actual < expected."""
        if not all(isinstance(x, numbers.Number) for x in [actual, expected]):
            raise ValueError('invalid data types for verification')

        value = actual < expected
        text = [f"Verify {msg + ' ' if msg else ''} (less than):"]
        text.append(f"\t  Expected : Actual < {expected}")
        text.append(f"\t  Actual   : {actual}")

        self.logger.log_result(value, text, test_num, actual, f"< {expected}")

        if not value and on_fail:
            self._handle_on_fail(on_fail)

        return value

    def verify_gt(self, actual: Union[int, float], expected: Union[int, float],
                  msg: str = "", test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify actual > expected."""
        if not all(isinstance(x, numbers.Number) for x in [actual, expected]):
            raise ValueError('invalid data types for verification')

        value = actual > expected
        text = [f"Verify {msg + ' ' if msg else ''} (greater than):"]
        text.append(f"\t  Expected : Actual > {expected}")
        text.append(f"\t  Actual   : {actual}")

        self.logger.log_result(value, text, test_num, actual, f"> {expected}")

        if not value and on_fail:
            self._handle_on_fail(on_fail)

        return value

    def verify_le(self, actual: Union[int, float], expected: Union[int, float],
                  msg: str = "", test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify actual <= expected."""
        if not all(isinstance(x, numbers.Number) for x in [actual, expected]):
            raise ValueError('invalid data types for verification')

        value = actual <= expected
        text = [f"Verify {msg + ' ' if msg else ''} (less or equal):"]
        text.append(f"\t  Expected : Actual <= {expected}")
        text.append(f"\t  Actual   : {actual}")

        self.logger.log_result(value, text, test_num, actual, f"<= {expected}")

        if not value and on_fail:
            self._handle_on_fail(on_fail)

        return value

    def verify_ge(self, actual: Union[int, float], expected: Union[int, float],
                  msg: str = "", test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify actual >= expected."""
        if not all(isinstance(x, numbers.Number) for x in [actual, expected]):
            raise ValueError('invalid data types for verification')

        value = actual >= expected
        text = [f"Verify {msg + ' ' if msg else ''} (greater or equal):"]
        text.append(f"\t  Expected : Actual >= {expected}")
        text.append(f"\t  Actual   : {actual}")

        self.logger.log_result(value, text, test_num, actual, f">= {expected}")

        if not value and on_fail:
            self._handle_on_fail(on_fail)

        return value

    def verify_string(self, actual: str, expected: str, msg: str = "",
                      test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify string equality (case-sensitive)."""
        if not all(isinstance(x, str) for x in [actual, expected]):
            raise ValueError('invalid data types for string verification')

        value = actual == expected
        text = [f"Verify {msg + ' ' if msg else ''} (string):"]
        text.append(f"\t  Expected : '{expected}'")
        text.append(f"\t  Actual   : '{actual}'")

        self.logger.log_result(value, text, test_num, actual, expected)

        if not value and on_fail:
            self._handle_on_fail(on_fail)

        return value

    def verify_percent(self, actual: Union[int, float], expected: Union[int, float],
                       tolerance_percent: Union[int, float], msg: str = "",
                       test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify values are within percentage tolerance."""
        if not all(isinstance(x, numbers.Number) for x in [actual, expected, tolerance_percent]):
            raise ValueError('invalid data types for percentage verification')

        if expected == 0:
            raise ValueError('expected value cannot be zero for percentage verification')

        percent_diff = abs((actual - expected) / expected) * 100
        value = percent_diff <= tolerance_percent

        text = [f"Verify {msg + ' ' if msg else ''} (percentage):"]
        text.append(f"\t  Expected : {expected} ± {tolerance_percent}%")
        text.append(f"\t  Actual   : {actual}")
        text.append(f"\t  Difference: {percent_diff:.2f}%")

        self.logger.log_result(value, text, test_num, actual, expected, tolerance_percent)

        if not value and on_fail:
            self._handle_on_fail(on_fail)

        return value

    def _handle_on_fail(self, on_fail: Callable) -> None:
        """Handle on_fail callback."""
        try:
            if hasattr(on_fail, '__iter__'):
                for obj in on_fail:
                    obj.run()
            else:
                on_fail()
        except Exception as e:
            print(f"Warning: on_fail callback failed: {e}")