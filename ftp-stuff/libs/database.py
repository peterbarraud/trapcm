import mysql.connector
from mysql.connector.errors import IntegrityError
import json
import os
from uuid import uuid4
from datetime import datetime
time = datetime.now()

from libs.runtype import RunType
# from libs.topics import TopicVisibility


class Database:
    def __init__(self, runtype : RunType) -> None:
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, 'config.json')) as f:
            config_json = json.load(f)
            if runtype == RunType.PETERBDOTIN:
                self._db_config = config_json['db']['peterbdotin']
            elif runtype == RunType.STAGEPETERBDOTIN:
                self._db_config = config_json['db']['stagepeterbdotin']
        self._runtype = runtype
        self.Connect()
           


    @property
    def RunType(self) -> RunType:
        return self._runtype




        

    def SetBuildDateToNow(self, doCommit : bool):
        if not self.IsConnected:
            self.Connect()
        sql_update_query = "UPDATE trapcmsys SET lastbuild = %s WHERE id = %s;"
        cursor = self._connection.cursor()
        now_time = datetime.now()
        update_values = (now_time.strftime("%Y-%m-%d %H:%M:%S"), 1)
        cursor.execute(sql_update_query, update_values)
        if doCommit:
            self._connection.commit()

        
    def GetCurrentSystemVersion(self):
        if not self.IsConnected:
            self.Connect()
        sql_select_query = "select version from trapcmsys;"
        cursor = self._connection.cursor()
        cursor.execute(sql_select_query)
        for row in cursor:
            return row[0]

    def UpdateBuildVersion(self, doCommit : bool, versionNumber):
        if not self.IsConnected:
            self.Connect()
        sql_update_query = "UPDATE trapcmsys SET version = %s WHERE id = %s;"
        update_values = (versionNumber, 1)
        cursor = self._connection.cursor()
        cursor.execute(sql_update_query, update_values)
        if doCommit:
            self._connection.commit()
    

    def Commit(self) -> None:
        self._connection.commit()

    def Rollback(self) -> None:
        self._connection.rollback()
    
    def Connect(self) -> None:
        self._connection = mysql.connector.connect(host=self._db_config['host'],
                                                   user=self._db_config['user'],
                                                   password=self._db_config['password'],
                                                   database=self._db_config['database'])



    
    @property
    def IsConnected(self) -> bool:
        return self._connection.is_connected()
    

    def __del__(self):
        self._connection.close()

if __name__ == '__main__':
    print("This is a library. It will not run on it's own. It must be called from a client")
