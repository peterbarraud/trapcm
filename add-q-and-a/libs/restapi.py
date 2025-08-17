from os import path, getcwd
from json import load, dumps
from requests import get, post, Response



class RestApi:
    def __init__(self) -> None:
        __location__ = path.realpath(path.join(getcwd(), path.dirname(__file__)))
        with open(path.join(__location__, 'config.json')) as f:
            self.__config_json = load(f)

    @property
    def QandAFilesRoot(self):
        return self.__config_json['qandaFilesRoot']

    @property
    def PCMEnvs(self):
        return self.__config_json['restapi']
        
    @property
    def QuestionPlacehoderImg(self):
        return self.__config_json['questionplacehoderimg']

    @property
    def AnswerPlacehoderImg(self):
        return self.__config_json['answerplacehoderimg']

    @property
    def NoAnswerAvailableImg(self):
        return self.__config_json['noansavailableimg']

    def getSubjectsAndTopics(self, restapiurl : str,testName):
        response = get(f"{restapiurl}getallsubjectsandtopics/{testName}")
        return response.json()

    def getQuestionSources(self, restapiurl : str):
        response = get(f"{restapiurl}getquestionsources")
        return response.json()

    def getQuestionTypes(self, restapiurl : str):
        response : Response = get(f"{restapiurl}getquestiontypes")
        return response.json()
    
    def saveQuestion(self, questionDict : dict, question_id : str, restapiurl : str):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        response : Response = post(f"{restapiurl}savequestion/{question_id}", data=dumps(questionDict), headers=headers)
        return response.json()
    
    def getRecentQuestion(self, restapiurl : str, offset : int):
        response : Response = get(f"{restapiurl}getrecentquestion/{offset}")
        return response.json()

    def getQuestion(self, restapiurl : str, questionid : str):
        response : Response = get(f"{restapiurl}getquestionbyid/{questionid}")
        return response.json()

    def getTopicAndSubjectByTopicID(self, restapiurl : str, topicid : str):
        response : Response = get(f"{restapiurl}gettopicandsubjectbytopicyid/{topicid}")
        return response.json()


    def deleteQuestion(self, restapiurl : str, questionid : str):
        response : Response = get(f"{restapiurl}deletequestionbyid/{questionid}")
        return response.json()

