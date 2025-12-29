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
import sys
import os
import argparse
import shutil
from pathlib import Path
from xml.dom import minidom

from sparetools_aerospace.products.ngaims.setup_environment import get_oms_repository_config
from ngapy.util.custom_logging import setup_logging_from_config
from ngapy.util.execute_command import execute_command

JAVA_COMMAND = "java -Dcom.ibm.team.repository.transport.client.protocol=\"TLSv1.2\""
BASE_URL = "https://aeroclm.honeywell.com/qm/service/com.ibm.rqm.integration.service.IIntegrationService/resources/Maintenance%20Solutions%20%28QM%29"
CMCF_CONTEXT_CONFIG_URI = "https://aeroclm.honeywell.com/gc/configuration/661"
TCRF_CONTEXT_CONFIG_URI = "https://aeroclm.honeywell.com/gc/configuration/666"

LOG_BAMBOO_DIR = os.environ.get("DOCKER_LOGS_PATH")
RESULTS_BAMBOO_DIR = os.environ.get("TEST_RESULTS_PATH")

RQM_UTIL_PATH = None

TEXT_VALS_TO_CHANGE = ["ns16:machine", "ns4:title", "ns6:state", "ns4:creator", "ns6:owner", "ns16:starttime",
                       "ns16:endtime", "ns16:totalRunTime", "ns16:actualRunTime", "ns16:tester"]
ELEMENTS_WITH_ATTRIBS_TO_CHANGE = ['ns4:creator', 'ns6:owner', "ns16:tester", "ns2:testcase", "ns2:executionworkitem",
                                   "ns2:buildrecord"]
STATUS_CODES = {'error': 'com.ibm.rqm.execution.common.state.error',
                'passed': 'com.ibm.rqm.execution.common.state.passed',
                'failed': 'com.ibm.rqm.execution.common.state.failed'
                }
DEBUG = False
BAMBOO_TENV_STRING = os.environ["BAMBOO_TENV_ID"] if os.environ.get('BAMBOO_TENV_ID') else 'ASE_Bamboo_TENV'
BAMBOO_BUILD_NAME = os.environ["TGT_BUILD_NAME"] if os.environ.get('TGT_BUILD_NAME') else 'Test_Build_4'
TCR_BASE_PATH = Path(os.path.dirname(os.path.realpath(__file__))) / "TCR_BASE.xml"
BR_BASE_PATH = Path(os.path.dirname(os.path.realpath(__file__))) / "BR_BASE.xml"
TCER_BASE_PATH = Path(os.path.dirname(os.path.realpath(__file__))) / "TCER_BASE.xml"
BAMBOO_BUILD_TIMESTAMP = os.environ["bamboo_buildTimeStamp"] if os.environ.get("bamboo_buildTimeStamp") \
    else '2021-11-09T20:40:25.082Z'
BAMBOO_WD = os.environ.get('bamboo_build_working_directory')
BAMBOO_TS = os.environ.get('bamboo_buildTimeStamp')

SKIP_TESTS = ['example_test', 'non_system_tests']


def execute_http_command(command):
    ret = execute_command(command)
    code_str = "Stub Code: default False"
    for line in ret[1]:
        if 'Server Response code' in line:
            code_str = ret[1][8]

    if '200' in code_str or '201' in code_str:
        return True
    else:
        log.info(f'Bad response code: {code_str}')
        return False


class Args:
    def __init__(self):
        args = sys.argv[1].split(' ')
        self.eid = args[0]
        self.pswd = args[1]
        self.utilpath = args[2]

class Commands:
    def __init__(self, args):
        self.java_path = ''
        self.cmcf_url_get = f"-command GET -user {args.eid} -password {args.pswd}  " \
                            f"-configURI {CMCF_CONTEXT_CONFIG_URI} -url {BASE_URL}"
        self.cmcf_url_post = f"-command POST -user {args.eid} -password {args.pswd}  " \
                             f"-configURI {CMCF_CONTEXT_CONFIG_URI} -url {BASE_URL}"
        self.cmcf_url_put = f"-command PUT -user {args.eid} -password {args.pswd}  " \
                            f"-configURI {CMCF_CONTEXT_CONFIG_URI} -url {BASE_URL}"
        self.url_post_wo_uri = f"-command POST -user {args.eid} -password {args.pswd} -url {BASE_URL}"
        self.tcrf_url_get = f"-command GET -user {args.eid} -password {args.pswd}  " \
                            f"-configURI {TCRF_CONTEXT_CONFIG_URI} -url {BASE_URL}"
        self.tcrf_url_post = f"-command POST -user {args.eid} -password {args.pswd}  " \
                             f"-configURI {TCRF_CONTEXT_CONFIG_URI} -url {BASE_URL}"
        self.tcrf_url_put = f"-command PUT -user {args.eid} -password {args.pswd}  " \
                            f"-configURI {TCRF_CONTEXT_CONFIG_URI} -url {BASE_URL}"
        self.all_tcr = '/executionresult'
        self.all_tcer = '/executionworkitem'
        self.all_tc = '/testcase'
        self.all_attach = '/attachment'
        self.attach_spec = '/urn:com.ibm.rqm:attachment:'
        # ID needs to be inserted to the end
        self.tcr_spec = "/urn:com.ibm.rqm:executionresult:"
        self.tcer_spec = "/urn:com.ibm.rqm:executionworkitem:"


class TestCase:
    def __init__(self):
        self.eid = None
        self.tc_ref = None
        self.tcer_ref = None
        self.timestamp = None
        self.name = None
        self.errors = None
        self.failures = None
        self.n_tests = None
        self.time = None
        self.machine = None
        self.title = None
        self.state = None
        self.actualRunTime = None
        self.totalRunTime = None
        self.creator = None
        self.tester = None
        self.owner = None
        self.executionworkitem = None
        self.testcase = None
        self.starttime = None
        self.endtime = None
        self.contrib = None
        self.buildrecord = None
        self.id = None
        self.failed = None
        self.area = ''

    def compute_needed_params(self):
        if self.failed:
            self.state = STATUS_CODES["failed"]
        else:
            self.state = STATUS_CODES["passed"]
        self.actualRunTime = self.time
        self.totalRunTime = self.time
        self.starttime = self.compute_correct_format_time(self.timestamp.replace('_',''))
        self.endtime = self.compute_end_time(self.timestamp.replace('_',''))
        self.tester = self.eid
        self.creator = self.eid
        self.owner = self.eid
        self.executionworkitem = self.tcer_ref
        self.testcase = self.tc_ref
        self.contrib = f'https://aeroclm.honeywell.com/jts/resource/itemName/com.ibm.team.repository.Contributor/{self.eid}'
        self.title = self.area + '_' + self.id + f'_{BAMBOO_TENV_STRING}_' + self.timestamp

    def compute_correct_format_time(self, timestamp):
        # format like this 2021-06-18T10:06:46.535Z
        str_timestamp = timestamp[4:8]+'-'+timestamp[0:2]+'-'+timestamp[2:4] + 'T' + timestamp[8:10] + ':' + \
                        timestamp[10:12] + ':' + timestamp[12:14] + '.000Z'
        return str_timestamp

    def compute_end_time(self, timestamp):
        str_timestamp = str(int(timestamp) + int(float(self.time)))
        if len(timestamp) != len(str_timestamp):
            str_timestamp = '0' + str_timestamp
        return self.compute_correct_format_time(str_timestamp)


class XMLParser:
    def __init__(self, args):
        self.bamboo_xml_files = []
        self.test_cases = []
        self.existing_tcers = []
        self.eid = args.eid
        self.commands = None
        self.buildrecord = None
        pass

    def parse_results(self, results):
        tc_list = list(results.getElementsByTagName("testcase"))
        res = []
        for tc in tc_list:
            tc_info = {}
            parts = (tc.attributes['name'].value).split(' ')
            first = False
            for pt in parts:
                if any(i.isdigit() for i in pt) and first:
                    ti = ''
                    start = False
                    for ch in pt:
                        if ch.isdigit:
                            ti += ch
                            start = True
                        elif start:
                            break
                    tc_info['id'] = ti
                    break
                elif any(i.isdigit() for i in pt):
                    first = True
            if not 'id' in tc_info.keys():
                a = 0
            aux = tc.getElementsByTagName("failure")
            if aux:
                tc_info['failed'] = True
            else:
                tc_info['failed'] = False
            res.append(tc_info)

        return res

    def get_timestamp_area(self, parts):
        tc = parts[0]
        timestamp = ''
        for part in parts[1:]:
            if not part.isnumeric():
                tc += '_' + part
            else:
                timestamp += '_' + part
        return timestamp[1:], tc

    def get_test_cases(self):
        self.bamboo_xml_files = [str(file.stem) for file in Path(RESULTS_BAMBOO_DIR).iterdir()
                                 if '.xml' in str(file) and file.is_file()]
        for xml_file in self.bamboo_xml_files:
            results = minidom.parse(os.path.join(RESULTS_BAMBOO_DIR, xml_file + '.xml'))
            ts = results.getElementsByTagName("testsuite")[0]
            machine = ts.attributes['hostname'].value
            results = self.parse_results(results)
            timestamp, area = self.get_timestamp_area(xml_file.split('_'))
            if area in SKIP_TESTS:
                continue
            for result in results:
                test_case = TestCase()
                test_case.area = area
                test_case.timestamp = timestamp
                test_case.time = test_case.timestamp
                test_case.eid = self.eid
                test_case.machine = machine
                test_case.id = result['id']
                test_case.failed = result['failed']
                self.test_cases.append(test_case)

    def process_log_file(self, name, timestamp):
        log_file_path = Path(LOG_BAMBOO_DIR) / (name + '.log')
        if log_file_path.exists():
            new_name = Path(LOG_BAMBOO_DIR) / (name + '_' + timestamp + '.log')
            try:
                shutil.copyfile(log_file_path, new_name)
            except:
                log.info("Unable to copy log file. Probably already exists")
            return new_name
        else:
            return None

    def hash_id(self, timestamp):
        timestamp = timestamp.replace('_','')
        id_dig_1 = str((5 + int(timestamp[7])))
        id_dig_23 = str(int(timestamp[0:2]) + int(timestamp[2:4]))
        id_dig_4567 = str(int(timestamp[-4:]))
        id_dig_8 = '0'
        id = id_dig_1 + id_dig_23 + id_dig_4567 + id_dig_8
        command = f'{JAVA_COMMAND} -jar {RQM_UTIL_PATH} {commands.cmcf_url_get}{commands.all_attach}/{id}' \
                  f' -filepath ' \
                  f'attach_exists.xml'
        ret = execute_http_command(command) if not DEBUG else False
        if ret:
            id = list(id)
            id[-1] = str(3)
            id = ''.join(id)

        return id

    def post_attachment(self, file_path, id_at):
        command = f'{JAVA_COMMAND} -jar {RQM_UTIL_PATH} {commands.cmcf_url_put}{commands.all_attach}/{id_at}' \
                  f' -filepath ' \
                  f'{file_path}'
        ret = execute_http_command(command)
        return ret

    def upload_attachments(self):
        done_areas = {}
        for tc in self.test_cases:
            if tc.area not in done_areas.keys():
                ret = False
                base_file = tc.area + '_' + tc.timestamp + '.xml'
                id_at = int(self.hash_id(tc.timestamp))

                xml_file_path = os.path.join(RESULTS_BAMBOO_DIR, base_file)
                ret = self.post_attachment(xml_file_path, id_at)
                tc.xml_attachment = f"{BASE_URL}{commands.all_attach}/{id_at}"

                txt_file_path = xml_file_path.replace('.xml', '.txt')
                ret = ret and self.post_attachment(txt_file_path, str(int(id_at + 1)))
                tc.txt_attachment = f"{BASE_URL}{commands.all_attach}/{str(int(id_at + 1))}"

                log_file_path = self.process_log_file(tc.area, tc.timestamp)
                ret = ret and self.post_attachment(log_file_path, str(int(id_at + 2)))
                tc.log_attachment = f"{BASE_URL}{commands.all_attach}/{str(int(id_at + 2))}"

                done_areas[tc.area] = {'xml': tc.xml_attachment, 'txt': tc.txt_attachment, 'log': tc.log_attachment}
                if not ret:
                    log.info(f'Unable to upload attachemnt')
            else:
                tc.txt_attachment = done_areas[tc.area]['txt']
                tc.xml_attachment = done_areas[tc.area]['xml']
                tc.log_attachment = done_areas[tc.area]['log']

        return

    def get_area_id_rqm(self, title):
        parts = title.split('_')
        area = ''
        id = None
        for part in parts:
            if part.isnumeric():
                id = part
                break
            else:
                area += '_' + part
        return area[1:], id

    def parse_tcs(self, tcs, tcrf):
        entries = list(tcs.getElementsByTagName("entry"))
        for entry in entries:
            title = entry.getElementsByTagName("title")[0]
            area, id = self.get_area_id_rqm(title.firstChild.nodeValue)
            if tcrf:
                area = "tcrf_" + area
            if id is None:
                continue
            href = entry.getElementsByTagName("id")[0]
            tc_obj = [tc for tc in self.test_cases if tc.area == area and tc.id == id]
            if not tc_obj:
                continue
            else:
                tc_obj = tc_obj[0]
            tc_obj.testcase = href.firstChild.nodeValue
        return

    def get_all_tcs(self):
        for get_command in (commands.tcrf_url_get,):
            command = f'{JAVA_COMMAND} -jar {RQM_UTIL_PATH} {get_command}{commands.all_tc} ' \
                         f'-filepath all_tc.xml'
            ret = execute_http_command(command)
            rqm_tcs = minidom.parse('all_tc.xml')
            self.parse_tcs(rqm_tcs, True if get_command == commands.tcrf_url_get else False)
            next_set = True
            while next_set:
                next_set = False
                links = list(rqm_tcs.getElementsByTagName("link"))
                for link in links:
                    if link.getAttribute("rel") == "next":
                        next_set = True
                        next_url = link.getAttribute("href")
                        break
                if not next_set:
                    break
                next_page_command = ' '.join(get_command.split(' ')[:-1]) + ' ' + next_url
                tc_command = f'{JAVA_COMMAND} -jar {RQM_UTIL_PATH} {next_page_command} ' \
                             f'-filepath all_tc.xml'
                ret = execute_http_command(tc_command)
                rqm_tcs = minidom.parse('all_tc.xml')
                self.parse_tcs(rqm_tcs, True if get_command == commands.tcrf_url_get else False)

    def create_tcers(self):
        self.get_all_tcs()
        tcer_base = minidom.parse(str(TCER_BASE_PATH))
        for tc in self.test_cases:
            if not tc.testcase or 'tcrf' not in tc.area:
                continue
            print(tc.testcase)
            title = tc.area[5:] + '_' + tc.id + '_tcrf_' + BAMBOO_TENV_STRING
            elem = tcer_base.getElementsByTagName('ns4:title')[0].childNodes[0]
            elem.replaceWholeText(title)
            tcer_base.getElementsByTagName('ns2:testcase')[0].attributes.__setitem__('href', tc.testcase)
            with open("UPDATED_TCER.xml", "w") as xml_file:
                tcer_base.writexml(xml_file)
            command = f'{JAVA_COMMAND} -jar {RQM_UTIL_PATH} {commands.tcrf_url_post}{commands.all_tcer} ' \
                      f'-filepath UPDATED_TCER.xml'
            ret = execute_http_command(command)

    def map_correct_tcers(self):
        bamboo_tc = [tc.area + '_' + tc.id for tc in self.test_cases]
        new_tc_list = []
        # one time call to create TCERS
        #self.create_tcers()

        for name, i in zip(bamboo_tc, range(0, len(bamboo_tc))):
            if 'tcrf' in name:
                title = name[5:] + '_tcrf_' + BAMBOO_TENV_STRING
                get_command = commands.tcrf_url_get
            else:
                title = name + '_' + BAMBOO_TENV_STRING
                get_command = commands.cmcf_url_get

            command = f'{JAVA_COMMAND} -jar {RQM_UTIL_PATH} {get_command}{commands.all_tcer}' \
                      f'?fields=feed/entry/content/executionworkitem[title=\'{title}\']/description ' \
                      f'-filepath spec_tcer.xml'
            ret = execute_http_command(command)
            if not ret:
                continue
            tcer_desc = minidom.parse('spec_tcer.xml')
            try:
                ref = (tcer_desc.getElementsByTagName("id")[1].childNodes[0].data)
            except:
                continue
            self.test_cases[i].tcer_ref = ref
            id = ref.split('/')[-1]
            # download full tcer
            command = f'{JAVA_COMMAND} -jar {RQM_UTIL_PATH} {get_command}{commands.all_tcer}/{id} ' \
                      f'-filepath spec_tcer.xml'
            ret = execute_http_command(command)
            if not ret:
                continue
            tcer = minidom.parse('spec_tcer.xml')
            self.fill_tcer_to_tc(self.test_cases[i], tcer)
            new_tc_list.append(self.test_cases[i])
        self.test_cases = new_tc_list

    def fill_tcer_to_tc(self, tc, tcer):
        try:
            tcr = tcer.getElementsByTagName("ns2:testcase")[0]
            tc.tc_ref = tcr.getAttribute("href")
        except:
            log.info(f'Something not expected is in xml from RQM')
        tc.compute_needed_params()

    def send_tcr_to_rqm(self):
        for tc in self.test_cases:
            post_command = commands.tcrf_url_post if 'tcrf' in tc.area else commands.cmcf_url_post
            tc.buildrecord = self.buildrecord
            tcr_base = minidom.parse(str(TCR_BASE_PATH))
            self.fill_parameters(tc, tcr_base)
            with open("UPDATED_TCR.xml", "w") as xml_file:
                tcr_base.writexml(xml_file)
            command = f'{JAVA_COMMAND} -jar {RQM_UTIL_PATH} {post_command}{commands.all_tcr}' \
                  f' -filepath UPDATED_TCR.xml'
            ret = execute_http_command(command)

    def fill_parameters(self, tc, tcr_base):
        for attrib in TEXT_VALS_TO_CHANGE:
            tc_attrib = attrib.split(':')[1]
            elem = tcr_base.getElementsByTagName(attrib)[0].childNodes[0]
            elem.replaceWholeText(getattr(tc, tc_attrib))
        for attrib in ELEMENTS_WITH_ATTRIBS_TO_CHANGE:
            if attrib not in ["ns2:testcase", "ns2:executionworkitem", "ns2:buildrecord"]:
                tc_attrib = tc.contrib
                tcr_attrib = "ns1:resource"
            else:
                tcr_attrib = "href"
                tc_attrib = getattr(tc, attrib.split(':')[1])
            tcr_base.getElementsByTagName(attrib)[0].attributes.__setitem__(tcr_attrib, tc_attrib)
        attachments = tcr_base.getElementsByTagName('a')
        attachments[0].attributes.__setitem__("href", tc.xml_attachment)
        attachments[1].attributes.__setitem__("href", tc.txt_attachment)
        attachments[2].attributes.__setitem__("href", tc.log_attachment)
        pass

    def process_build(self):
        br_base = minidom.parse(str(BR_BASE_PATH))
        elem = br_base.getElementsByTagName("ns4:title")[0].childNodes[0]
        elem.replaceWholeText(BAMBOO_BUILD_NAME)
        elem = br_base.getElementsByTagName("ns2:starttime")[0].childNodes[0]
        elem.replaceWholeText(BAMBOO_BUILD_TIMESTAMP)
        elem = br_base.getElementsByTagName("ns2:endtime")[0].childNodes[0]
        elem.replaceWholeText(BAMBOO_BUILD_TIMESTAMP)

        self.buildrecord = ''

        with open("UPDATED_BR.xml", "w") as xml_file:
            br_base.writexml(xml_file)

        command = f'{JAVA_COMMAND} -jar {RQM_UTIL_PATH} {commands.cmcf_url_post}/buildrecord' \
                  f' -filepath UPDATED_BR.xml'
        ret = execute_http_command(command)
        if ret:
            self.buildrecord = self.get_build_id()


    def get_build_id(self, tcrf=False):
        get_command = commands.tcrf_url_get if tcrf else commands.cmcf_url_get
        command = f'{JAVA_COMMAND} -jar {RQM_UTIL_PATH} {get_command}/buildrecord?fields=feed/entry/content/buildrecord[title=\'{BAMBOO_BUILD_NAME}\']' \
                  f' -filepath BuildRecord.xml'
        ret = execute_http_command(command)
        if ret:
            tcr_base = minidom.parse("BuildRecord.xml")
            buildrecord = tcr_base.getElementsByTagName("id")[1].childNodes[0].data
            return buildrecord


if __name__ == '__main__':
    log = setup_logging_from_config(get_oms_repository_config())
    args = Args()
    RQM_UTIL_PATH = args.utilpath
    commands = Commands(args)
    xml_par = XMLParser(args)
    xml_par.process_build()
    xml_par.get_test_cases()
    xml_par.upload_attachments()
    xml_par.map_correct_tcers()
    xml_par.send_tcr_to_rqm()

