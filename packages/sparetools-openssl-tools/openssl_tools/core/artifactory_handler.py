#!/usr/bin/env python3
"""
OpenSSL Tools Artifactory Handler
Based on openssl-tools patterns for package repository management
"""

import logging
import os
from pathlib import Path

try:
    import artifactory
    from artifactory import ArtifactoryPath
    ARTIFACTORY_AVAILABLE = True
except ImportError:
    ARTIFACTORY_AVAILABLE = False
    ArtifactoryPath = None

from openssl_tools.util.copy_tools import ensure_target_exists

log = logging.getLogger('__main__.' + __name__)


class ArtifactoryHandler:
    def __init__(self, config_loader):
        self.config = config_loader
        self.connector = None

    def _jfrog_authentication(self, repository_path) -> ArtifactoryPath:
        if not ARTIFACTORY_AVAILABLE:
            raise ImportError("artifactory package not available. Install with: pip install artifactory")
            
        artifactory_path = ArtifactoryPath(
            self.config.artifactory.root + '/' + repository_path,
            auth=(self.config.artifactory.user, self.config.artifactory.password)
        )
        artifactory_path.touch()
        return artifactory_path

    def connect_to_artifactory(self, repository_path) -> ArtifactoryPath:
        """
        Artifactory connector
        """
        return self._jfrog_authentication(repository_path)

    def get_all_in_path(self, repository_path, target):
        """
        Download all files in folder and its subdirectories
        :param repository_path: Artifactory path to get data from
        :param target: Target location to store files to
        :return: None
        """
        self.original_path = repository_path
        self.__get_all_in_path(repository_path, target)

    def __get_all_in_path(self, repository_path, target):
        connector = self.connect_to_artifactory(repository_path)
        for p in connector:
            if p.is_dir():
                self.__get_all_in_path(p, target)
            else:
                subfolders = str(p.parent).replace(str(self.original_path), "")[1:]
                self.store_single_file(p, os.path.join(target, subfolders))

    @staticmethod
    def artifactory_walk(repository_path, topdown=True):
        if not ARTIFACTORY_AVAILABLE:
            raise ImportError("artifactory package not available. Install with: pip install artifactory")
        return artifactory.walk(repository_path, topdown)

    @staticmethod
    def store_single_file(p, target):
        """
        Download single file from artifactory and store it to target location
        :param p: Artifactory object instance (NOT artifactory path)
        :param target: Target location to store file to
        :return: None
        """
        ensure_target_exists(target)
        log.debug(f'Artifactory - Storing file: {p} to {target}, metadata: {p.stat()}')
        with p.open() as fd:
            with open(target, "wb") as out:
                return out.write(fd.read()) > 0