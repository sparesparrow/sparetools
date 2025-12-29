#
# DATA_RIGHTS:  HONEYWELL CONFIDENTIAL & PROPRIETARY
#              THIS WORK CONTAINS VALUABLE CONFIDENTIAL AND PROPRIETARY
#              INFORMATION. DISCLOSURE, USE OR REPRODUCTION OUTSIDE OF
#              HONEYWELL INTERNATIONAL, INC. IS PROHIBITED EXCEPT AS
#              AUTHORIZED IN WRITING. THIS UNPUBLISHED WORK IS PROTECTED BY
#              THE LAWS OF THE UNITED STATES AND OTHER COUNTRIES. IN THE
#              EVENT OF PUBLICATION, THE FOLLOWING NOTICE SHALL APPLY:
#              COPR. 2020-2021 HONEYWELL INTERNATIONAL, INC. ALL RIGHTS RESERVED.
#
import logging
import pprint
from operator import methodcaller

from ngapy.exceptions.ngapy_exceptions import NgapyAttributeError
from ngapy.util.miscellaneous_functions import make_list_from_variable

log = logging.getLogger('__main__.' + __name__)


def combine_and(array):
    if False in array:
        return False
    return True


def combine_or(array):
    if True in array:
        return True
    return False


def filter_by_attribute(collection: list, filter_functions, combination_function=combine_and):
    filter_functions = make_list_from_variable(filter_functions)
    result_list = []
    for value in collection:
        result_logical = list(map(methodcaller('__call__', value), filter_functions))
        if combination_function(result_logical):
            result_list.append(value)
    return result_list


def search_by_attribute(collection: list, filter_functions, combination_function=combine_and):
    result = filter_by_attribute(collection, filter_functions, combination_function)
    if len(result):
        return result[0]
    else:
        formatted_collection = pprint.pformat(collection, depth=5)
        log.warning(
            f'Filter: Not able to find value using {filter_functions} in collection: {formatted_collection[:100 * 1024]}',
            stack_info=True)
        return None


class Functor(object):
    def __init__(self, function, attribute, *arguments) -> None:
        self.arguments = arguments
        self.attribute = attribute
        self.function = function

    def __call__(self, object_to_evaluate):
        if not hasattr(object_to_evaluate, self.attribute):
            raise NgapyAttributeError(f'Object {object_to_evaluate} does not have attribute: {self.attribute}')
        return self.function(getattr(object_to_evaluate, self.attribute), self.arguments)


def equality(value, attributes):
    if attributes[0] == value:
        return True
    return False


def not_equality(value, attributes):
    if attributes[0] != value:
        return True
    return False


def string_equal_case_insensitive(value, attributes):
    if attributes[0].lower() != value.lower():
        return True
    return False


def string_equal_case_sensitive(value, attributes):
    return equality(value, attributes)


def get_string_comparison_function(case_sensitive):
    if case_sensitive:
        return string_equal_case_sensitive
    else:
        return string_equal_case_insensitive


def id_limit_function(value, attributes):
    if attributes[0] > value:
        return True
    return False


def array_with_size_greater_than(value, attributes):
    if attributes[0] < len(value):
        return True
    return False
