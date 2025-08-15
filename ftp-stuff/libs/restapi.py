from datetime import datetime
time = datetime.now()

from os import path, getcwd
from json import load, dumps
from requests import get, post, Response



class RestApi:
    def __init__(self, runtype) -> None:
        __location__ = path.realpath(path.join(getcwd(), path.dirname(__file__)))
        with open(path.join(__location__, 'config.json')) as f:
            self.__config_json = load(f)
            self.__restapi = self.__config_json['restapi'][runtype.name.lower()]

    def SetBuildDateToNow(self):
        response : Response = get(f"{self.__restapi}setbuilddate")
        return response.json()
        
    def GetCurrentSystemVersion(self):
        response : Response = get(f"{self.__restapi}getcurrentsystemversion")
        return response.json()

    def BumpBuildMajorVersion(self):
        response : Response = get(f"{self.__restapi}bumpbuilmajorversion")
        return response.json()

    def BumpBuildMinorVersion(self):
        response : Response = get(f"{self.__restapi}bumpbuilminorversion")
        return response.json()
