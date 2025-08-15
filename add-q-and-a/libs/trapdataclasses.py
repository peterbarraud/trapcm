from dataclasses import dataclass
from enum import Enum

class AddFromUrl(Enum):
    Question = 1
    Answer = 2
    Choices = 3

@dataclass
class ImageDim:
    Width : int = 400
    Height : int = 660

@dataclass
class FunnyValueChoice:
    HasFunnyChoice : bool = False
    Number : int = None
    BadValue : str = None
    GoodValue : str = None

@dataclass
class ChoiceData:
    ChoiceValue : str = None
    ChoiceState : str = None

class TestType(Enum):
    All = 1
    JEEONLY = 2
    CBSEONLY = 3

class MsgType(Enum):
    ERR = 1
    INFO = 2
    WARN = 3

class ReplaceWhat(Enum):
    QUESTIONONLY = 1
    CHOICESONLY = 2
    BOTH = 3
    CLOSEDIALOG = 4

class ReplaceDialogState(Enum):
    ISOPEN = 1
    ISCLOSED = 2

class QuestionDirection(Enum):
    Next = 1
    Previous = 2

@dataclass
class QuestionData:
    SubjectTitle : str = None
    TopicTitle : str  = None
    SourceTitle : str = None
