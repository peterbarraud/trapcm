from ftplib import FTP
from re import search as research
import os
import json

from libs.runtype import RunType

class MyFtp:
    def __init__(self, runtype : RunType) -> None:
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, 'config.json')) as f:
            config_json = json.load(f)
            ftp_config = None
            if runtype == RunType.PETERBDOTIN:
                ftp_config = config_json['ftp']['prod']
            elif runtype == RunType.STAGEPETERBDOTIN:
                ftp_config = config_json['ftp']['stage']

            self._ftp = FTP(ftp_config['server'])
            self._ftp.login(ftp_config['username'],ftp_config['pwd'])

    def SaveFile(self, full_file_name : str) -> str:
        with open(full_file_name, 'rb') as f:
            search_group = research('[a-z0-9]*?.png',full_file_name)
            file2BeSavedAs = search_group.group(0)
            ftpCommand = "STOR %s"%file2BeSavedAs;
            self._ftp.cwd('/question.files')
            ftpResponseMessage = self._ftp.storbinary(ftpCommand, fp=f);
    
    def FTPBuildFile(self, full_file_name : str):
        # always ensure you're in root
        self._ftp.cwd('/')
        with open(full_file_name, 'rb') as f:
            file2BeSavedAs = os.path.basename(full_file_name).split('/')[-1]
            ftpCommand = "STOR %s"%file2BeSavedAs;
            if 'includes' in full_file_name:
                self._ftp.cwd('/includes')
            ftpResponseMessage = self._ftp.storbinary(ftpCommand, fp=f);

    def FTPRestAPIFiles(self, full_file_name : str):
        # always ensure you're in root
        self._ftp.cwd('/')
        with open(full_file_name, 'rb') as f:
            # search_group = research('[a-z0-9]*?.php',full_file_name)
            # file2BeSavedAs = search_group.group(0)
            file2BeSavedAs = os.path.basename(full_file_name).split('/')[-1]
            ftpCommand = "STOR %s"%file2BeSavedAs;
            self._ftp.cwd('/services')
            ftpResponseMessage = self._ftp.storbinary(ftpCommand, fp=f);

    def __del__(self) -> None:
        self._ftp.close()