from os import path
from random import choices
import string
from re import match

from libs.database import Database
from libs.runtype import RunType
from libs.ftpapp import ftpAllFiles



def __check_to_ftp_prod(runtype : RunType):
    if runtype == RunType.PETERBDOTIN:
        capCha : str = ''.join(choices(string.ascii_uppercase + string.digits, k=4))
        ui = input(f"You are about to FTP files to Prod. Be doubly sure\nTo confirm enter this Capcha : {capCha}\n")
        if ui == capCha:
            return True
        else:
            return False
    else:
        return True

def _getNextSystemVersion(db : Database):
    currentVersion = db.GetCurrentSystemVersion()
    ui = input(f"The current app version is {currentVersion}. What is the next version?. Or press Enter to exit")
    if ui != '':
        db.UpdateBuildVersion(True, ui)
        return ui
    else:
        return False

def __updateSystemDate(db : Database):    
    db.SetBuildDateToNow(True)
    print("Updated the System Build date and Version number")


def FTPStuff(runtype : RunType):
    db = Database(runtype)
    if __check_to_ftp_prod(runtype):
        db = Database(runtype)
        latestVersion = _getNextSystemVersion(db)
        if latestVersion != False:
            (ftpBuildDone, ftpAPIsDone) = ftpAllFiles(runtype, latestVersion)
            if ftpBuildDone == 'y' or ftpBuildDone == 'Y':
                __updateSystemDate(db)
            else:
                if ftpAPIsDone == 'y' or ftpAPIsDone == 'Y':
                    ui = input("You have FTPd Rest APIs but no build.\nDo you want to update the system date.\nPress Y for Yes. Press N for No")
                    if ui == 'y' or ui == 'Y':
                        __updateSystemDate(db)
                    else:
                        print("Exiting without doing anything")
                else:
                    print("Exiting without doing anything")


            

if __name__ == '__main__':
    rt = input("Runtype\nPress 1 to run on peterb.in\nPress 2 to run on stage peterb.in\n")
    runtype : RunType = None
    # make doubly sure that you want to FTP to Prod
    if rt == "1":
        runtype = RunType.PETERBDOTIN
    elif rt == "2":
        runtype = RunType.STAGEPETERBDOTIN
    if runtype is not None:
        FTPStuff(runtype)
    input("Press Enter to Exit")
