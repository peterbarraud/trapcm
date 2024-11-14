from libs.runtype import RunType
from libs.myftp import MyFtp
from os import walk, path

def ftpAllFiles(runtype : RunType, latestVersion : str):
    myftp = MyFtp(runtype)
    uiBuild = input("FTP Build files?.\nPress Y for Yes. Press N for No")
    if uiBuild == 'y' or uiBuild == 'Y':
        __ftpBuildFiles(runtype, myftp, latestVersion)
    uiRestAPI = input("FTP rest.api.php?.\nPress Y for Yes. Press N for No")
    if uiRestAPI == 'y' or uiRestAPI == 'Y':
        __ftpRestAPIFiles(runtype, myftp)
    return (uiBuild, uiRestAPI)

def __ftpBuildFiles(runtype : RunType, myftp : MyFtp, latestVersion : str):
    for root, dirs, files in walk("build", topdown=False):
        for name in files:
            if name == 'index.html':
                htmlStr : str = ''
                with open(path.join(root, name), 'r') as f:
                    htmlStr = f.read()
                    htmlStr = htmlStr.replace("\"index.js\"", f"\"index.js?version={latestVersion}\"")
                    htmlStr = htmlStr.replace("\"index.css\"", f"\"index.css?version={latestVersion}\"")
                with open(path.join(root, name), 'w') as f:
                    f.write(htmlStr)
            myftp.FTPBuildFile(path.join(root, name))

def __ftpRestAPIFiles(runtype : RunType, myftp : MyFtp):
    restApiDir : str = 'the.dr.nefario.backside/services/'
    myftp.FTPRestAPIFiles(f"{restApiDir}rest.api.php")
     
