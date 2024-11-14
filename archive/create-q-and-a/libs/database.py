import mysql.connector
from mysql.connector.errors import IntegrityError
import json
import os
from dataclasses import dataclass
from uuid import uuid4
from datetime import datetime
time = datetime.now()

from libs.runtype import RunType
from libs.questionfiles import QuestionInfo, ChoiceInfo, AnswerInfo
# from libs.topics import TopicVisibility

@dataclass
class Subject:
    ID: int
    Name: str
    Title: str

@dataclass
class QuestionType:
    ID: int
    Name: str
    Title: str

@dataclass
class Topic:
    ID: int
    Title: str
    ShowTopic : str



class Database:
    def __init__(self, runtype : RunType) -> None:
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, 'config.json')) as f:
            config_json = json.load(f)
            if runtype == RunType.PETERBDOTIN:
                self._db_config = config_json['db']['peterbdotin']
            elif runtype == RunType.LOCAL:
                self._db_config = config_json['db']['localhost']
            elif runtype == RunType.STAGEPETERBDOTIN:
                self._db_config = config_json['db']['stagepeterbdotin']
        self._runtype = runtype
        self.Connect()
           
    @property
    def Subjects(self) -> dict:
        subjects = dict()
        cursor = self._connection.cursor()
        cursor.execute("select * from subject")
        for row in cursor:
            subjects[row[0]] = Subject(*row)
        return subjects
    
    @property
    def QuestionTypes(self) -> dict:
        q_types = dict()
        cursor = self._connection.cursor()
        cursor.execute("select * from questiontype")
        for row in cursor:
            q_types[row[0]] = Subject(*row)
        return q_types

    @property
    def RunType(self) -> RunType:
        return self._runtype
    
    def TopicsBySubject(self, subject_id) -> dict:
        topics = dict()
        if not self.IsConnected:
            self.Connect()
        cursor = self._connection.cursor()
        cursor.execute(f"select id,title,show_topic from topic where subject_id = {subject_id};")
        for row in cursor:
            topics[row[0]] = Topic(*row)
        return topics
    
    def TopicsBySubjectByVisibility(self, subject_id, topic_visibility) -> dict:
        topics = dict()
        cursor = self._connection.cursor()
        sql_select_query = "select id,title,show_topic from topic where subject_id = %s and show_topic = %s"
        where_clause = (subject_id, topic_visibility.value)
        cursor.execute(sql_select_query, where_clause)
        for row in cursor:
            topics[row[0]] = Topic(*row)
        return topics


    def AddQuestion(self, subject : Subject, topic : Topic, q_type : QuestionType, questionInfo : QuestionInfo):
        cursor = self._connection.cursor()
        sql_insert_query = "INSERT INTO question (q_type_id, topic_id, file_name) VALUES (%s,%s,%s)"
        insert_values = (q_type.ID, topic.ID, questionInfo.FileName)
        cursor.execute(sql_insert_query, insert_values)
        return cursor.lastrowid
        
    def AddChoice(self, question_id, choiceInfo : ChoiceInfo):
        # the remote db connection seems to break (maybe timeout issues)
        # so, before any such operation, we'll check if connected
        # and reconnect if needed
        # if not self.IsConnected:
        #     self.Connect()
        cursor = self._connection.cursor()
        sql_insert_query = "INSERT INTO choice (question_id, correct_ans, file_name) VALUES (%s,%s,%s)"
        insert_values = (question_id, 1 if choiceInfo.IsCorrect else 0, choiceInfo.FileName)
        cursor.execute(sql_insert_query, insert_values)
        return cursor.lastrowid
    
    def _obsolete_SetCorrectChoice(self, choice_id):
        cursor = self._connection.cursor()
        sql_update_query = "UPDATE choice SET correct_ans = %s WHERE id = %s"
        update_values = (1, choice_id)
        cursor.execute(sql_update_query, update_values)

    def AddAnswer(self, question_id,answerInfo : AnswerInfo):
        cursor = self._connection.cursor()
        sql_insert_query = "INSERT INTO answer (question_id, description, url, file_name) VALUES (%s,%s,%s,%s)"
        insert_values = (question_id, answerInfo.Desc, answerInfo.URL, answerInfo.FileName)
        cursor.execute(sql_insert_query, insert_values)
        choice_id = cursor.lastrowid
    
    def AddTopic(self, topic_title, subject_id) -> None:
        # the remote db connection seems to break (maybe timeout issues)
        # so, before any such operation, we'll check if connected
        # and reconnect if needed
        # if not self.IsConnected:
        #     self.Connect()
        cursor = self._connection.cursor()
        sql_insert_query = "INSERT INTO topic (title, subject_id) VALUES (%s,%s)"
        insert_values = (topic_title, subject_id)
        try:
            cursor.execute(sql_insert_query, insert_values)
            self._connection.commit()
        except IntegrityError as ie:
            print(f"Duplicate topic title {topic_title}")

    def ShowHideTopic(self, topic_id, topic_visibility):
        cursor = self._connection.cursor()
        sql_update_query = "UPDATE topic SET show_topic = %s WHERE id = %s"
        update_values = (topic_visibility.value, topic_id)
        cursor.execute(sql_update_query, update_values)


    def SetTopicToShow(self, topic : Topic, doCommit : bool):
        if not self.IsConnected:
            self.Connect()
        cursor = self._connection.cursor()
        sql_update_query = "UPDATE topic SET show_topic = %s WHERE id = %s"
        update_values = (1, topic.ID)
        cursor.execute(sql_update_query, update_values)
        if doCommit:
            self._connection.commit()

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
    
    def executeQuery(self, query : str, doCommit : bool = True):
        if not self.IsConnected:
            self.Connect()
        cursor = self._connection.cursor()
        cursor.execute(query)
        if doCommit:
            self._connection.commit()
        return cursor

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
