import unittest
from enum import IntEnum


class LiteralType(IntEnum):
    float = 0
    int = 1
    uint = 2
    boolean = 3
    text = 6


eq_type_map = {
    0: 'error',
    1: 'paramIn',
    2: 'paramOut',
    3: 'literal',
    4: 'variableIn',
    5: 'variableOut',
    6: 'caid',
    7: 'optLogicIn',
    8: 'fdeActiveIn',
    9: 'fdeInactiveIn',
    10: 'bufVariableIn',
    11: 'bufVariableOut',
    1000: 'frActiveIn',
    1001: 'frInactiveIn',
    1002: 'msStsFailedIn',
    1003: 'msStsInvalidIn',
    1004: 'msStsOperationalIn',
    1005: 'msStsTestIn',
    1006: 'msInstalledIn',
    1007: 'msNotInstalledIn',
    1008: 'inhibitIn',
    1009: 'frOut',
    1010: 'cmdOut',
    1011: 'fdeOut',
    1012: 'inhibitOut',
    1013: 'optLogicOutMs',
    1014: 'optLogicOutMm',
    1015: 'optLogicOutFde',
    1016: 'optLogicOutTest',
    1017: 'triggerRisingEdge',
    2000: 'optLogicOutFrame',
    2001: 'triggerContinuousStart',
    2002: 'triggerContinuousStartStop',
    3000: 'funcAdd',
    3001: 'funcSubtract',
    3002: 'funcDivide',
    3003: 'funcMultiply',
    3004: 'funcAbs',
    3005: 'funcLogAnd',
    3006: 'funcLogOr',
    3007: 'funcLogNot',
    3008: 'funcLogXor',
    3009: 'funcIsEqual',
    3010: 'funcIsNotEqual',
    3011: 'funcIsGreater',
    3012: 'funcIsGreaterOrEqual',
    3013: 'funcIsLess',
    3014: 'funcIsLessOrEqual',
    3015: 'funcBitAnd',
    3016: 'funcBitOr',
    3017: 'funcBitNot',
    3018: 'funcBitXor',
    3019: 'funcIf',
    3020: 'funcSelect',
    3021: 'funcTimeDelayTrue',
    3022: 'funcTimeDelayFalse',
    3023: 'funcIsValid',
    4000: 'funcSum',
    4001: 'funcMinimum',
    4002: 'funcMaximum',
    4003: 'funcMean',
    4004: 'funcStdev',
    4005: 'funcChanged',
    4006: 'funcRising',
    4007: 'funcFalling',
    4008: 'funcStable',
    4009: 'funcElapsedTime',
    4010: 'funcContinue',
    4011: 'funcSumUnlimit',
    4012: 'funcMinimumUnlimit',
    4013: 'funcMaximumUnlimit',
    4014: 'funcMeanUnlimit',
    4015: 'funcStdevUnlimit',
    4016: 'funcStore',
}

eq_type_map_reversed = {name: eq_type_id for eq_type_id, name in eq_type_map.items()}


class IfInputs(IntEnum):
    condition = 0
    ifFalse = 1
    ifTrue = 2


class StableInputs(IntEnum):
    interval = 0
    tolerance = 1
    value = 2


class ElapsedTimeInputs(IntEnum):
    start = 0
    stop = 1


class EdgeInputs(IntEnum):
    from_ = 0
    to = 1
    value = 2


class DelayInputs(IntEnum):
    interval = 0
    value = 1


class StatisticalInputs(IntEnum):
    intervalSize = 0
    startCondition = 1
    stopCondition = 2
    value = 2
    samplingFrequency = 2


def get_input_name(index, node_type):
    node_type_name = eq_type_map[node_type]
    match node_type_name:
        case 'funcIf':
            return (IfInputs(index)).name
        case 'funcStable':
            return (StableInputs(index)).name
        case 'funcElapsedTime':
            return (ElapsedTimeInputs(index)).name
        case 'funcChanged':
            return (EdgeInputs(index)).name
        case _ if eq_type_map_reversed['funcTimeDelayTrue'] <= node_type <= eq_type_map_reversed['funcTimeDelayFalse']:
            return (DelayInputs(index)).name
        case _ if eq_type_map_reversed['funcRising'] <= node_type <= eq_type_map_reversed['funcFalling']:
            return f'Input {index}'
        case _ if eq_type_map_reversed['funcSum'] <= node_type <= eq_type_map_reversed['funcStdevUnlimit']:
            return (StatisticalInputs(index)).name
        case _:
            return f'Input {index}'


class TestInputConversion(unittest.TestCase):
    def test_if(self):
        self.assertEqual(get_input_name(0, eq_type_map_reversed['funcIf']), (IfInputs(0)).name)
