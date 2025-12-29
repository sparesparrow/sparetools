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
################################################################################
#
### tcrf_report.py ###
#
# Description:
#
# TCRF report utilities.
#
# The module defines interface and functionality for handling decoded TCRF report.
#
################################################################################

################################################################################
## Imports

import os
import sys
import logging

################################################################################
## Public interface

## class TCRFReport
## =============================================================================
## The class defines interface and functionality for handling decoded TCRF report.
##
## Decoded TCRF report is interpreted as the following internal dictionary structure:
##
## parameters
## {
##     "<parameter_1_name>" :
##     {
##         "id"     : <parameter_id>
##         "empty"  : False | True
##         "freq"   : <parameter_freq>
##         "frame"  : <parameter_frame>
##         "values" :
##         [
##             (<time_stamp_1> , <value_1>)
##             (<time_stamp_2> , <value_2>)
##             ...
##         ]
##     }
##     "<parameter_2_name>" :
##     {
##         "id"     : <parameter_id>
##         "empty"  : False | True
##         "freq"   : <parameter_freq>
##         "frame"  : <parameter_frame>
##         "values" :
##         [
##             (<time_stamp_1> , <value_1>)
##             (<time_stamp_2> , <value_2>)
##             ...
##         ]
##     }
##     ...
## }
class TCRFReport:

## Methods
## -----------------------------------------------------------------------------

    ## Class Constructor.
    def __init__(self):
        self._parameters = {}  # Dictionary of TCRF report recorded parameters.

        return

    ## The method gets TCRF report recorded parameters.
    @property
    def parameters(self):
        return self._parameters

    ## The method gets value of TCRF parameter for the specified time stamp.
    def get_value(
        self,
        name,  # Name of TCRF parameter.
        time   # Time stamp.
    ):
        value = None

        if not(self._parameters[name]["empty"]):
            for item in self._parameters[name]["values"]:
                if ((item[0] == time) and (item[1] != None)):
                    value = item[1]
                    break

        return value

    ## The method gets values of TCRF parameters for the specified time stamp.
    def get_values(
        self,
        time,            # Time stamp.
        do_full = False  # Indicator, which indicates that all TCRF parameters (including None values) shall be collected.
    ):
        values = {}

        for key in self._parameters:
            value = self.get_value(key, time)

            if ((value == None) and not(do_full)):
                continue

            values[key] = self.get_value(key, time)

        return values

    ## The method parses decoded TCRF report file and creates internal dictionary.
    def create(
        self,
        report_file_name,  # Name of decoded TCRF report file.
        do_full            # Indicator, which indicates that full TCRF report shall be parsed.
    ):
        #is_data_header_line = False
        is_data_line = False

        with open(report_file_name, "r") as report_file:
            for line in report_file:
                if (line.startswith("Frequency,Id,Time")):
                    values = line.split(",")[3 : ]

                    for index, value in enumerate(values):
                        self._parameters[value.strip()] = {"id" : index, "empty" : True}

                    is_data_line = True

                    continue

                if (is_data_line):
                    values = line.split(",")
                    time_stamp_values = values[ : 3]
                    parameter_values = values[3 : ]

                    for index, value in enumerate(parameter_values):
                        try:
                            value = eval(value.strip())
                        except:
                            value = None

                        if ((value == None) and not(do_full)):
                            continue

                        for key in self._parameters:
                            if index == self._parameters[key]["id"]:
                                if ("freq" not in self._parameters[key]):
                                    self._parameters[key].update({"freq" : eval(time_stamp_values[0])})

                                if ("frame" not in self._parameters[key]):
                                    self._parameters[key].update({"frame" : eval(time_stamp_values[1])})

                                if ("values" not in self._parameters[key]):
                                    self._parameters[key].update({"values" : [tuple([eval(time_stamp_values[2]), value])]})
                                    self._parameters[key]["empty"] = False
                                else:
                                    self._parameters[key]["values"].append(tuple([eval(time_stamp_values[2]), value]))

                                break

        return

## end class TCRFReport

### tcrf_report.py ###
