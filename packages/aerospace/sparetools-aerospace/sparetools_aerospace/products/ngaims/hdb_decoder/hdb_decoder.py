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
# hdb_decoder.py
#
# Description:
#
# HDB decoder utilities.
#
# The module defines interface and functionality for decoding HDB database.
#
################################################################################

################################################################################
# Imports

import logging
import os
import sqlite3

import pandas as pd
from tkinter import filedialog

log = logging.getLogger('__main__.' + __name__)


################################################################################
# Public interface

# class hdbDecoder
# =============================================================================
# The class defines interface and functionality for decoding HDB Database.
class HDBDecoder:

    # Attributes
    # -----------------------------------------------------------------------------

    # Methods
    # -----------------------------------------------------------------------------

    # Class Constructor.
    def __init__(
            self,
            gui_root
    ):
        self._gui_root = gui_root  # Root GUI window.

        self._cmcf_ldi_file_name = ""  # Name of cmcf ldi file.
        self._cmcf_hdb_file_name = ""  # Name of cmcf hdb file.
        self._decoded_hdb_file_name = ""  # Name of decoded hdb file.

        return

    # The method gets name of cmcf ldi file.
    @property
    def cmcf_ldi_file_name(self):
        return self._cmcf_ldi_file_name

    # The method gets name of cmcf hdb file.
    @property
    def cmcf_hdb_file_name(self):
        return self._cmcf_hdb_file_name

    # The method gets name of Decode XLSX file.
    @property
    def decoded_hdb_file_name(self):
        return self._decoded_hdb_file_name

    # The method determines files used by hdb decoder application.
    def _determine_files(
            self,
            cmcf_ldi_file_name,  # Name of CMCF LDI file.
            cmcf_hdb_file_name,  # Name of CMCF HDB file.

    ):
        if cmcf_ldi_file_name:
            self._cmcf_ldi_file_name = cmcf_ldi_file_name

        if cmcf_hdb_file_name:
            self._cmcf_hdb_file_name = cmcf_hdb_file_name

        return

    # The method determines files used by hdb decoder application.
    def _determine_files_gui(
            self,
            cmcf_ldi_initial_dir_name,  # Name of initial directory, where to search CMCF LDI file.
            cmcf_hdb_initial_dir_name  # Name of initial directory, where to search CMCF HDB file.
    ):
        if cmcf_ldi_initial_dir_name:
            self._cmcf_ldi_file_name = filedialog.askopenfilename(
                parent=self._gui_root,
                initialdir=cmcf_ldi_initial_dir_name,
                title="Select CMCF LDI file:",
                filetypes=[("Sqlite Database files (.db)", ".db"), ("All files", ".*")]
            )
        if cmcf_hdb_initial_dir_name:
            self._cmcf_hdb_file_name = filedialog.askopenfilename(
                parent=self._gui_root,
                initialdir=cmcf_hdb_initial_dir_name,
                title="Select CMCF HDB file:",
                filetypes=[("Sqlite Database files (.db)", ".db"), ("All files", ".*")]
            )
        return

    # The method decodes HDB Database.
    def decode(
            self,
            cmcf_ldi_file_name=None,  # Name of CMCF LDI file.
            cmcf_hdb_file_name=None,  # Name of the CMCF HDB file.
            cmcf_ldi_initial_dir_name=None,  # Name of initial directory, where to search cmcf ldi file.
            cmcf_hdb_initial_dir_name=None,  # Name of initial directory, where to search cmcf hdb file.
    ):
        try:
            self._determine_files(cmcf_ldi_file_name, cmcf_hdb_file_name)
            self._determine_files_gui(cmcf_ldi_initial_dir_name, cmcf_hdb_initial_dir_name)

            conn = sqlite3.connect(self._cmcf_ldi_file_name)
            attach_query = "ATTACH" + "'" + self._cmcf_hdb_file_name + "'" + "AS hdb;"
            conn.execute(attach_query)

            # For query purposes, the first database is known as main

            flight_leg_query = ''' select fl.absolute as "Absolute Flight Leg",
                                       fl.relative as "Relative Flight Leg",
                                       DATETIME(fl.unixtime, 'unixepoch') as "Date/Time"
                                       from hdb.FlightLeg fl 
                            '''

            mm_query = '''
                        SELECT Mmt.MmId,
                           case mmt.State when 0 then 'INACTIVE' when 1 then 'ACTIVE' end as "State",
                            DATETIME(mmt.unixtime, 'unixepoch') as "Date/Time",
                            fl.absolute as "Absolute Flight Leg",
                            fp.FlightPhase as "Flight Phase Number",
                            fpd.text as "Flight Phase Name",
                            case when mmt.mmid = 0 then '<FlightPhase/FlightLeg Marker>' when mm.id is null then '<NO MAINT MSG NAME>' else mm.name end as 'Maint Msg Name',
                            case when mmt.mmid = 0 then '<FlightPhase/FlightLeg Marker>' when mm.id is null then '<NO MAINT MSG NUMBER>' else mm.number end as 'Maint Msg Number',
                            case when mmt.mmid = 0 then '<FlightPhase/FlightLeg Marker>' when mm.id is null then '<NO MAINT MSG TYPE>' else mmtype.name end as 'Maint Msg Type'
                    from hdb.MmTransition Mmt
                    inner join hdb.FlightLeg fl ON mmt.flightLegId = fl.id
                    inner join hdb.FlightPhase fp on mmt.flightPhaseId = fp.id
                    inner join main.FlightPhaseDef fpd on fp.FlightPhase = fpd.FlightPhase
                    left join main.Mm mm on mmt.mmid = mm.id
                    left join main.mmtype mmtype on mm.MmTypeId = mmtype.id
                '''
            mm_fde_query = '''
                         select case when fct.fdeid = 0 then NULL else fct.fdeid end as "FDE ID",
                               case when fct.mmid = 0 then NULL else fct.mmid end as "Maint MSg Id",
                               case fct.state when 0 then 'INACTIVE' when 1 then 'ACTIVE' end as "State",
                                DATETIME(fct.unixtime, 'unixepoch') as "Date/Time",
                                fl.absolute as "Absolute Flight Leg",
                                fp.FlightPhase as "Flight Phase Number",
                                fpd.text as "Flight Phase Name",
                                case when fct.fdeid = 0 then 'No FDE Info' else fde.name end  "FDE Name",
                                case when fct.fdeid = 0 then 'No FDE Info' else fdesev.name end   "FDE Severity",
                                case when fct.mmid = 0 then '<FlightPhase/FlightLeg Marker>' when mm.id is null then '<NO MAINT MSG NAME>' else mm.name end as 'Maint Msg Name',
                                case when fct.mmid = 0 then '<FlightPhase/FlightLeg Marker>' when mm.id is null then '<NO MAINT MSG NUMBER>' else mm.number end as 'Maint Msg Number',
                                case when fct.mmid = 0 then '<FlightPhase/FlightLeg Marker>' when mm.id is null then '<NO MAINT MSG TYPE>' else mmtype.name end as 'Maint Msg Type'
                        from hdb.fdecorrelationtime fct
                        inner join hdb.FlightLeg fl ON fct.flightLegId = fl.id
                        inner join hdb.FlightPhase fp on fct.flightPhaseId = fp.id
                        inner join main.FlightPhaseDef fpd on fp.FlightPhase = fpd.FlightPhase
                        left join main.fde fde on fct.fdeid = fde.id
                        left join main.fdesev fdesev on fde.fdesevid = fdesev.id
                        left join main.Mm mm on fct.mmid = mm.id
                        left join main.mmtype mmtype on mm.MmTypeId = mmtype.id
                '''
            df_fl_leg = pd.read_sql_query(flight_leg_query, conn)
            df_mm = pd.read_sql_query(mm_query, conn)
            df_mm_fde = pd.read_sql_query(mm_fde_query, conn)
            # todo: how to point to the working directory??
            current_dir = os.path.dirname(self._cmcf_hdb_file_name)
            decoded_file_name = "Decoded_HDB.xlsx"
            self._decoded_hdb_file_name = os.path.join(current_dir, decoded_file_name)
            with pd.ExcelWriter(self._decoded_hdb_file_name) as writer:
                df_fl_leg.to_excel(writer, sheet_name='Flight_leg_data')
                df_mm.to_excel(writer, sheet_name='Maintenance_Message')
                df_mm_fde.to_excel(writer, sheet_name='FDE-MM_Correlation')
            conn.execute("detach database hdb")

        except Exception as ex:
            log.exception(ex)

        return

# end class hdbDecoder

################################################################################
# Public interface functions

# hdb_decoder.py
