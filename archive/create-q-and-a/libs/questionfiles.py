from PIL import ImageGrab
from ctypes import windll
from enum import Enum
from dataclasses import dataclass
from uuid import uuid4
import os

from libs.runtype import RunType
from libs.myftp import MyFtp

class Choice(Enum):
    a = 97
    b = 98
    c = 99
    d = 100

@dataclass
class QuestionInfo:
    FileName : str
    FileImg : None

@dataclass
class ChoiceInfo:
    FileName : str
    FileImg : None
    Choice : str
    IsCorrect : bool

@dataclass
class AnswerInfo:
    FileName : str
    FileImg : None
    Desc : str
    URL : str

class QuestionData:
    def __init__(self) -> None:
        self._question_info : QuestionInfo = None
        self._choices : dict = dict()
        self._answer_info : AnswerInfo = None
    
    def GrabQuestionImg(self):
        img =  ImageGrab.grabclipboard()
        while img is None:
            input("We can't find the Question screenshot on your clipboard. Please take the screenshot and press Enter.")
            img = ImageGrab.grabclipboard()
        QuestionData.ClearClipboard()
        self._question_info = QuestionInfo(f"{uuid4().hex}.png", img)

    def GrabChoiceImg(self, choice : str, is_correct: bool):
        img = ImageGrab.grabclipboard()
        keep_trying = True
        while img is None:
            input(f"We can't find the Choice {choice} screenshot on your clipboard. Please take the screenshot and press Enter.")
            img = ImageGrab.grabclipboard()
        QuestionData.ClearClipboard()
        self._choices[choice] = ChoiceInfo(f"{uuid4().hex}.png", img, choice, is_correct)

    def AddAnswerUrl(self, answer_url : str):
        self._answer_info = AnswerInfo(None, None, None, answer_url)

    def GrabAnswerImg(self, isMandatory : bool):
        img = ImageGrab.grabclipboard()
        if isMandatory:
            while img is None:
                input("No screenshot found. Please take the answer screenshot")
                img = ImageGrab.grabclipboard()
            self._answer_info.FileImg = img
            self._answer_info.FileName = f"{uuid4().hex}.png"
        else:
            if img is not None:
                QuestionData.ClearClipboard()
                self._answer_info.FileImg = img
                self._answer_info.FileName = f"{uuid4().hex}.png"


    def SaveAllFiles(self, runtpe : RunType):
        question_file_dir : str = os.path.join(os.getcwd(), "question.files")
        myftp = MyFtp(runtpe) if (runtpe == RunType.PETERBDOTIN or runtpe == RunType.STAGEPETERBDOTIN) else None
        # save quesiton file
        self._question_info.FileImg.save(f"{question_file_dir}/{self._question_info.FileName}", 'PNG')
        if myftp:
            myftp.SaveFile(full_file_name=f"{question_file_dir}/{self._question_info.FileName}")
        # save choice files
        for (_, choice) in self._choices.items():
            choice.FileImg.save(f"{question_file_dir}/{choice.FileName}", 'PNG')
            if myftp:
                myftp.SaveFile(full_file_name=f"{question_file_dir}/{choice.FileName}")
        # save answer file, if required
        if self._answer_info.FileImg is not None:
            self._answer_info.FileImg.save(f"{question_file_dir}/{self._answer_info.FileName}", 'PNG')
            if myftp:
                myftp.SaveFile(full_file_name=f"{question_file_dir}/{self._answer_info.FileName}")
            

    @property
    def Question(self):
        return self._question_info

    @property
    def Answer(self):
        return self._answer_info
    
    @property
    def Choices(self):
        return self._choices

    @staticmethod
    def ClearClipboard():
        if windll.user32.OpenClipboard(None):
            windll.user32.EmptyClipboard()
            windll.user32.CloseClipboard()

# def getImageGrab():
#     img = ImageGrab.grabclipboard()
#     while 1:
#         if img is None:
#             input("We can't find the screenshot on your clipboard. Please take the screenshot and press Enter.")
#             img = ImageGrab.grabclipboard()
#         else:
#             img.save(f"{file_name}", 'PNG')
#             ClearClipboard()
#             if db.RunType == RunType.PETERBDOTIN:
#                 myftp.SaveFile(full_file_name=file_name)
#             break

# def SaveFile(db : Database, myftp : MyFtp, file_name : str):
#     img = ImageGrab.grabclipboard()
#     while 1:
#         if img is None:
#             input("We can't find the screenshot on your clipboard. Please take the screenshot and press Enter.")
#             img = ImageGrab.grabclipboard()
#         else:
#             img.save(f"{file_name}", 'PNG')
#             ClearClipboard()
#             if db.RunType == RunType.PETERBDOTIN:
#                 myftp.SaveFile(full_file_name=file_name)
#             break
