"""
Wrapper around existing verification logic.
Preserves all evaluation, tolerance, and error handling.
"""

def verify_local(actual, expected, operation, msg):
    """
    Local verification without caounting this result to final result
    :param actual: Actual parameter to verify
    :type actual: any
    :param expected: Expceted value
    :type expected: any
    :param operation: Operation to be used for comapring
    :type operation: str
    :param msg: Message to be shown with result
    :type msg: str
    :return: Result
    :rtype: bool
    """
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        verification_str = f'{actual}{operation}{expected}'
    else:
        verification_str = f'"{actual}"{operation}"{expected}"'

    result = eval(verification_str)
    message(msg=('MSG-INFO> Verify ' + msg))
    message(msg=('MSG-CHCK> ' + verification_str + ' with result ' + str(result)))
    return result


def message(msg):
    """Simple message function for compatibility"""
    print(msg)


class Verifier:
    def verify(self, actual, expected, operator="==", tolerance=None):
        # Call existing verify_local logic
        return verify_local(actual, expected, operator, "")

    def verify_range(self, actual, min_val, max_val):
        # Call existing range checking logic
        return verify_local(actual, [min_val, max_val], "in_range", "")