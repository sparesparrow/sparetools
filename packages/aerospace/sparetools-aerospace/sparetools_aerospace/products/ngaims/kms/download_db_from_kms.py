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
import argparse
import logging
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

import selenium
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

from ngapy.conan.conan_functions import download_python_interpreter
from ngapy.miscellaneous.git_handler import GitHandler
from ngapy.util.custom_logging import setup_logging_from_config
from ngapy.util.execute_command import execute_command
from ngapy.util.file_operations import decompress_with_progress, remove_directory_tree
from ngapy.util.miscellaneous_functions import combine_multiple_globs
from ngapy.util.setup_environment import get_config_by_os_variable

log = logging.getLogger('__main__.' + __name__)


def download_wait(path_to_downloads):
    seconds = 0
    timeout_seconds = 120
    dl_wait = True
    while dl_wait and seconds < timeout_seconds:
        time.sleep(1)
        dl_wait = False
        for fname in os.listdir(path_to_downloads):
            if fname.endswith('.crdownload'):
                dl_wait = True
        seconds += 1
    if seconds == timeout_seconds:
        raise RuntimeError('Download SLDB timeout reached.')
    return seconds


def new_chrome_browser(headless=True, download_path=None):
    """ Helper function that creates a new Selenium browser """
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('headless')
    if download_path is not None:
        preferences = {}
        os.makedirs(download_path, exist_ok=True)
        preferences["profile.default_content_settings.popups"] = 0
        preferences["download.default_directory"] = download_path
        options.add_experimental_option("prefs", preferences)
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)


def login_to_kms(browser_driver, ldi_config):
    browser_driver.get(ldi_config.kms_login.login_link)
    username = browser_driver.find_element_by_name("user")
    username.clear()
    username.send_keys(ldi_config.kms_login.username)
    password = browser_driver.find_element_by_name("password")
    password.clear()
    password.send_keys(ldi_config.kms_login.password)
    browser_driver.find_element_by_name("honidsubmit").click()


def wait_for_element_by_id(browser_driver, element, timeout=10):
    return WebDriverWait(browser_driver, timeout).until(lambda br: br.find_element_by_id(element))


def wait_for_element_by_xpath(browser_driver, element, timeout=10):
    return WebDriverWait(browser_driver, timeout).until(lambda br: br.find_elements_by_xpath(element))


def process_sldbs(repository_root):
    os.environ['ENV_OMS_PRODUCT_REPOSITORY_ROOT'] = repository_root
    oms_product_dev_config = get_config_by_os_variable('ENV_OMS_PRODUCT_REPOSITORY_ROOT')
    for database_config in oms_product_dev_config.oms_product_repository_layout.databases:
        with tempfile.TemporaryDirectory() as download_path:
            kms_files = []
            browser_driver = download_sldbs(kms_files, database_config,
                                            download_path,
                                            oms_product_dev_config.oms_product_repository_layout)

            if database_config.db_type == 'CMCF_LDI':
                generator = LdiConfigGenerator(download_path, database_config)
            if database_config.db_type == 'TCRF_SLDB':
                generator = TcrfConfigGenerator(download_path, database_config)
            store_sldbs_to_git(database_config, oms_product_dev_config, database_config.product_name, download_path, generator)
            browser_driver.close()
            browser_driver.quit()


class ConfigGenerator:
    def __init__(self, download_path):
        self.download_path = Path(download_path)
        self.branches = {Path(x).with_suffix(''): Path(x) for x in os.listdir(download_path)}

    def get_branch(self):
        for branch_name in self.branches.keys():
            yield branch_name

    def get_file(self, branch_name):
        if self.branches[branch_name].suffix == '.db':
            path = self.download_path / self.branches[branch_name]
            yield path, self.get_target_path(path)
        if self.branches[branch_name].suffix == '.zip':
            tmp_folder = self.download_path / branch_name
            os.makedirs(tmp_folder, exist_ok=True)

            database_provided = False
            decompress_with_progress(self.download_path / self.branches[branch_name], tmp_folder)
            for path in combine_multiple_globs([self.download_path / branch_name / '*.db',
                                               self.download_path / branch_name / '*.xml'],
                                               recursive=False):
                if database_provided or Path(path).suffix == '.db':
                    database_provided = True
                else:
                    return
                yield Path(path), self.get_target_path(Path(path))
            return


class LdiConfigGenerator(ConfigGenerator):
    def __init__(self, download_path, config):
        super(LdiConfigGenerator, self).__init__(download_path)
        self.config = config

    def get_target_path(self, source_name):
        return Path(self.config.db_path) / 'cmcf_ldi.db'


class TcrfConfigGenerator(ConfigGenerator):
    def __init__(self, download_path, config):
        super(TcrfConfigGenerator, self).__init__(download_path)
        self.config = config

    def get_target_path(self, source_name):
        if source_name.suffix == '.db':
            return Path(self.config.db_path) / 'tcrf_oem.db'
        if source_name.suffix == '.xml':
            return Path(self.config.db_path) / 'tcrf_fred.xml'


def store_sldbs_to_git(ldi_config, oms_product_dev_config, product_name, download_path, generator):
    repository = GitHandler()
    repository_root = oms_product_dev_config.oms_product_repository_layout.repository_root
    conan_path, python_path = download_python_interpreter(repository_root)
    repository.create_new_or_reuse_repo(repository_root)
    repository.create_branch_and_switch(f'{product_name}/develop')
    for branch_name in generator.get_branch():
        file_provided = False
        main_file_name = ''
        destination = ldi_config.db_path
        remove_directory_tree(destination)
        for file_name, destination_path in generator.get_file(branch_name):
            if not file_provided:
                branch_composed_name = f'{product_name}/feature/{ldi_config.branch_prefix}{branch_name}'
                repository.create_branch_and_switch(branch_composed_name, f'{product_name}/develop')
                file_provided = True
                main_file_name = file_name
            os.makedirs(destination, exist_ok=True)
            shutil.move(file_name, destination_path)
        if not file_provided:
            continue
        execute_command(f'{conan_path} install .', cwd=repository_root)
        execute_command(f'{conan_path} build .', cwd=repository_root)
        if not repository.diff_is_empty():
            repository.commit_current_changes(
                f'Automatic commit of {main_file_name} gathered in {ldi_config.kms_login.download_link}',
                email='Michal.Cermak@Honeywell.com',
                author='Michal Cermak')
            #repository.repository.remotes.origin.push(branch_name)
            log.debug(f'Storing file to the GIT: {main_file_name}')
        else:
            log.debug(f'GIT diff is empty: {main_file_name}')


def hover(browser, xpath):
    element_to_hover_over = wait_for_element_by_xpath(browser, xpath)[0]
    ActionChains(browser).move_to_element(element_to_hover_over).click().perform()


def download_sldbs(kms_files, ldi_config, download_path, complete_config, timeout=30):
    browser_driver = new_chrome_browser(False, download_path)
    login_to_kms(browser_driver, ldi_config)

    log.debug(f'Configuration selection  {complete_config.product_selection_xpath}')
    hover(browser_driver, complete_config.product_selection_xpath)
    time.sleep(5)
    log.debug(f'Configuration selection click: {ldi_config.product_selection}')
    wait_for_element_by_xpath(browser_driver, ldi_config.product_selection)[0].click()

    browser_driver.get(ldi_config.kms_login.download_link)
    log.debug(f'Switching to  {ldi_config.kms_login.download_link}')

    content_frame = wait_for_element_by_id(browser_driver, 'content', timeout)
    browser_driver.switch_to.frame(content_frame)
    sldb_button = wait_for_element_by_xpath(browser_driver, ldi_config.task_and_files_button, timeout)

    sldb_button[0].click()
    try:
        sldb_rows = \
            WebDriverWait(browser_driver, timeout).until(
               lambda br: br.find_elements_by_partial_link_text(ldi_config.kms_login.web_page_match_pattern))
        for row in sldb_rows:
            try:
                print(row)
                kms_files.append(row.text)
                log.debug(f'    Downloading {row.text}')
                row.click()
            except selenium.common.exceptions.StaleElementReferenceException:
                pass
        download_wait(download_path)
    except selenium.common.exceptions.TimeoutException:
        pass

    return browser_driver


if __name__ == "__main__":
    setup_logging_from_config()
    parser = argparse.ArgumentParser(
        description='Script for packaging the build')
    parser.add_argument(
        '--repositoryRoot',
        dest='repository_root',
        required=True)
    options = parser.parse_args(sys.argv[1:])
    process_sldbs(options.repository_root)
