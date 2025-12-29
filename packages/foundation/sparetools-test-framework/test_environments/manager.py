#              AUTHORIZED IN WRITING. THIS UNPUBLISHED WORK IS PROTECTED BY
#              THE LAWS OF THE UNITED STATES AND OTHER COUNTRIES. IN THE
#              EVENT OF PUBLICATION, THE FOLLOWING NOTICE SHALL APPLY:
#              COPR. 2020-2021 HONEYWELL INTERNATIONAL, INC. ALL RIGHTS RESERVED.
#
"""
//********************************************************************************************
//
//
// File Name: bench_manager.py
//
// Program:   TITAN
//
// Purpose:   Maintenance model container
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import abc
import datetime
import time
import atexit


from sparetools.test_environments.bench_factory import TestBenchContainer
from ngapy.simulations.clock import ClockSimulation


class TestEnvironmentState:
    def __init__(self):
        self.bench_running = False


class BaseAppManager:
    @abc.abstractmethod
    def start_app(self):
        """
                Starts Application in default PSSL Context on ASE. Needs running bench.
        """
        raise NotImplementedError("Method not implemented.")

    @abc.abstractmethod
    def load_model(self):
        """
                Loads DB model of an App into Manager.
        """
        raise NotImplementedError("Method not implemented.")


class TestEnvironmentManager:
    def __init__(self, selected_modules):
        self.modules = selected_modules
        self.bench_object = TestBenchContainer().get_instance()
        self.bench_object.stop()
        self.bench_state = BenchState()
        self.restart_needed = True
        self.clock_sim = ClockSimulation()
        self.clock_sim.start(datetime.datetime.now(), force=True)
        self.init_time_delay = 10
        self.callable_function_list = None
        atexit.register(self.stop_bench)
        for module in self.modules:
            self.modules[module].set_bench_manager(self)
        self.set_up()

    def set_up(self, bench_running=True, restart=False, restore=False, callable_function_list=None):
        self.callable_function_list = callable_function_list
        if restore:
            self.bench_object.restore()
        if restart:
            self.stop_bench()
            self.start_bench()
        else:
            if bench_running:
                self.start_bench()
            else:
                self.stop_bench()

    def get_modules(self):
        return self.modules

    def stop_bench(self):
        if self.bench_state.bench_running:
            self.bench_object.stop()
            self.bench_state.bench_running = False

    def start_bench(self):
        if not self.bench_state.bench_running:
            self.bench_object.start()
            self.bench_state.bench_running = True
            self.restart_needed = False
            if self.callable_function_list:
                for function in self.callable_function_list:
                    function()
            time.sleep(self.init_time_delay)
            for module in self.modules:
                self.modules[module].start_app()
                self.modules[module].load_model()

    def __del__(self):
        self.bench_object.stop()
