@echo off

rem ################################################################################
rem #
rem ### res_parser.bat ###
rem #
rem # Description:
rem #
rem # Test results parsing utilities.
rem #
rem # The module defines interface and functionality for parsing Test result files.
rem #
rem # Arguments:
rem # - res_name - Name of Test result to parse.
rem #
rem ################################################################################


:settings

setlocal

rem Arguments
rem ----------------------------------------------------------------------------

set res_name=%~1

rem Others
rem ----------------------------------------------------------------------------

set python_exe="C:\titan-python-environment\8.0\python.exe"
set res_parser_py="%ENV_OMS_REPOSITORY_ROOT%\..\ngapy-dev\ngapy\product_specific\ngaims\test_execution\res_parser.py"
set exit_code=-1


:run

call %python_exe% %res_parser_py% "%res_name%"

set exit_code=%ERRORLEVEL%


:finalize

exit %exit_code%

rem ### res_parser.bat ###
