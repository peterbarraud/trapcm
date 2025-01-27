# from typing import Any, List, Optional, Union
import flet as ft
# from flet_core.control import Control, OptionalNumber
from flet_core.ref import Ref
# from flet_core.types import AnimationValue, OffsetValue, ResponsiveNumber, RotateValue, ScaleValue
from ctypes import windll
from PIL import ImageGrab, Image, BmpImagePlugin, PngImagePlugin
import base64
from io import BytesIO
from enum import Enum
from os.path import isfile
import cv2
from dataclasses import dataclass
from re import sub as resub, findall, split as resplit, error as reerror, search as research
import collections
from urllib.parse import unquote


from libs.restapi import RestApi
from libs.clipboardtext import getClipboardData, setClipboardData
from libs.getqandc import getQandC
from libs.souper import getTextFromSoup
from libs.findreplacehistory import FindReplaceHistory
from libs.littlebeepbeep import beeper
from libs.correctanswers import CorrectAnswers
from libs.listings import Listings, ListingInfo

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

class theApp(ft.UserControl):
    def __init__(self, page : ft.Page):
        super().__init__()

        self.__imageDim = ImageDim()
        self.__restapi = RestApi()
        self.__questionData = QuestionData()

        self.__selected_restapi_url : str = None
        self.__selected_restapi_url : str = None
        self.__selected_subject_id : str = None
        self.__selected_topic_id : str = None
        self.__selected_source_id : str = None
        self.__selected_question_id = -1
        self.__recent_question_offset = 0
        self.__correctAnwers = None
        self.__qanda_number_infocus = False


        self.__tags = ['<b>','<sup>','<sub>','<br>','<i>']

        self.__listings : Listings = Listings()
        
        self.__choice_counter = 65 # which is A caps
        self.__questionIDTxt : ft.Text = ft.Text(self.__selected_question_id, size=10);
        self.__is_advanced_q_checkbox : ft.Checkbox = ft.Checkbox(label="Is A(d)v", value=False)
        self.__is_fitb_q_checkbox : ft.Checkbox = ft.Checkbox(label="Is FITB",tooltip="Fill-in-the-blanks question", value=False)
        self.__is_mmcq_q_checkbox : ft.Checkbox = ft.Checkbox(label="Is MMCQ",tooltip="Is this MMCQ question", value=False)
        self.__answer_not_required : ft.Checkbox = ft.Checkbox(label="Ans Not Req",tooltip="Answer not required", value=False)
        self.__change_topic : ft.Checkbox = ft.Checkbox(label="Change topic", value=False,visible=False)
        self.__change_source : ft.Checkbox = ft.Checkbox(label="Change source", value=False,visible=False)
        self.__funny_val_choice : FunnyValueChoice = FunnyValueChoice()




        self.__questionRow : ft.Row = ft.Row([self.__questionIDTxt,
                                              ft.ElevatedButton("Del",on_click=self.__delete_question,tooltip="Delete question"),
                                              self.__is_advanced_q_checkbox,self.__change_topic,
                                              self.__is_fitb_q_checkbox,
                                              self.__is_mmcq_q_checkbox,
                                              self.__answer_not_required,
                                              self.__change_source,
                                              ft.ElevatedButton(text="Cls Cs",on_click=self.__clear_choices,tooltip="Clear all Choices"),
                                              ft.ElevatedButton("-",on_click=self.__change_image_container_heights,
                                                                tooltip="Reduce container heights",key="decrease"),
                                              ft.ElevatedButton("S.Rpl",on_click=self.__spl_replace_both,
                                                                tooltip="Special find/replace"),
                                              ft.ElevatedButton("S(w)Cs",on_click=self.__open_rearrange_choices_dialog,
                                                                tooltip="Rearrange choices"),
                                              ft.ElevatedButton("Rpl(H)",on_click=self.__open_replace_dialog,
                                                                tooltip="Replace text in Question"),
                                              ft.ElevatedButton("+",on_click=self.__change_image_container_heights,
                                                                tooltip="Increase container heights",key="increase")])

        self.__questionContainer : ft.Container = ft.Container(
                        content=ft.Image(src_base64=self.__restapi.QuestionPlacehoderImg,
                                         fit=ft.ImageFit.CONTAIN,
                                         width=self.__imageDim.Width,
                                         height=self.__imageDim.Height),
                                         on_long_press=self.__add_question)
        self.__answerContainer : ft.Container = ft.Container(
                        content=ft.Image(src_base64=self.__restapi.AnswerPlacehoderImg,
                                         fit=ft.ImageFit.CONTAIN,width=self.__imageDim.Width,height=self.__imageDim.Height),
                                         on_click=self.__add_answer)

        self.__choices : ft.Row = ft.Row()
        self.__answer_url : ft.TextField = ft.TextField(label="Answer (G)oogle U(R)L",on_submit=self.__save_question_click,width=150)
        self.__qanda_folder_number : ft.TextField = ft.TextField(label="Folder name",width=170)
        self.__qanda_topic_number : ft.TextField = ft.TextField(label="Topic#",width=90,on_blur=self.__qanda_topic_number_update)
        self.__qanda_number : ft.TextField = ft.TextField(label="QAndA number",width=90,
                                                          on_submit=self.__get_qanda_image,
                                                          on_focus=self.__qanda_number_gotfocus,
                                                          on_blur=self.__qanda_number_lostfocus)
        self.__marks : ft.TextField = ft.TextField(label="Marks",width=90,on_blur=self.__marks_lostfocus)
        
        self.__menu : ft.Row = ft.Row()
        self.__dropdowns : ft.Row = ft.Row()
        self.__waitSignal = ft.ElevatedButton(text="Waiting for something awesome",visible=False,height=200)
        self.__environmentDropDown : ft.Dropdown = ft.Dropdown(label="Environment",on_change=self.__env_select)
        self.__subjectDropDown : ft.Dropdown = ft.Dropdown(label="Subject",on_change=self.__subject_select)
        self.__topicDropDown : ft.Dropdown = ft.Dropdown(label="Topic",on_change=self.__topic_select)
        self.__sourceDropDown : ft.Dropdown = ft.Dropdown(label="Source",on_change=self.__source_select)
        self.__dropdowns.controls = [self.__environmentDropDown, self.__subjectDropDown, self.__topicDropDown, self.__sourceDropDown]
        self.__previous_question_button = ft.ElevatedButton(text="<",on_click=self.__show_previous_question,tooltip="Previous question")
        self.__next_question_button = ft.ElevatedButton(text=">",on_click=self.__show_next_question,tooltip="Next question")
        self.__InfoBox : ft.Text = ft.Text("Information box")
        

        self.__buildAppMenu()
        self.__buildEnvDropDown()

        self.__yesnoprompt = ft.AlertDialog(
            modal=True,
            title=ft.Text("Please confirm"),
            content=ft.Text("You haven't added any choices. Click Yes to save as Long form. Click No to add choices."),
            actions=[
                ft.TextButton("Yes", on_click=self.__close_yesnoprompt_yes),
                ft.TextButton("No", on_click=self.__close_yesnoprompt_no),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )


        self.__funnyvalueprompt = ft.AlertDialog(
            modal=False,
            title=ft.Text("Please confirm"),
            content=ft.Text(f"{self.__funny_val_choice.GoodValue}  You haven't added any choices. Click Yes to save as Long form. Click No to add choices."),
            actions=[
                ft.TextButton("Yes", on_click=self.__close_funnyvalueprompt_yes)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )

        self.__confirmDelete = ft.AlertDialog(
            modal=True,
            title=ft.Text("Please confirm"),
            content=ft.Text("Are you sure you want to delete the current Question?"),
            actions=[
                ft.TextButton("Yes", on_click=self.__close_confirmdelete_yes),
                ft.TextButton("No", on_click=self.__close_confirmdelete_no),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )


        self.__findReplaceHistory = FindReplaceHistory()

        self.__find_textbox : ft.TextField = ft.TextField(label="Find what",on_focus=self.__find_replace_textbox_focus,on_blur=self.__find_replace_textbox_blur,data="find_textbox")
        self.__replace_textbox : ft.TextField = ft.TextField(label="Replace with",on_focus=self.__find_replace_textbox_focus,on_blur=self.__find_replace_textbox_blur,data="replace_textbox")
        self.__findreplace_info : ft.Text = ft.Text(max_lines=1)
        self.__choices_rearrange_info : ft.Text = ft.Text()
        page.on_keyboard_event = self.__on_keyboard
        self.__from_text_infocus = False
        self.__replace_with_infocus = False
        self.__replace_dialog_state = ReplaceDialogState.ISCLOSED

        self.__replace_text_prompt : ft.AlertDialog = ft.AlertDialog(
            modal=True,
            content=ft.Column([self.__find_textbox,self.__replace_textbox,self.__findreplace_info],height=130),
            actions=[ft.TextButton("Question only", on_click=self.__replace_in_question,data=ReplaceWhat.QUESTIONONLY),
                     ft.TextButton("Choices only", on_click=self.__replace_in_question,data=ReplaceWhat.CHOICESONLY),
                     ft.TextButton("Both", on_click=self.__replace_in_question,data=ReplaceWhat.BOTH),
                     ft.TextButton("C(l)ose", on_click=self.__replace_in_question,data=ReplaceWhat.CLOSEDIALOG),
                     ft.TextButton("More info", on_click=self.__find_replace_info,data=ReplaceWhat.CLOSEDIALOG),
                     
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.__choices_to_switch_row : ft.Row = ft.Row()

        self.__rearrange_choices_dialog : ft.AlertDialog = ft.AlertDialog(
            modal=False,
            content=ft.Column([self.__choices_to_switch_row,self.__choices_rearrange_info],height=75),
            actions=[ft.TextButton("OK", on_click=self.__rearrange_choices)],
            actions_alignment=ft.MainAxisAlignment.END

        )

        self.__add_from_url_prompt : ft.AlertDialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("What do you want to get from this URL"),
            content=ft.Text(""),
            actions=[
                ft.TextButton("All", on_click=self.__add_from_url,data=[AddFromUrl.Question,AddFromUrl.Answer,AddFromUrl.Choices],key="choices"),
                ft.TextButton("Q&A", on_click=self.__add_from_url,data=[AddFromUrl.Question,AddFromUrl.Answer],key="q&a"),
                ft.TextButton("Q&Choices", on_click=self.__add_from_url, data=[AddFromUrl.Question,AddFromUrl.Choices],key="choices"),
                ft.TextButton("A&Choices", on_click=self.__add_from_url, data=[AddFromUrl.Answer,AddFromUrl.Choices],key="choices"),
                ft.TextButton("Only Q", on_click=self.__add_from_url,data=[AddFromUrl.Question],key="onlyq"),
                ft.TextButton("Only A", on_click=self.__add_from_url,data=[AddFromUrl.Answer],key="onlya"),
                ft.TextButton("Only Choices", on_click=self.__add_from_url,data=[AddFromUrl.Choices],key="choices"),
                ft.TextButton("Cancel", on_click=self.__close_details_prompt,key="cancel"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
            
        )

    def __info_box_update(self, txt, appendTxt=True):
        if appendTxt:
            self.__InfoBox.value += f"\n{txt}"
        else:
            self.__InfoBox.value = txt
        self.__InfoBox.update()    

    def __close_confirmdelete_yes(self, e):
        self.__restapi.deleteQuestion(self.__selected_restapi_url, self.__selected_question_id)
        self.__reset_question()
        self.__confirmDelete.open = False
        self.page.update()

    def __close_confirmdelete_no(self, e):
        self.__confirmDelete.open = False
        self.page.update()

    def OpenAlert(self, title):
        dlg : ft.AlertDialog = ft.AlertDialog(title=ft.Text(title))
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def __delete_question(self, e):
        if self.__selected_question_id != -1:
            self.__confirmDelete.open = True
            self.page.dialog = self.__confirmDelete
            self.page.update()
        else:
            self.OpenAlert("Select a question to delete. You're right now on a New question")
    
    def __increase_image_container_heights(self):
        height_delta :int = 200
        if isinstance(self.__questionContainer.content,ft.Image):
            self.__questionContainer.content.height += height_delta
            self.__questionContainer.update()
        if isinstance(self.__answerContainer.content,ft.Image):
            self.__answerContainer.content.height += height_delta
            self.__answerContainer.update()
    
    def __close_funnyvalueprompt_yes(self, e):
        self.__choices.controls[self.__funny_val_choice.Number].content.value = self.__funny_val_choice.GoodValue
        self.__choices.controls[self.__funny_val_choice.Number].content.update()
        self.__funnyvalueprompt.open = False
        self.page.update()
        # reset funny value object
        self.__funny_val_choice.HasFunnyChoice = False
        self.__funny_val_choice.Number = None
        self.__funny_val_choice.BadValue = None
        self.__funny_val_choice.GoodValue = None


    def __decrease_image_container_heights(self):
        height_delta :int = 200
        if isinstance(self.__questionContainer.content,ft.Image):
            self.__questionContainer.content.height -= height_delta
            self.__questionContainer.update()
        if isinstance(self.__answerContainer.content,ft.Image):
            self.__answerContainer.content.height -= height_delta
            self.__answerContainer.update()
    
    def __change_image_container_heights(self, e):
        if e.control.key == "decrease":
            self.__decrease_image_container_heights()
        elif e.control.key == "increase":
            self.__increase_image_container_heights()
        
    def __qanda_topic_number_update(self, e):
        if self.__selected_subject_id:
            if self.__selected_source_id:
                qanda_file_path = f"{self.__restapi.QandAFilesRoot}/{self.__questionData.SourceTitle.lower()}/{self.__questionData.SubjectTitle.lower()}/{self.__qanda_folder_number.value}"
                ans_file_location = f"{qanda_file_path}/answer-files/topic{e.control.value}"
                self.__correctAnwers = CorrectAnswers(ans_file_location)
                if not self.__correctAnwers.CorrectAnswerFileFound:
                    self.OpenAlert(f"Correct choices file NOT found")
            else:
                self.OpenAlert("You haven't selected a source")
        else:
            self.OpenAlert("You haven't selecgted a subject")

    def __close_yesnoprompt_no(self, e):
        self.__yesnoprompt.open = False
        self.page.update()

    def __close_yesnoprompt_yes(self, e):
        self.__yesnoprompt.open = False
        self.page.update()
        # save as long form
        self.__save_question(self.QuestionType.long)


    def __open_yesnoprompt(self):
        self.__yesnoprompt.open = True
        self.page.dialog = self.__yesnoprompt
        self.page.update()


    def __buildEnvDropDown(self):
        envs = self.__restapi.PCMEnvs
        options : list = []
        for i, v in envs.items():
            options.append(ft.dropdown.Option(key=v,text=i))
        self.__environmentDropDown.options = options

    def __buildSourcesDropDown(self):
        options : list = []
        for source in self.__restapi.getQuestionSources(self.__selected_restapi_url):
            options.append(ft.dropdown.Option(text=source['title'],key=source['id']))
        self.__sourceDropDown.options = options
        self.__sourceDropDown.update()


    def __buildSubjectDropDown(self):
        options : list = []
        for subject in self.__subjectsandtopics:
            options.append(ft.dropdown.Option(text=subject['title'],key=subject['id']))
        self.__subjectDropDown.options = options
        self.__subjectDropDown.update()

    @staticmethod
    def __get_topic_title(topic):
        topic_title : str = topic['title']
        if topic['show_topic'] == '1':
            topic_title += " (V)"
        else:
            topic_title += " (H)"
        return topic_title

    def __buildTopicDropDown(self):
        options : list = []
        for subject in self.__subjectsandtopics:
            if subject['id'] == self.__selected_subject_id:
                for topic in subject['topics']:
                    if (topic_title := theApp.__get_topic_title(topic)) is not None:
                        options.append(ft.dropdown.Option(text=topic_title,key=topic['id']))
                break
        self.__topicDropDown.options = options
        self.__topicDropDown.update()

    def __open_rearrange_choices_dialog(self, _):
        if len(self.__choices.controls) > 1:
            col_width : int = 40
            choice_controls : list = list()

            for i in range(int(len(self.__choices.controls)/2)):
                choice_controls.append(ft.TextField(label=chr(i+65),width=col_width,data=chr(i+65)))
            self.__choices_to_switch_row.controls = choice_controls


            self.__rearrange_choices_dialog.open = True
            self.page.dialog = self.__rearrange_choices_dialog
            self.page.update()
        else:
            self.__info_box_update("No choices available",False)

    def __do_rearrange_choices(self):
        j = 0
        items_for_update : list = list()
        for i in range(1,len(self.__choices.controls),2):
            choiceContainer : ft.Container = self.__choices.controls[i]
            if isinstance(choiceContainer.content,ft.TextField):
                x = ChoiceData(choiceContainer.content.value,self.__choices.controls[i-1].value)
                items_for_update.append(ChoiceData(choiceContainer.content.value,self.__choices.controls[i-1].value))
        for i in range(1,len(self.__choices.controls),2):
            choiceContainer : ft.Container = self.__choices.controls[i]
            if isinstance(choiceContainer.content,ft.TextField):
                choice_pos = ord(self.__choices_to_switch_row.controls[j].value.upper())-65
                choiceContainer.content.value = items_for_update[choice_pos].ChoiceValue
                choiceContainer.content.update()
                self.__choices.controls[i-1].value = items_for_update[choice_pos].ChoiceState
                self.__choices.controls[i-1].update()
                j += 1
        self.__rearrange_choices_dialog.open = False
        self.page.update()

    def __rearrange_choices(self, _):
        empty_choices = [x.data for x in self.__choices_to_switch_row.controls if x.value.strip() == '']
        if any(empty_choices):
            self.__choices_rearrange_info_update("Choices can't be empty: " + ",".join(empty_choices),MsgType.ERR)
        else:
            choices_for_check = [x.value for x in self.__choices_to_switch_row.controls]
            duplicates = [item for item, count in collections.Counter(choices_for_check).items() if count > 1]
            if len(duplicates):
                self.__choices_rearrange_info_update("Duplicate Choices not allowed: " + ",".join(duplicates),MsgType.ERR)
            else:
                choices_data = [x.data.upper() for x in self.__choices_to_switch_row.controls]
                choice_outside_range = [x for x in choices_for_check if x.upper() not in choices_data]
                if len(choice_outside_range):
                    self.__choices_rearrange_info_update("Some incorrect Choice values: " + ",".join(choice_outside_range),MsgType.ERR)
                else:
                    self.__do_rearrange_choices()
            

    def __open_replace_dialog(self, _):
        self.__replace_text_prompt.open = True
        self.page.dialog = self.__replace_text_prompt
        self.__replace_dialog_state = ReplaceDialogState.ISOPEN
        self.page.update()
        self.__find_textbox.focus()
        copyText = getClipboardData()
        self.__find_textbox.value = copyText if copyText else self.__findReplaceHistory.CurrentInFindHistory
        # if copyText:
        #     self.__find_textbox.value    
        # self.__find_textbox.value = self.__findReplaceHistory.CurrentInFindHistory
        self.__find_textbox.update()
        self.__replace_textbox.value = self.__findReplaceHistory.CurrentInReplaceHistory
        self.__replace_textbox.update()

    def __close_replace_dialog(self):
        self.__replace_text_prompt.open = False
        self.__replace_dialog_state = ReplaceDialogState.ISCLOSED
        self.page.update()
        self.__findReplaceHistory.Save()


    def __find_replace_info(self, e):
        if self.__findreplace_info.max_lines == 1:
            self.__findreplace_info.max_lines = 10
            e.control.text = "Less info"
        elif self.__findreplace_info.max_lines == 10:
            self.__findreplace_info.max_lines = 1
            e.control.text = "More info"
        self.__findreplace_info.update()
        e.control.update()

    def __spl_replace_both(self, _):
        if isinstance(self.__questionContainer.content,ft.TextField):
            questionText : str = self.__fixTextForHTML(self.__questionContainer.content.value)
            newQuestionText = questionText
            for k,v in self.__listings.FindReplaceListing.items():
                newQuestionText = resub(k,v,newQuestionText)
            newQuestionText = self.__clean_clipboard_text(newQuestionText)
            if newQuestionText != questionText:
                self.__questionContainer.content.value = newQuestionText
                self.__questionContainer.update()
        for i, ctrl in enumerate(self.__choices.controls):
            if type(ctrl) == ft.Checkbox:
                choiceContainer : ft.Container = self.__choices.controls[i + 1]
                if isinstance(choiceContainer.content,ft.TextField):
                    choiceText : str = choiceContainer.content.value
                    newChoiceText = choiceText
                    for k,v in self.__listings.FindReplaceListing.items():
                        newChoiceText = resub(k,v,newChoiceText)
                    newChoiceText = self.__clean_clipboard_text(newChoiceText)
                    if newChoiceText != choiceText:
                        choiceContainer.content.value = newChoiceText
                        choiceContainer.update()

    def __replace_in_question(self, e):
        self.__findreplace_info.value = None
        self.__findreplace_info.update()
        if e.control.data == ReplaceWhat.CLOSEDIALOG:
            self.__close_replace_dialog()
        else:
            try:
                replace_what = self.__find_textbox.value
                replace_with_what = self.__replace_textbox.value
                ans_update_msg : str = None
                choices_changed : dict = {}
                # msg_type : MsgType = None
                if e.control.data == ReplaceWhat.QUESTIONONLY or e.control.data == ReplaceWhat.BOTH:
                    if isinstance(self.__questionContainer.content,ft.TextField):
                        questionText : str = self.__fixTextForHTML(self.__questionContainer.content.value)
                        newQuestionText = resub(replace_what,replace_with_what,questionText)
                        if newQuestionText != questionText:
                            self.__questionContainer.content.value = newQuestionText
                            self.__questionContainer.update()
                            ans_update_msg = f"For Question - Replaced: \"{questionText}\" with \n\"{self.__questionContainer.content.value}\""
                if  e.control.data == ReplaceWhat.CHOICESONLY or e.control.data == ReplaceWhat.BOTH:
                    for i, ctrl in enumerate(self.__choices.controls):
                        if type(ctrl) == ft.Checkbox:
                            choiceContainer : ft.Container = self.__choices.controls[i + 1]
                            if isinstance(choiceContainer.content,ft.TextField):
                                choiceText : str = choiceContainer.content.value
                                newChoiceText = resub(replace_what,replace_with_what,choiceText)
                                if newChoiceText != choiceText:
                                    choiceContainer.content.value = newChoiceText
                                    choiceContainer.update()
                                    choices_changed[chr(int(i/2)+65)] = f"For choice {chr(int(i/2)+65)} - Replaced: \"{choiceText}\" with \"{choiceContainer.content.value}\""
                if ans_update_msg or choices_changed:
                    # we are only adding to history if the replace actually did something
                    self.__findReplaceHistory.addToFindHistory(replace_what)
                    self.__findReplaceHistory.addToReplaceHistory(replace_with_what)
                    
            except reerror as re_er:
                self.__findreplace_info_update(re_er.msg,MsgType.ERR)
            else:
                msgs = []
                if ans_update_msg or choices_changed:
                    if ans_update_msg:
                        msgs.append(ans_update_msg)
                    if choices_changed:
                        msgs.append("Choices changed: " + ";".join(choices_changed.keys()))
                        for choice, msg in choices_changed.items():
                            msgs.append(f"Choice changed: {choice} for {msg}")
                    self.__findreplace_info_update("\n".join(msgs), MsgType.INFO)
                else:
                    self.__findreplace_info_update("No changes made",MsgType.INFO)



    def __findreplace_info_update(self, upd_txt, msg_type : MsgType):
        self.__findreplace_info.value = upd_txt
        if msg_type == MsgType.ERR:
            self.__findreplace_info.color = ft.colors.RED
        elif msg_type == MsgType.WARN:
            self.__findreplace_info.color = ft.colors.ORANGE
        elif msg_type == MsgType.INFO:
            self.__findreplace_info.color = None
        self.__findreplace_info.update()

    def __choices_rearrange_info_update(self, upd_txt, msg_type : MsgType):
        self.__choices_rearrange_info.value = upd_txt
        if msg_type == MsgType.ERR:
            self.__choices_rearrange_info.color = ft.colors.RED
        elif msg_type == MsgType.WARN:
            self.__choices_rearrange_info.color = ft.colors.ORANGE
        elif msg_type == MsgType.INFO:
            self.__choices_rearrange_info.color = None
        
        self.__choices_rearrange_info.update()

    def __find_replace_textbox_focus(self, e):
        if e.control.data == "find_textbox":
            self.__from_text_infocus = True
        elif e.control.data == "replace_textbox":
            self.__replace_with_infocus = True

    def __find_replace_textbox_blur(self, e):
        self.__from_text_infocus = False
        self.__replace_with_infocus = False

    def __if_replace_dialog_closed(self, e):
        if e.key == 'S':
            self.__save_question_click(None)
        elif e.key == 'Enter':
            if self.__qanda_number_infocus:
                self.__set_qanda_info(True)
        elif e.key == 'H':
            self.__open_replace_dialog(None)
        elif e.key == 'N':
            self.__reset_question()
        elif e.key == 'O':
            self.__answer_not_required.value = not self.__answer_not_required.value
            self.__answer_not_required.update()
        elif e.key == 'T':
            self.__toggle_dropdowns(None)
        elif e.key == 'D':
            self.__is_advanced_q_checkbox.value = not self.__is_advanced_q_checkbox.value
            self.__is_advanced_q_checkbox.update()
        elif e.key == 'P':
            self.__add_choice(None)
        elif e.key == '-':
            self.__decrease_image_container_heights()
        elif e.key == '+':
            pass
            # for some reason Ctrl+ seems not to work?
            # self.__increase_image_container_heights()
        elif e.key == 'Q':
            self.__add_question(None)
        elif e.key == "W":
            self.__open_rearrange_choices_dialog(None)
        elif e.key in ['G','R']:
            url = getClipboardData()
            if url:
                if 'https://www.google.com/' in url:
                    self.__answer_url.value = url
                    self.__answer_url.update()
                    self.__qanda_number.focus()
                    if e.key == 'G':
                        self.__add_question_from_url(url)
                else:
                    self.OpenAlert("Google URL not found on clipboard")    
            else:
                self.OpenAlert("No URL found on clipboard")
        elif e.key in [str(x) for x in range(1,5)]:
            ctrlIndex = 2*int(e.key) - 2
            if len(self.__choices.controls) >= ctrlIndex:
                self.__choices.controls[ctrlIndex].value = not self.__choices.controls[ctrlIndex].value
                self.__choices.controls[ctrlIndex].update()


    def __if_replace_dialog_open(self, e):
        if e.key == "L":
            self.__close_replace_dialog()
        elif e.key == "Arrow Down":
            if self.__from_text_infocus:
                self.__find_textbox.value = self.__findReplaceHistory.nextInSplFindHistory
                self.__find_textbox.update()
            elif self.__replace_with_infocus:
                self.__replace_textbox.value = self.__findReplaceHistory.nextInSplReplaceHistory
                self.__replace_textbox.update()
        elif e.key == "Arrow Up":
            if self.__from_text_infocus:
                self.__find_textbox.value = self.__findReplaceHistory.PrevInSplFindHistory
                self.__find_textbox.update()
            elif self.__replace_with_infocus:
                self.__replace_textbox.value = self.__findReplaceHistory.prevInSplReplaceHistory
                self.__replace_textbox.update()
        

    def __on_keyboard(self, e: ft.KeyboardEvent):
        if e.ctrl:
            if self.__replace_dialog_state == ReplaceDialogState.ISCLOSED:
                self.__if_replace_dialog_closed(e)
            elif self.__replace_dialog_state == ReplaceDialogState.ISOPEN:
                self.__if_replace_dialog_open(e)
        elif e.alt:
            if self.__replace_dialog_state == ReplaceDialogState.ISCLOSED:
                if e.key == 'Arrow Right':
                    self.__show_recent_question(QuestionDirection.Next)
                elif e.key == 'Arrow Left':
                    self.__show_recent_question(QuestionDirection.Previous)
        else:
            if self.__from_text_infocus:
                if e.key == "Arrow Down":
                    self.__find_textbox.value = self.__findReplaceHistory.nextInFindHistory
                    self.__find_textbox.update()
                elif e.key == "Arrow Up":
                    self.__find_textbox.value = self.__findReplaceHistory.PrevInFindHistory
                    self.__find_textbox.update()
                elif e.key == "Escape":
                    self.__find_textbox.value = None
                    self.__find_textbox.update()
            elif self.__replace_with_infocus:
                if e.key == "Arrow Up":
                    self.__replace_textbox.value = self.__findReplaceHistory.nextInReplaceHistory
                    self.__replace_textbox.update()
                elif e.key == "Arrow Down":
                    self.__replace_textbox.value = self.__findReplaceHistory.prevInReplaceHistory
                    self.__replace_textbox.update()
                elif e.key == "Escape":
                    self.__replace_textbox.value = None
                    self.__replace_textbox.update()


    def __buildAppMenu(self):
        self.__menu.controls.append(self.__previous_question_button)
        self.__menu.controls.append(self.__next_question_button)
        self.__menu.controls.append(ft.ElevatedButton(text="+C(P)",on_click=self.__add_choice,tooltip="Add Choice from Image/Text"))
        self.__menu.controls.append(ft.ElevatedButton(text="+(Q)",on_click=self.__add_question,tooltip="Add Question from Image/Text"))
        self.__menu.controls.append(ft.ElevatedButton(text="+A",on_click=self.__add_answer,tooltip="Add Answer from Image"))
        self.__menu.controls.append(ft.ElevatedButton(text="(N)ew",on_click=self.__new_question,tooltip="Reset all of question"))
        self.__menu.controls.append(ft.ElevatedButton(text="Cs",on_click=self.__get_only_choices,tooltip="Get Choices from URL"))
        self.__menu.controls.append(ft.ElevatedButton(text="Q",on_click=self.__get_only_question,tooltip="Get Question from URL"))
        self.__menu.controls.append(ft.ElevatedButton(text="Q&Cs",on_click=self.__get_question_and_choices,tooltip="Get Question&Choices from URL"))
        self.__menu.controls.append(ft.ElevatedButton(text="(S)ave",on_click=self.__save_question_click,tooltip="Save question"))
        self.__menu.controls.append(ft.ElevatedButton(text="Cls Cs",on_click=self.__clear_choices,tooltip="Clear all Choices"))
        self.__menu.controls.append(ft.ElevatedButton(text="CCs",on_click=self.__copy_choices,tooltip="Copy all Choices to clipboard"))
        self.__menu.controls.append(ft.ElevatedButton(text="Toggle DDs",on_click=self.__toggle_dropdowns,key="show",tooltip="Toggle Drop-downs"))
        self.__menu.controls.append(ft.ElevatedButton(text="+Q",on_click=self.__add_question,tooltip="Add Question from Image"))
        self.__menu.controls.append(ft.ElevatedButton(text="Get from URL",on_click=self.__open_details_prompt,tooltip="Get All from URL"))

    def __show_previous_question(self, _):
        self.__show_recent_question(QuestionDirection.Previous)

    def __show_next_question(self, _):
        self.__show_recent_question(QuestionDirection.Next)
    
    def __show_recent_question(self, questionDirection : QuestionDirection):
        # Question offset
        # 1: Get last (most recently added) question
        # 2: Get 2nd last
        # 3: Get 3rd last, and so on
        if self.__selected_restapi_url:
            self.__wait_for_end()
            if questionDirection == QuestionDirection.Next:
                self.__recent_question_offset -= 1
                # for now what we're going to do is if the counter is less than 1, we're going to reset it to 1
                if self.__recent_question_offset < 1:
                    self.__recent_question_offset = 1
            elif questionDirection == QuestionDirection.Previous:
                self.__recent_question_offset += 1
            question = self.__restapi.getRecentQuestion(self.__selected_restapi_url,self.__recent_question_offset)
            if question['id'] == -1:
                self.OpenAlert("Currently previous questions")
                # let's also put the counter back
                if questionDirection == QuestionDirection.Next:
                    self.__recent_question_offset += 1
                elif questionDirection == QuestionDirection.Previous:
                    self.__recent_question_offset -= 1
            else:
                self.__reset_question()
                self.__selected_question_id = question['id']
                if question['description']:
                    self.__questionContainer.clean()
                    self.__questionContainer.content = ft.TextField(value=question['description'],multiline=True)
                else:
                    self.__questionContainer.content.src_base64 = question['filestr']

                if question['answer']['description']:
                    self.__answerContainer.clean()
                    self.__answerContainer.content = ft.TextField(value=question['answer']['description'],multiline=True)
                else:
                    self.__answerContainer.content.src_base64 = question['answer']['filestr']



                self.__questionIDTxt.value = f"{question['id']}/{question['topic_id']}"
                
                self.__is_advanced_q_checkbox.value = True if question['is_jee_advanced'] == '1' else False
                # self.__is_advanced_q_checkbox.value = True if question['is_jee_advanced'] == 1 else False
                self.__is_fitb_q_checkbox.value = True if question['questiontype']['name'] == "fitb" else False
                self.__answer_url.value = question['answer']["url"]
                self.__marks.value = question['marks']
                for choice in question['choices']:
                    self.__choices.controls.append(ft.Checkbox(label=chr(self.__choice_counter),value=True if choice['correct_ans']=="1" else False ))
                    choiceContainer : ft.Container = ft.Container(on_long_press=self.__choice_on_long_press)
                    self.__choice_counter += 1
                    if choice['description']:
                        choiceContainer.content = ft.TextField(value=choice['description'],width=150)
                    else:
                        choiceContainer.content = ft.Image(src_base64=choice['filestr'],fit=ft.ImageFit.FIT_HEIGHT,width=150)
                    self.__choices.controls.append(choiceContainer)
                self.update()
            self.__wait_for_end_over()        
        else:
            self.OpenAlert("You haven't selected an Environment to run in")

    def __reset_question(self):
        # re-init question
        self.__change_topic.visible = self.__change_topic.value = False
        # self.__change_topic.update()
        self.__change_source.visible = self.__change_source.value = False
        # self.__change_source.update()

        self.__choice_counter = 65 # which is A caps
        self.__selected_question_id = -1
        self.__questionIDTxt.value = self.__selected_question_id
        self.__is_advanced_q_checkbox.value = self.__is_fitb_q_checkbox.value = self.__is_mmcq_q_checkbox.value = self.__answer_not_required.value = False
        theApp.ClearClipboard()
        self.__questionContainer.content = ft.Image(src_base64=self.__restapi.QuestionPlacehoderImg,fit=ft.ImageFit.CONTAIN,width=self.__imageDim.Width,height=self.__imageDim.Height)
        self.__answerContainer.content = ft.Image(src_base64=self.__restapi.AnswerPlacehoderImg,fit=ft.ImageFit.CONTAIN,width=self.__imageDim.Width,height=self.__imageDim.Height)
        self.__choices.clean()
        self.__answer_url.value = ''
        self.__qanda_number.value = ''
        # self.__info_box_update(None, False)
        self.update()


    def __new_question(self, e):
        self.__reset_question()
 
    def __clear_choices(self, e):
        self.__choice_counter = 65
        self.__choices.clean()
        self.__choices.update()

    def __copy_choices(self, e):
        # IMPORTANT
        # We are going to "Copy" the choice text.
        # There is no reason to "Cut" the choice text, since client will use the Cls C and +C methods to replace the choices after whatever is done
        choices : list = list()
        for i in range(1,len(self.__choices.controls),2):
            choiceContainer : ft.Container = self.__choices.controls[i]
            if isinstance(choiceContainer.content,ft.TextField):
                choices.append(choiceContainer.content.value)
        try:
            if choices:
                setClipboardData("\n".join(choices))
                self.OpenAlert("Choices copied to clipboard")
            else:
                self.OpenAlert("No choices found")
        except UnicodeEncodeError as uee:
            self.OpenAlert(f"Some error copying choices:\n{uee}")

    def __toggle_dropdowns(self, _):
        allGood : bool = True
        if allGood:
            if self.__selected_restapi_url:
                allGood = True
            else:
                self.OpenAlert("You must select an Environment")
                allGood = False
        if allGood:
            if self.__selected_subject_id:
                allGood = True
            else:
                self.OpenAlert("You must select a Subject")
                allGood = False
        if allGood:
            if self.__selected_topic_id:
                allGood = True
            else:
                self.OpenAlert("You must select a Topic")
                allGood = False
        if allGood:
            if self.__selected_source_id:
                allGood = True
            else:
                self.OpenAlert("You must select a Source")
                allGood = False
            
        if allGood:
            if self.__dropdowns.visible:
                self.page.title += ' - Env: ' + [x for x in self.__environmentDropDown.options if x.key == self.__selected_restapi_url][0].text
                self.page.title += ' - Subject: ' + [x for x in self.__subjectDropDown.options if x.key == self.__selected_subject_id][0].text
                self.page.title += '; Topic: ' + [x for x in self.__topicDropDown.options if x.key == self.__selected_topic_id][0].text
                self.page.title += '; Source: ' + [x for x in self.__sourceDropDown.options if x.key == self.__selected_source_id][0].text
            else:
                self.page.title = "traPCM App"
            self.__dropdowns.visible ^= True
            self.__dropdowns.update()
            self.page.update()
    
    def __fixTextForHTML(self, textToFix : str):
        textToFix = textToFix.replace('"',"'")
        textToFix = textToFix.replace("\n", '<br>')
        retval = ''
        
        for i,y in enumerate(textToFix):
            if y == '<':
                for tag in self.__tags:
                    if textToFix[i:i+len(tag)] == tag or textToFix[i:i+len(tag)+1] == tag[0] + '/' + tag[1:len(tag)]:
                        retval += y
                        break
                else:
                    retval += '&lt;'
            elif y == '>':
                for tag in self.__tags:
                    if textToFix[i-(len(tag)-1):i+1] == tag or textToFix[i-len(tag):i+1] == tag[0] + '/' + tag[1:len(tag)]:
                        retval += y
                        break
                else:
                    retval += '&gt;'
            else:
                retval += y
        return retval

    def __save_question(self, question_type):
        allGood : bool = True
        if self.__selected_question_id != -1:   # question update
            existingQuestion =  self.__restapi.getQuestion(self.__selected_restapi_url,self.__selected_question_id)
            topicWasChanged = False
            sourceWasChanged = False
            if self.__change_topic.value == True:
                allGood = True
            else:
                if existingQuestion['topic_id'] != self.__selected_topic_id:
                    topicDetails  = self.__restapi.getTopicAndSubjectByTopicID(self.__selected_restapi_url,existingQuestion['topic_id'])
                    error_msg = "We can't save the existing question because:\n"
                    error_msg += f"The question is from topic: \"{topicDetails['topic']['title']}\". Which is different from the Topic drop-down.\n"
                    if topicDetails['subject']['id'] != self._theApp__selected_subject_id:
                        error_msg += f"Also, the subject is from \"{topicDetails['subject']['title']}\". Which is different from the Subject drop-down.\n"
                    topicWasChanged = True
                    allGood = False
            if self.__change_source.value == True:
                allGood = True
            else:
                if existingQuestion['q_src_id'] != self.__selected_source_id:
                    sourceWasChanged = True
                    selectSrcTitle = [x for x in self.__sourceDropDown.options if x.key == existingQuestion['q_src_id']][0].text
                    if not topicWasChanged:
                        error_msg = "\nWe can't save the existing question because:\n"
                    error_msg += f"The question is from source: \"{selectSrcTitle}\". Which is different from the Source drop-down.\n"
                    allGood = False
            if not allGood:
                error_msg += "You will need to make the correct drop-down selections before saving this question.\nOR:"
                if topicWasChanged:
                    error_msg += "\nYou'll need to check Change topic"
                    self.__change_topic.visible = True
                    self.__change_topic.update()
                if sourceWasChanged:
                    error_msg += "\nYou'll need to check Change source"
                    self.__change_source.visible = True
                    self.__change_source.update()
                self.OpenAlert(error_msg)
        if allGood:
            self.__wait_for_end()
            questionData : dict = dict()
            questionData["id"] = self.__selected_question_id;
            questionData['choices'] = list()
            for i, ctrl in enumerate(self.__choices.controls):
                if type(ctrl) == ft.Checkbox:
                    choice : dict = dict()
                    choice['iscorrect'] = 1 if ctrl.value else 0
                    choiceContainer : ft.Container = self.__choices.controls[i + 1]
                    if isinstance(choiceContainer.content,ft.TextField):
                        choice["description"] = self.__fixTextForHTML(choiceContainer.content.value)
                    elif isinstance(choiceContainer.content,ft.Image):
                        choice["imageStr"] = choiceContainer.content.src_base64
                    questionData['choices'].append(choice)
            questionData["topicID"] = self.__selected_topic_id
            questionData["advanced"] = '1' if self.__is_advanced_q_checkbox.value == True else '0'
            questionData["questionTypeID"] = question_type.value
            questionData['marks'] = self.__marks.value if 'cbse' in self.__selected_restapi_url else 4
            if isinstance(self.__questionContainer.content,ft.TextField):
                questionText : str = self.__fixTextForHTML(self.__questionContainer.content.value)
                questionData["description"] = questionText
            elif isinstance(self.__questionContainer.content,ft.Image):
                questionData["imageStr"] = self.__questionContainer.content.src_base64
            if isinstance(self.__answerContainer.content,ft.TextField):
                questionData["answerdescription"] = str(self.__answerContainer.content.value)
            elif isinstance(self.__answerContainer.content,ft.Image):
                if self.__answerContainer.content.src_base64 == self.__restapi.AnswerPlacehoderImg:
                    questionData["answerImageStr"] = self.__restapi.NoAnswerAvailableImg
                else:
                    questionData["answerImageStr"] = self.__answerContainer.content.src_base64
            questionData["answerURL"] = self.__answer_url.value
            questionData['source'] = self.__selected_source_id
            questionID = self.__restapi.saveQuestion(questionDict=questionData, question_id=self.__selected_question_id, restapiurl=self.__selected_restapi_url)
            self.__wait_for_end_over()
            if questionID == self.__selected_question_id:
                self.__info_box_update(f"Updated Question ID: {questionID}",False)
            else:
                self.__info_box_update(f"New Question ID: {questionID}",False)
            self.__reset_question()

    # check that at least one choice is selected as correct

    def __check_multiple_choice(self):
        choice_counter = 0
        for i, ctrl in enumerate(self.__choices.controls):
            if type(ctrl) == ft.Checkbox:
                if ctrl.value:
                    choice_counter += 1
        if choice_counter > 1 or self.__is_mmcq_q_checkbox.value == True:
            return self.QuestionType.mmcq
        else:
            if choice_counter == 1:
                return self.QuestionType.mcq
            else:
                return False

    def __save_question_click(self, _):
        # we need a lot of validation here
        # one thing we do need is this:
        # instead of requiring selection of question type, we can do this:
        # if there are choices, this has to be MCQ
        # if there are no choices, prompt saying "there are no chioices", should we save as long form
        allGood : bool = False
        if self.__selected_restapi_url:
            allGood = True
        else:
            self.OpenAlert("You haven't selected an Environment to run in")
            allGood = False
        if allGood:
            if self.__selected_subject_id:
                allGood = True
            else:
                self.OpenAlert("You haven't selected a Subject")
                allGood = False
        if allGood:
            if self.__selected_topic_id:
                allGood = True
            else:
                self.OpenAlert("You haven't selected a Topic")
                allGood = False
        if allGood:
            if self.__selected_source_id:
                allGood = True
            else:
                self.OpenAlert("You haven't selected a Question Source")
                allGood = False
        if allGood:
            if isinstance(self.__questionContainer.content,ft.TextField):
                if self.__questionContainer.content.value != "" and self.__questionContainer.content.value is not None:
                    allGood = True
            elif isinstance(self.__questionContainer.content,ft.Image):
                if self.__questionContainer.content.src_base64 != self.__restapi.QuestionPlacehoderImg:
                    allGood = True
                else:
                    self.OpenAlert("You haven't added a question")
                    allGood = False
        if allGood:
            if self.__answer_not_required.value == False:
                if isinstance(self.__answerContainer.content,ft.TextField):
                    if self.__answerContainer.content.value != "" and self.__answerContainer.content.value is not None:
                        allGood = True
                elif isinstance(self.__answerContainer.content,ft.Image):
                    if self.__answerContainer.content.src_base64 != self.__restapi.AnswerPlacehoderImg:
                        allGood = True
                    else:
                        self.OpenAlert("You haven't added an answer.\nIf you don't want to add and answer, check Ans Not Req.")
                        allGood = False
        if allGood:
            if self.__answer_url.value.strip():
                googleDomain : str = 'https://www.google.com/'
                if self.__answer_url.value[:len(googleDomain)] != googleDomain:
                    self.OpenAlert("Your answer URL doesn't seem to be a google search URL.")
                    allGood = False
                else:
                    if len(findall(googleDomain, self.__answer_url.value)) != 1:
                        self.OpenAlert("Your answer URL seems to have multiple google domain names.\nDid you accidentally paste the google URL multiple times?")
                        allGood = False
            else:
                self.OpenAlert("You haven't entered a google search URL")
                allGood = False
        if allGood:
            if self.__marks.visible:
                try:
                    if int(self.__marks.value) not in range(1,11):
                            self.OpenAlert("Marks must be with the range 1 - 10")
                            allGood = False
                except Exception as _:
                    self.OpenAlert("Marks must be with the range 1 - 10")
                    allGood = False
        if allGood:
            if len(self.__choices.controls) == 0:
                # prompt to save as long-form
                self.__open_yesnoprompt()
            elif len(self.__choices.controls) == 2:
                # save as fitb
                self.__save_question(self.QuestionType.fitb)
            else:
                choice_check = self.__check_multiple_choice()
                if not choice_check:
                    self.OpenAlert("You haven't selected any choices as correct. Please select at least one.")
                else:
                    self.__save_question(choice_check)

    def __qanda_number_gotfocus(self, _):
        self.__qanda_number_infocus = True

    def __qanda_number_lostfocus(self, _):
        self.__qanda_number_infocus = False

    def __marks_lostfocus(self, e):
        try:
            if int(e.control.value) not in range(1,11):
                    self.OpenAlert("Marks must be with the range 1 - 10")
        except Exception as _:
            self.OpenAlert("Marks must be with the range 1 - 10")

    def __set_qanda_info(self,overwrite_question_text=False):
        if self.__correctAnwers.getCorrectOptionByQuestion(self.__qanda_number.value, chr(self.__choice_counter)):
            self.__info_box_update("Correct options: " + "; ".join(self.__correctAnwers.getCorrectOptionNames(self.__qanda_number.value)),False)
        qanda_file_path = f"{self.__restapi.QandAFilesRoot}/{self.__questionData.SourceTitle.lower()}/{self.__questionData.SubjectTitle.lower()}/{self.__qanda_folder_number.value}"
        ans_file_location = f"{qanda_file_path}/answer-files/topic{self.__qanda_topic_number.value}/{self.__qanda_number.value}.png"
        ques_file_location = f"{qanda_file_path}/question-files/topic{self.__qanda_topic_number.value}/{self.__qanda_number.value}.png"
        if isfile(ans_file_location):
            self.__answerContainer.content.src_base64 = theApp.getImageString(ans_file_location)
            self.__answerContainer.update()
        else:
            self.__info_box_update(f"Answer File not found at: {self.__qanda_number.value}.png")
        if isfile(ques_file_location):
            if isinstance(self.__questionContainer.content,ft.TextField):
                if overwrite_question_text:
                    self.__questionContainer.clean()
                    self.__questionContainer.content = ft.Image(src_base64=theApp.getImageString(ques_file_location),
                                                                fit=ft.ImageFit.CONTAIN,width=self.__imageDim.Width,
                                                                height=self.__imageDim.Height)
            else:
                self.__questionContainer.clean()
                self.__questionContainer.content = ft.Image(src_base64=theApp.getImageString(ques_file_location),
                                                            fit=ft.ImageFit.CONTAIN,width=self.__imageDim.Width,
                                                            height=self.__imageDim.Height)
            self.__questionContainer.update()
            self.__answer_url.focus()
        else:
            self.__info_box_update(f"Question File not found at: {self.__qanda_number.value}.png")

    def __get_qanda_image(self, e):
        self.__set_qanda_info()

    def __env_select(self, e):
        # clear out subject and topic lists and selected values
        self.__subjectDropDown.clean()
        self.__topicDropDown.clean()
        self.__sourceDropDown.clean()
        self.__reset_question()
        self.__selected_subject_id = None
        self.__selected_topic_id = None
        
        self.__selected_restapi_url = e.control.value
        self.__marks.visible = 'cbse' in self.__selected_restapi_url
        self.__marks.update()
        try:
            self.__wait_for_end()
            self.__subjectsandtopics = self.__restapi.getSubjectsAndTopics(self.__selected_restapi_url)
            self.__buildSubjectDropDown()
            # also let's get the question types for the selected env
            self.QuestionType = Enum('QuestionType', self.__restapi.getQuestionTypes(self.__selected_restapi_url))
            self.__buildSourcesDropDown()
        except:
            self.OpenAlert("Couldn't hit this server")
        finally:
            self.__wait_for_end_over()

    def __subject_select(self, e):
        self.__selected_subject_id = e.control.value
        for opt in e.control.options:
            if opt.key == e.control.value:
                self.__questionData.SubjectTitle = opt.text
                self.__buildTopicDropDown()
                
                break        

    def __topic_select(self, e):
        self.__selected_topic_id = e.control.value
        for opt in e.control.options:
            if opt.key == e.control.value:
                self.__questionData.TopicTitle = opt.text
                break        
        for subject in self.__subjectsandtopics:
            if subject['id'] == self.__selected_subject_id:
                for topic in subject['topics']:
                    if topic['id'] == self.__selected_topic_id:
                        if topic['test_name'] == 'jee':
                            self.__is_advanced_q_checkbox.visible = True
                            self.__is_advanced_q_checkbox.update()
                        elif topic['test_name'] == 'cbse':
                            self.__is_advanced_q_checkbox.visible = False
                            self.__is_advanced_q_checkbox.update()
                        else:
                            raise Exception(f"Topic: {self.__selected_topic_id} seems not to have a test_name - JEE or CBSE")


    def __source_select(self, e):
        for opt in e.control.options:
            if opt.key == e.control.value:
                self.__questionData.SourceTitle = opt.text
                break        
        self.__selected_source_id = e.control.value

    # obsolete

    def __add_answer(self, _):
        try:
            if self.__qanda_number:
                txt : str = getClipboardData()
                somethingFound = False
                if txt is not None:
                    txt = self.__clean_clipboard_text(txt)
                    self.__answerContainer.clean()
                    self.__answerContainer.content = ft.TextField(value=txt,multiline=True)
                    somethingFound = True
                else:
                    self.__imgToSave = ImageGrab.grabclipboard()
                    if self.__imgToSave is not None:
                        self.__answerContainer.clean()
                        self.__answerContainer.content = ft.Image(src_base64=theApp.getImageString(self.__imgToSave),
                                                                    fit=ft.ImageFit.CONTAIN,width=self.__imageDim.Width,
                                                                    height=self.__imageDim.Height)
                        somethingFound = True
                if somethingFound:
                    self.update()
                    theApp.ClearClipboard()
                else:
                    self.OpenAlert("Nothing for answer found on clipboard.")
            else:
                self.OpenAlert("Please add a QAndA number first")
                self.__qanda_number.focus()
        except OSError  as osex:
            self.OpenAlert("Error with clipboard")
            
    def obsolete__add_answer(self, _):
        try:
            self.__imgToSave = ImageGrab.grabclipboard()
            if self.__imgToSave is not None:
                self.__answerContainer.content.src_base64 = theApp.getImageString(self.__imgToSave)
                self.__answerContainer.update()
                theApp.ClearClipboard()
            else:
                self.OpenAlert("No Answer image found on clipboard.")
        except OSError  as osex:
            self.OpenAlert("Error with clipboard")


    
    def __add_from_url(self, e):
        if AddFromUrl.Question in e.control.data:
            self.__questionContainer.clean()
            self.__questionContainer.content = ft.TextField(value=getTextFromSoup(self.__qc.question),multiline=True)
            self.__questionContainer.update()
        if AddFromUrl.Answer in e.control.data:
            self.__answerContainer.clean()
            self.__answerContainer.content = ft.TextField(value=getTextFromSoup(self.__qc.solution))
            self.__answerContainer.update()
        if AddFromUrl.Choices in e.control.data:
            self.__choices.controls.clear()
            self.__choice_counter = 65
            for choice,is_right in self.__qc.choices.items():
                self.__choices.controls.append(ft.Checkbox(label=chr(self.__choice_counter),value=is_right))
                self.__choice_counter += 1
                choiceContainer : ft.Container = ft.Container(
                    content=ft.TextField(value=getTextFromSoup(choice)),
                    on_long_press=self.__choice_on_long_press,
                    width=120,
                )
                self.__choices.controls.append(choiceContainer)
        self.update()
        theApp.ClearClipboard()

        self.__add_from_url_prompt.open = False
        self.page.update()

    def __append_image(self, e):
        try:
            fromClipboard = ImageGrab.grabclipboard()
            if fromClipboard:
                folderToSave : str = f"{self.__restapi.QandAFilesRoot}/"
                # first save the current image to disc
                if isinstance(self.__imgToSave, list):
                    self.__imgToSave[0].save(f'{folderToSave}tmp1.png')
                else:
                    self.__imgToSave.save(f'{folderToSave}tmp1.png')
                # then save the clipboard image (to be appended)
                fromClipboard.save(f'{folderToSave}tmp2.png')
                # we are using another lib (cv2), so we need to read these back
                merged_img = theApp.resize_on_vertical([cv2.imread(f'{folderToSave}tmp1.png'),
                                                        cv2.imread(f'{folderToSave}tmp2.png')])
                # we will have to write this back to disc
                cv2.imwrite(f'{folderToSave}tmp-final.png', merged_img)
                self.__imgToSave = Image.open(f'{folderToSave}tmp-final.png')
                if e.control.key == "appendtoanswer":
                    self.__answerContainer.content.src_base64 = theApp.getImageString(self.__imgToSave)
                    self.__answerContainer.update()
                elif e.control.key == "appendtoquestion":
                    self.__questionContainer.content.src_base64 = theApp.getImageString(self.__imgToSave)
                    self.__questionContainer.update()
                theApp.ClearClipboard()
            else:
                self.OpenAlert("No image found on clipboard.")
        except OSError  as osex:
            self.OpenAlert("Error with clipboard")


    def __undo_append_image(self, e):
        self.__imgToSave = Image.open(f'{self.__restapi.QandAFilesRoot}/tmp1.png')
        if e.control.key == "undoappendtoanswer":
            self.__answerContainer.content.src_base64 = theApp.getImageString(self.__imgToSave)
            self.__answerContainer.update()
        elif e.control.key == "undoappendtoquestion":
            self.__questionContainer.content.src_base64 = theApp.getImageString(self.__imgToSave)
            self.__questionContainer.update()


    def __wait_for_end(self):
        self.__waitSignal.visible = True
        self.__waitSignal.update()
        self.__menu.visible = self.__questionRow.visible = self.__questionContainer.visible = self.__choices.visible = self.__answerContainer.visible = False
        self.__menu.update()
        self.__questionRow.update()
        self.__questionContainer.update()
        self.__choices.update()
        self.__answerContainer.update()


    
    def __wait_for_end_over(self):
        self.__waitSignal.visible = False
        self.__waitSignal.update()
        self.__menu.visible = self.__questionRow.visible = self.__questionContainer.visible = self.__choices.visible = self.__answerContainer.visible = True
        self.__menu.update()
        self.__questionRow.update()
        self.__questionContainer.update()
        self.__choices.update()
        self.__answerContainer.update()
        beeper(2,1000,100)


    def __get_question_and_choices(self, _):
        try:
            url = getClipboardData()
            if url:
                self.__wait_for_end()
                self.__qc = getQandC(url)
                if self.__qc:
                    self.__questionContainer.clean()
                    self.__questionContainer.content = ft.TextField(value=getTextFromSoup(self.__qc.question),multiline=True)
                    self.__questionContainer.update()
                    if len(self.__qc.choices.items()) > 0:
                        self.__choices.controls.clear()
                        self.__choice_counter = 65
                        for choice,is_right in self.__qc.choices.items():
                            self.__choices.controls.append(ft.Checkbox(label=chr(self.__choice_counter),value=is_right))
                            self.__choice_counter += 1
                            choiceContainer : ft.Container = ft.Container(
                                content=ft.TextField(value=getTextFromSoup(choice),tooltip=getTextFromSoup(choice)),
                                on_long_press=self.__choice_on_long_press,
                                width=120,
                            )
                            self.__choices.controls.append(choiceContainer)
                        self.__choices.update()
                    else:
                        self.OpenAlert(f"Doesn't seem to be any choices")
                else:
                    self.OpenAlert(f"Doesn't seem to be a supported URL\n{url}")
            else:
                self.OpenAlert("Nothing found on clipboard")
        except Exception as ex:
            self.OpenAlert(ex)
        finally:
            self.__wait_for_end_over()

    def __get_only_choices(self, e):
        try:
            url = getClipboardData()
            if url:
                self.__wait_for_end()
                self.__qc = getQandC(url)
                if self.__qc:
                    if len(self.__qc.choices.items()) > 0:
                        self.__choices.controls.clear()
                        self.__choice_counter = 65
                        for choice,is_right in self.__qc.choices.items():
                            self.__choices.controls.append(ft.Checkbox(label=chr(self.__choice_counter),value=is_right))
                            self.__choice_counter += 1
                            choiceContainer : ft.Container = ft.Container(content=ft.TextField(value=getTextFromSoup(choice)),
                                                on_long_press=self.__choice_on_long_press,width=120,tooltip=getTextFromSoup(choice))
                            self.__choices.controls.append(choiceContainer)
                        # self.update()
                        self.__choices.update()
                    else:
                        self.OpenAlert(f"Doesn't seem to be any choices")
                else:
                    self.OpenAlert(f"Doesn't seem to be a supported URL\n{url}")
                # self.__wait_for_end_over()
            else:
                self.OpenAlert("Nothing found on clipboard")
        except Exception as ex:
            self.OpenAlert(ex)
        finally:
            self.__wait_for_end_over()

    def __get_only_question(self, e):
        try:
            url = getClipboardData()
            if url:
                self.__wait_for_end()
                self.__qc = getQandC(url)
                if self.__qc:
                    self.__questionContainer.clean()
                    self.__questionContainer.content = ft.TextField(value=getTextFromSoup(self.__qc.question),multiline=True)
                    self.__questionContainer.update()
                else:
                    self.OpenAlert(f"Doesn't seem to be a supported URL\n{url}")
                # self.__wait_for_end_over()
            else:
                self.OpenAlert("Nothing found on clipboard")
        except Exception as ex:
            self.OpenAlert(ex)
        finally:
            self.__wait_for_end_over()

        
        
        

    def __close_details_prompt(self, e):
        self.__add_from_url_prompt.open = False
        self.page.update()      

    def __open_details_prompt(self, e):
        url = getClipboardData()
        if url:
            self.__qc = getQandC(url)
            if self.__qc:
                promptText : str = "Question: " + getTextFromSoup(self.__qc.question)
                promptText += "\nAnswer: " + getTextFromSoup(self.__qc.solution)
                for choice,is_right in self.__qc.choices.items():
                    if is_right:
                        promptText += f"\n(Correct) {getTextFromSoup(choice)}"
                    else:
                        promptText += f"\n{getTextFromSoup(choice)}"
                self.__add_from_url_prompt.content.value = promptText
                # if there aren't any choices, then hide all "choice" buttons
                for action in [x for x in self.__add_from_url_prompt.actions if x.key == "choices"]:
                    action.visible = len(self.__qc.choices.items()) > 0
                self.__add_from_url_prompt.open = True
                self.page.dialog = self.__add_from_url_prompt
                self.page.update()
            else:
                self.OpenAlert(f"Doesn't seem to be a supported URL\n{url}")
        else:
            self.OpenAlert("Nothing found on clipboard")


    def __choice_on_long_press(self, e):
        try:
            img = ImageGrab.grabclipboard()
            if img is not None:
                e.control.content=ft.Image(src_base64=theApp.getImageString(img),fit=ft.ImageFit.FIT_HEIGHT,width=150)
                e.control.update()
                theApp.ClearClipboard()
        except OSError  as osex:
            self.OpenAlert("Error with clipboard")

    def __add_question_from_url(self, g_url : str):
        m = research('search\?q=(.+?)&rlz', g_url)
        txt = unquote(m.groups()[0]).replace('+',' ')
        txt = self.__clean_clipboard_text(txt)
        self.__questionContainer.clean()
        self.__questionContainer.content = ft.TextField(value=txt,multiline=True)
        self.update()

    def __clean_clipboard_text(self, txt : str):
        for f, r in self.__listings.CleanTextListing.items():
            txt = txt.replace(f,r)
        txt = txt.replace('\x00', '')
        # txt = txt.replace('\uf0d7','.').replace('\uf03c', '<').replace('\uf0be\uf0ae','&rarr;').replace('\uf070', '&pi;')
        # txt = txt.replace('\uf02b','+').replace('\uf02d','-').replace('\uf03d', '=')
        # txt = txt.replace('\uf044','&Delta;')
        txt = resub(r'\s+(\)|\])',r'\1',txt)
        return txt

    def __add_question(self, _):
        try:
            if self.__qanda_number:
                txt : str = getClipboardData()
                somethingFound = False
                if txt is not None:
                    txt = self.__clean_clipboard_text(txt)
                    self.__questionContainer.clean()
                    self.__questionContainer.content = ft.TextField(value=txt,multiline=True)
                    somethingFound = True
                else:
                    self.__imgToSave = ImageGrab.grabclipboard()
                    if self.__imgToSave is not None:
                        self.__questionContainer.clean()
                        self.__questionContainer.content = ft.Image(src_base64=theApp.getImageString(self.__imgToSave),
                                                                    fit=ft.ImageFit.CONTAIN,width=self.__imageDim.Width,
                                                                    height=self.__imageDim.Height)
                        somethingFound = True
                if somethingFound:
                    self.update()
                    theApp.ClearClipboard()
                else:
                    self.OpenAlert("Nothing for question found on clipboard.")
            else:
                self.OpenAlert("Please add a QAndA number first")
                self.__qanda_number.focus()
            
        
        except OSError  as osex:
            self.OpenAlert("Error with clipboard")


    def __add_choice(self, _):
        if self.__is_fitb_q_checkbox.value:
            if len(self.__choices.controls) == 0:
                self.__choices.controls.append(ft.Checkbox(label=chr(self.__choice_counter),value=True))
                self.__choices.controls.append(ft.Container(content=ft.TextField(value=''),on_long_press=self.__choice_on_long_press,width=120))
                self.update()
            else:
                self.OpenAlert("For FITB questions, you can only add a single option.\nIf this is an MCQ, uncheck 'Is FITB'")
        else:
            try:
                txt : str = getClipboardData()
                somethingFound = False
                isTopicSet = self.__correctAnwers != None
                if txt is not None:
                    if isTopicSet:
                        txtParts = [t.strip() for t in resplit('\([A-Da-d]\)',txt) if t.strip() != '']
                        if len(txtParts) == 1:
                            txtParts = [t.strip() for t in resplit('\n',txt) if t.strip() != '']
                        self.__funny_val_choice.HasFunnyChoice = False
                        for txtPart in [resub(r'^\(.\)\s+', '', x) for x in txtParts]:  # removing the (a-d) from the front
                            txtPart = self.__clean_clipboard_text(txtPart)
                            m = research('^(.+?)\s*\(\d{4}.+?\)$',txtPart)
                            if m:
                                self.__funny_val_choice.HasFunnyChoice = True
                                self.__funny_val_choice.Number = 2*(self.__choice_counter - 65)+1
                                self.__funny_val_choice.BadValue = txtPart
                                self.__funny_val_choice.GoodValue = m.groups()[0]
                            check_value : bool = self.__correctAnwers.getCorrectOptionByQuestion(self.__qanda_number.value, chr(self.__choice_counter))
                            if check_value:
                                setClipboardData(f"({chr(self.__choice_counter)}) {txtPart}")
                                self.__add_answer(None)
                            self.__choices.controls.append(ft.Checkbox(label=chr(self.__choice_counter),value=check_value))
                            self.__choice_counter += 1
                            choiceContainer : ft.Container = ft.Container(content=ft.TextField(value=txtPart,width=120,tooltip=txtPart),
                                                                        on_long_press=self.__choice_on_long_press)
                            self.__choices.controls.append(choiceContainer)
                            somethingFound = True
                    else:
                        self.OpenAlert("You haven't set the topic number")
                else:
                    img = ImageGrab.grabclipboard()
                    if img is not None:
                        check_value : bool = self.__correctAnwers.getCorrectOptionByQuestion(self.__qanda_number.value, chr(self.__choice_counter))
                        self.__choices.controls.append(ft.Checkbox(label=chr(self.__choice_counter),value=check_value))
                        self.__choice_counter += 1
                        choiceContainer : ft.Container = ft.Container(content=ft.Image(src_base64=theApp.getImageString(img),fit=ft.ImageFit.FIT_HEIGHT,width=150),
                                                                      on_long_press=self.__choice_on_long_press)
                        self.__choices.controls.append(choiceContainer)
                        somethingFound = True
                if isTopicSet:
                    if somethingFound:
                        self.update()
                        theApp.ClearClipboard()
                        if self.__funny_val_choice.HasFunnyChoice:
                            prompt : str = "We found a funny value in choice: " + chr(self.__funny_val_choice.Number+65) + "\n"
                            prompt += self.__funny_val_choice.BadValue + "\n"
                            prompt += "Do you want to replace it with: " + self.__funny_val_choice.GoodValue + "?"
                            self.__funnyvalueprompt.content.value = prompt
                            self.page.dialog = self.__funnyvalueprompt
                            self.__funnyvalueprompt.open = True
                            self.page.update()
                        
                    else:
                        self.OpenAlert(f"Nothing for choice \"{chr(self.__choice_counter)}\" found on clipboard.")
            except OSError  as osex:
                self.OpenAlert("Error with clipboard")



    def build(self):
        # application's root control (i.e. "view") containing all other controls
        textFieldRow : ft.Row = ft.Row([self.__qanda_folder_number,self.__qanda_topic_number,self.__qanda_number,self.__answer_url,self.__marks])
        appendQuestionOptionsRow : ft.Row = ft.Row([ft.ElevatedButton(text="Append to Question",on_click=self.__append_image,key="appendtoquestion"),
                                                     ft.ElevatedButton(text="Undo Append",on_click=self.__undo_append_image,key="undoappendtoquestion")])
        questionImageColumn : ft.Column = ft.Column([appendQuestionOptionsRow,self.__questionContainer])
        appendAnswerOptionsRow : ft.Row = ft.Row([ft.ElevatedButton(text="Append to answer",on_click=self.__append_image,key="appendtoanswer"),
                                                     ft.ElevatedButton(text="Undo Append",on_click=self.__undo_append_image,key="undoappendtoanswer")])

        answerImageColumn : ft.Column = ft.Column([appendAnswerOptionsRow,self.__answerContainer])
        qandaRow : ft.Row = ft.Row([questionImageColumn,answerImageColumn])

        return ft.Column(controls=[self.__waitSignal,self.__dropdowns,
                                   self.__menu,self.__questionRow,
                                   textFieldRow,self.__InfoBox,qandaRow,self.__choices])


    @staticmethod
    def ClearClipboard():
        if windll.user32.OpenClipboard(None):
            windll.user32.EmptyClipboard()
            windll.user32.CloseClipboard()

    @staticmethod
    def getImageString(imageValue):
        if isinstance(imageValue, list):
            with open(imageValue[0], 'rb') as f:
                return base64.b64encode(f.read()).decode("utf-8")
        elif isinstance(imageValue, BmpImagePlugin.BmpImageFile):
            buff = BytesIO()
            imageValue.save(buff, format="PNG")
            return base64.b64encode(buff.getvalue()).decode("utf-8")
        elif isinstance(imageValue, PngImagePlugin.PngImageFile):
            buff = BytesIO()
            imageValue.save(buff, format="PNG")
            return base64.b64encode(buff.getvalue()).decode("utf-8")
        elif isfile(imageValue):
                with open(imageValue, 'rb') as f:
                    return base64.b64encode(f.read()).decode("utf-8")

    @staticmethod
    def resize_on_vertical(img_list, interpolation  
                    = cv2.INTER_CUBIC): 
        # take maximum width 
        w_min = max(img.shape[1]
                    for img in img_list) 
        
        # resizing images 
        im_list_resize = [cv2.resize(img, 
                        (w_min, int(img.shape[0] * w_min / img.shape[1])), 
                                    interpolation = interpolation) 
                        for img in img_list] 
        # return final image 
        return cv2.vconcat(im_list_resize)            



def main(page: ft.Page):
    page.title = "traPCM App"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add(theApp(page))

ft.app(target=main)