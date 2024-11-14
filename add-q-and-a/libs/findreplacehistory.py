from pathlib import Path

class FindReplaceHistory():
    def __init__(self) -> None:
        self.__set_findreplace_history()
        self.__set_spl_findreplace_history()
    
    def __set_findreplace_history(self):
        self.__file_path = f"{Path(__file__).parent.resolve()}/history"
        with open(f'{self.__file_path}/find.history', encoding='utf-8') as f:
            self.__find_history = [x.strip() for x in f]
        with open(f'{self.__file_path}/replace.history', encoding='utf-8') as f:
            self.__replace_history = [x.strip() for x in f]
        self.__find_history_index = 0
        self.__replace_history_index = 0

    def __set_spl_findreplace_history(self):
        __file_path = f"{Path(__file__).parent.resolve()}/history"
        with open(f'{self.__file_path}/spl.find.history', encoding='utf-8') as f:
            self.__spl_find_history = [x.strip() for x in f]
        with open(f'{self.__file_path}/spl.replace.history', encoding='utf-8') as f:
            self.__spl_replace_history = [x.strip() for x in f]
        self.__spl_find_history_index = 0
        self.__spl_replace_history_index = 0



    @property
    def CurrentInFindHistory(self):
        return self.__find_history[self.__find_history_index]

    @property
    def CurrentInReplaceHistory(self):
        return self.__replace_history[self.__replace_history_index]

    @property
    def nextInFindHistory(self):
        if self.__find_history_index < len(self.__find_history) - 1:
            self.__find_history_index += 1
        return self.__find_history[self.__find_history_index]
    @property
    def nextInReplaceHistory(self):
        if self.__replace_history_index < len(self.__replace_history) - 1:
            self.__replace_history_index += 1
        return self.__replace_history[self.__replace_history_index]

    @property
    def PrevInFindHistory(self):
        if self.__find_history_index > 0:
            self.__find_history_index -= 1
        return self.__find_history[self.__find_history_index]
    @property
    def prevInReplaceHistory(self):
        if self.__replace_history_index > 0:
            self.__replace_history_index -= 1
        return self.__replace_history[self.__replace_history_index]

    # For history items
    # what we are doing is put the item at the top of the list
    # which means that if the item already exists, we are doing to remove it and then insert another copy at the top

    def __add_to_history(self, history_list, item_to_add):
        if item_to_add.strip() in history_list:
            if item_to_add in history_list:
                history_list.remove(item_to_add)
        history_list.insert(0,item_to_add)

    def addToFindHistory(self, f):
        self.__add_to_history(self.__find_history, f)

    def addToReplaceHistory(self, r):
        self.__add_to_history(self.__replace_history, r)

    def Save(self)  -> None:
        with open(f'{self.__file_path}/find.history', 'w', encoding='utf-8') as f:
            f.write("\n".join(self.__find_history))
        with open(f'{self.__file_path}/replace.history', 'w', encoding='utf-8') as f:
            f.write("\n".join(self.__replace_history))

    @property
    def nextInSplFindHistory(self):
        if self.__spl_find_history_index < len(self.__spl_find_history) - 1:
            self.__spl_find_history_index += 1
        return self.__spl_find_history[self.__spl_find_history_index]
    @property
    def nextInSplReplaceHistory(self):
        if self.__spl_replace_history_index < len(self.__spl_replace_history) - 1:
            self.__spl_replace_history_index += 1
        return self.__spl_replace_history[self.__spl_replace_history_index]

    @property
    def PrevInSplFindHistory(self):
        if self.__spl_find_history_index > 0:
            self.__spl_find_history_index -= 1
        return self.__spl_find_history[self.__spl_find_history_index]
    @property
    def prevInSplReplaceHistory(self):
        if self.__spl_replace_history_index > 0:
            self.__spl_replace_history_index -= 1
        return self.__spl_replace_history[self.__spl_replace_history_index]

