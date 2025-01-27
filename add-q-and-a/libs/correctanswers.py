from re import match as rematch
from os.path import isfile

class CorrectAnswers:
    def __init__(self, ans_file_location) -> None:
        self.__correctanswers : dict = dict()
        self.__correctanswers_file_found = True
        if isfile(f'{ans_file_location}/correct.choices'):
            with open(f'{ans_file_location}/correct.choices', encoding='utf-8') as f:
                for l in [x.strip() for x in f if x.strip() != '']:
                    m = rematch('^\s*(\d+?)\.\s*\((.+?)\)$', l)
                    if m:
                        self.__correctanswers[m.groups()[0]] = [x.strip() for x in m.groups()[1].split(",")]
        else:
            self.__correctanswers_file_found = False

    @property
    def CorrectAnswerFileFound(self):
        return self.__correctanswers_file_found

    def getCorrectOptionNames(self, questionNumber):
        if self.__correctanswers.get(questionNumber, None):
            retval : list = list()
            for correctOption in self.__correctanswers.get(questionNumber, None):
                retval.append(correctOption)
            return retval
        else:
            return False


    def getCorrectOptionByQuestion(self, questionNumber, option_name : str):
        if self.__correctanswers.get(questionNumber, None):
            return option_name.lower() in self.__correctanswers.get(questionNumber, None)
        else:
            return False
