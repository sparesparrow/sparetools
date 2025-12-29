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
class FdeMmCommon:
    def __init__(self):
        self.mm_transition_list = []
        self.last_ate_tick = None

    def store_transition_list(self, mm_transition_list, last_ate_tick):
        self.mm_transition_list = mm_transition_list
        self.last_ate_tick = last_ate_tick
        if self.mm_transition_list:
            self.mm_transition_list.sort(key=lambda item: item.timestamp)
            return self.ate_status

    @property
    def ate_status(self):
        if self.last_transition:
            return self.ate_status_raw == 'Active'
        else:
            return False

    @property
    def ate_status_raw(self):
        if self.last_transition:
            return self.last_transition.active
        else:
            return False

    @property
    def last_transition_timestamp(self):
        if self.last_transition:
            return self.last_transition.timestamp
        else:
            return None

    @property
    def last_transition_flight_leg(self):
        if self.last_transition:
            return self.last_transition.flightLeg
        else:
            return None

    @property
    def last_transition_flight_phase(self):
        if self.last_transition:
            return self.last_transition.flightPhase
        else:
            return None

    @property
    def last_transition(self):
        if self.mm_transition_list:
            return self.mm_transition_list[-1]
        else:
            return None
