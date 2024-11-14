from os import path
from random import choices
import string
from re import match

from libs.ftpapp import ftpAllFiles
from libs.restapi import RestApi

from enum import Enum

class RunType(Enum):
    JEE = 1
    CBSE = 3

def __check_to_ftp_prod(runtype : RunType):
    capCha : str = ''.join(choices(string.ascii_uppercase + string.digits, k=4))
    ui = input(f"You are about to FTP files to {runtype.name} Prod. Be doubly sure\nTo confirm enter this Capcha : {capCha}\n")
    if ui == capCha:
        return True
    else:
        return False

# def _getNextSystemVersion(restApi : RestApi):
#     currentVersion = restApi.GetCurrentSystemVersion()
#     ui = input(f"The current app version is {currentVersion}. What is the next version?. Or press Enter to exit")
#     if ui != '':
#         db.UpdateBuildVersion(True, ui)
#         return ui
#     else:
#         return False

# def __updateSystemDate(db : Database):    
#     db.SetBuildDateToNow(True)
#     print("Updated the System Build date and Version number")


def FTPStuff(runtype : RunType):
    if __check_to_ftp_prod(runtype):
        restApi : RestApi = RestApi(runtype)
        latestVersion = restApi.GetCurrentSystemVersion()
        if latestVersion != False:
            (ftpBuildDone, ftpAPIsDone) = ftpAllFiles(runtype, latestVersion)
            if ftpBuildDone in ['y','Y']:
                vu = input(f"Build files were updated. The current Build version is {latestVersion}\nPress 1 to bump up the major version: \nPress2 to bump up the minor version: ")
                if vu == "1":
                    restApi.BumpBuildMajorVersion()
                elif vu == "2":
                    restApi.BumpBuildMinorVersion()
                restApi.SetBuildDateToNow()
            elif ftpAPIsDone in ['y','Y']:
                ui = input("You have FTPd Rest APIs but no build.\nDo you want to update the system date.\nPress Y for Yes. Press N for No")
                if ui in ['y','Y']:
                    restApi.SetBuildDateToNow()
            else:
                print("Exiting without doing anything")


            

if __name__ == '__main__':
    rt = input("FTP to JEE: Press 1.\nOr Enter to move out\n")
    if rt == "1":
        FTPStuff(RunType.JEE)
    rt = input("FTP to CBSE: Press 1.\nOr Enter to move out\n")
    if rt == "1":
        FTPStuff(RunType.CBSE)
    input("Press Enter to Exit")
