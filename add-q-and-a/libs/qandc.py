from dataclasses import dataclass

@dataclass
class QandC:
    question : str
    solution : str
    choices : dict
