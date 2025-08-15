from typing import Any, List, Optional, Union
import flet as ft
from flet_core.control import Control, OptionalNumber
from flet_core.ref import Ref
from flet_core.types import AnimationValue, ClipBehavior, OffsetValue, ResponsiveNumber, RotateValue, ScaleValue
from ctypes import windll
from PIL import ImageGrab
import os
import base64
from io import BytesIO
from enum import Enum

from libs.restapi import RestApi
from libs.clipboardtext import getClipboardData
from libs.getqandc import getQandC
from libs.souper import getTextFromSoup

class AddFromUrl(Enum):
    OnlyQuestion = 1
    OnlyChoices = 2
    BothQuestionAndChoices = 3

class QuestionDirection(Enum):
    Next = 1
    Previous = 2


class theApp(ft.UserControl):
    def __init__(self, controls = None, ref: Ref = None, key: str = None, width: OptionalNumber = None, height: OptionalNumber = None, left: OptionalNumber = None, top: OptionalNumber = None, right: OptionalNumber = None, bottom: OptionalNumber = None, expand: bool = None, col: ResponsiveNumber = None, opacity: OptionalNumber = None, rotate: RotateValue = None, scale: ScaleValue = None, offset: OffsetValue = None, aspect_ratio: OptionalNumber = None, animate_opacity: AnimationValue = None, animate_size: AnimationValue = None, animate_position: AnimationValue = None, animate_rotation: AnimationValue = None, animate_scale: AnimationValue = None, animate_offset: AnimationValue = None, on_animation_end=None, visible = None, disabled = None, data: Any = None, clip_behavior = None):
        super().__init__(controls, ref, key, width, height, left, top, right, bottom, expand, col, opacity, rotate, scale, offset, aspect_ratio, animate_opacity, animate_size, animate_position, animate_rotation, animate_scale, animate_offset, on_animation_end, visible, disabled, data, clip_behavior)

        self.__restapi = RestApi()

        self.__selected_restapi_url : str = None
        self.__selected_restapi_url : str = None
        self.__selected_subject_id : str = None
        self.__selected_topic_id : str = None
        self.__selected_question_id = -1
        self.__recent_question_offset = 0

        
        self.__choice_counter = 65 # which is A caps
        self.__questionIDTxt : ft.Text = ft.Text(self.__selected_question_id, size=10);
        self.__questionRow : ft.Row = ft.Row([self.__questionIDTxt,ft.ElevatedButton("DeleteQ",on_click=self.__delete_question)])
        

        self.__questionContainer : ft.Container = ft.Container(
                        content=ft.Image(src_base64=self.__restapi.QuestionPlacehoderImg,
                                         fit=ft.ImageFit.FIT_HEIGHT, width=350),
                                         on_click=self.__add_question_image)
        self.__answerContainer : ft.Container = ft.Container(
                        content=ft.Image(src_base64=self.__restapi.AnswerPlacehoderImg,
                                         fit=ft.ImageFit.FIT_HEIGHT, width=350),
                                         on_click=self.__add_answer)

        self.__choices : ft.Row = ft.Row()
        self.__answer_url : ft.TextField = ft.TextField(label="Enter answer URL (Probably a Google search)",on_submit=self.__save_question_click)
        self.__menu : ft.Row = ft.Row()
        self.__dropdowns : ft.Row = ft.Row()
        self.__environmentDropDown : ft.Dropdown = ft.Dropdown(label="Environment",on_change=self.__env_select)
        self.__subjectDropDown : ft.Dropdown = ft.Dropdown(label="Subject",on_change=self.__subject_select)
        self.__topicDropDown : ft.Dropdown = ft.Dropdown(label="topic",on_change=self.__topic_select)
        self.__dropdowns.controls = [self.__environmentDropDown, self.__subjectDropDown, self.__topicDropDown]
        self.__previous_question_button = ft.ElevatedButton(text="<",on_click=self.__show_previous_question,tooltip="Previous question")
        self.__next_question_button = ft.ElevatedButton(text=">",on_click=self.__show_next_question,tooltip="Next question")
        


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

        self.__add_qandc_details_prompt = ft.AlertDialog(
            modal=True,
            title=ft.Text("What do you want to get from this URL"),
            content=ft.Text(""),
            actions=[
                ft.TextButton("Both Questions & Choices", on_click=self.__add_question_and_choices),
                ft.TextButton("Only Question", on_click=self.__add_question_only),
                ft.TextButton("Only Choices", on_click=self.__add_choices_only),
                ft.TextButton("Cancel", on_click=self.__close_details_prompt), 
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
            
        )

        self.__add_qonly_details_prompt = ft.AlertDialog(
            modal=True,
            title=ft.Text("What do you want to get from this URL"),
            content=ft.Text(""),
            actions=[
                ft.TextButton("Add Question", on_click=self.__add_question),
                ft.TextButton("Cancel", on_click=self.__close_details_prompt),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
            
        )

    def __close_confirmdelete_yes(self, e):
        self.__restapi.deleteQuestion(self.__selected_restapi_url, self.__selected_question_id)
        self.__question_reset()
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

    def __buildSubjectDropDown(self):
        options : list = []
        for subject in self.__subjectsandtopics:
            options.append(ft.dropdown.Option(text=subject['title'],key=subject['id']))
        self.__subjectDropDown.options = options
        self.__subjectDropDown.update()
        

    def __buildTopicDropDown(self):
        options : list = []
        for subject in self.__subjectsandtopics:
            if subject['id'] == self.__selected_subject_id:
                for topic in subject['topics']:
                    topic_title : str = topic['title']
                    if topic['show_topic'] == '1':
                        topic_title += " (V)"
                    else:
                        topic_title += " (H)"
                    options.append(ft.dropdown.Option(text=topic_title,key=topic['id']))
                break
        self.__topicDropDown.options = options
        self.__topicDropDown.update()


    def __buildAppMenu(self):
        self.__menu.controls.append(ft.ElevatedButton(text="New Question",on_click=self.__new_question))
        self.__menu.controls.append(ft.ElevatedButton(text="+ Question",on_click=self.__add_question_image))
        self.__menu.controls.append(ft.ElevatedButton(text="+ Choice",on_click=self.__add_choice))
        self.__menu.controls.append(ft.ElevatedButton(text="+ Answer",on_click=self.__add_answer))
        self.__menu.controls.append(ft.ElevatedButton(text="Get from URL",on_click=self.__open_details_prompt))
        self.__menu.controls.append(ft.ElevatedButton(text="Save",on_click=self.__save_question_click))
        self.__menu.controls.append(ft.ElevatedButton(text="Clear choices",on_click=self.__clear_choices))
        self.__menu.controls.append(self.__previous_question_button)
        self.__menu.controls.append(self.__next_question_button)

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
                if question['topic_id'] != self.__selected_topic_id:
                    subject_title = None
                    topic_title = None
                    for subject in self.__subjectsandtopics:
                        subject_title = subject['title']
                        for topic in subject['topics']:
                            topic_title = topic['title']
                            if topic['id'] == question['topic_id']:
                                self.OpenAlert(f'The question is of subject: "{subject_title}" and topic "{topic_title}"\nYou will need to pick those from the dropdowns before you can view this question')
                else:
                    self.__question_reset()
                    self.__selected_question_id = question['id']
                    if question['description']:
                        self.__questionContainer.clean()
                        self.__questionContainer.content = ft.TextField(value=question['description'])
                    else:
                        self.__questionContainer.content.src_base64 = question['filestr']
                    self.__questionIDTxt.value = question['id']
                    self.__answerContainer.content.src_base64 = question['answer']['filestr']
                    self.__answer_url.value = question['answer']["url"]
                    for choice in question['choices']:
                        self.__choices.controls.append(ft.Checkbox(label=chr(self.__choice_counter),value=True if choice['correct_ans']=="1" else False ))
                        choiceContainer : ft.Container = ft.Container(on_click=self.__choice_select)
                        self.__choice_counter += 1
                        if choice['description']:
                            choiceContainer.content = ft.TextField(value=choice['description'])
                        else:
                            choiceContainer.content = ft.Image(src_base64=choice['filestr'],fit=ft.ImageFit.FIT_HEIGHT,width=150)
                        self.__choices.controls.append(choiceContainer)
                    self.update()
                    
        else:
            self.OpenAlert("You haven't selected an Environment to run in")

    def __question_reset(self):
        # re-init question
        self.__choice_counter = 65 # which is A caps
        self.__selected_question_id = -1
        self.__questionIDTxt.value = self.__selected_question_id
        theApp.ClearClipboard()
        # self.__question.src = None
        self.__questionContainer.content = ft.Image(src_base64=self.__restapi.QuestionPlacehoderImg)
        self.__answerContainer.content.src_base64 = self.__restapi.AnswerPlacehoderImg
        self.__choices.clean()
        self.__answer_url.value = ''
        self.update()


    def __new_question(self, e):
        self.__question_reset()
 
    def __clear_choices(self, e):
        self.__choices.clean()
        self.__choices.update()

    def __save_question(self, question_type):
        questionData : dict = dict()
        questionData["id"] = self.__selected_question_id;
        questionData['choices'] : list = list()
        for i, ctrl in enumerate(self.__choices.controls):
            if type(ctrl) == ft.Checkbox:
                choice : dict = dict()
                choice['iscorrect'] = 1 if ctrl.value else 0
                choiceContainer : ft.Container = self.__choices.controls[i + 1]
                if isinstance(choiceContainer.content,ft.TextField):
                    choice["description"] = str(choiceContainer.content.value)
                elif isinstance(choiceContainer.content,ft.Image):
                    choice["imageStr"] = choiceContainer.content.src_base64
                questionData['choices'].append(choice)
        questionData["subjectID"] = self.__selected_subject_id
        questionData["topicID"] = self.__selected_topic_id
        questionData["questionTypeID"] = question_type.value
        if isinstance(self.__questionContainer.content,ft.TextField):
            questionData["description"] = str(self.__questionContainer.content.value)
        elif isinstance(self.__questionContainer.content,ft.Image):
            questionData["imageStr"] = self.__questionContainer.content.src_base64
        if self.__answerContainer.content.src_base64 == self.__restapi.AnswerPlacehoderImg:
          questionData["answerImageStr"] = self.__restapi.NoAnswerAvailableImg
        else:
          questionData["answerImageStr"] = self.__answerContainer.content.src_base64
        questionData["answerURL"] = self.__answer_url.value
        questionID = self.__restapi.saveQuestion(questionDict=questionData, question_id=self.__selected_question_id, restapiurl=self.__selected_restapi_url)
        self.OpenAlert(f"New Question ID: {questionID}")
        self.__question_reset()

    # check that at least one choice is selected as correct
    def __has_correct_answer(self):
        for i, ctrl in enumerate(self.__choices.controls):
            if type(ctrl) == ft.Checkbox:
                if ctrl.value:
                    return True
        else:
            return False

    def __save_question_click(self, e):
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
            if self.__answerContainer.content.src_base64 != self.__restapi.AnswerPlacehoderImg or self.__answer_url.value:
                allGood = True
            else:
                self.OpenAlert("You haven't added an answer image or an answer URL. You must add at least one of them")
                allGood = False

        if allGood:
            if len(self.__choices.controls) == 0:
                self.__open_yesnoprompt()
            elif len(self.__choices.controls) == 1:
                allGood = False
            else:
                if self.__has_correct_answer():
                    # save as MCQ
                    self.__save_question(self.QuestionType.mcq)
                else:
                    self.OpenAlert("You haven't selected any choices as correct. Please select at least one.")

        
    def __env_select(self, e):
        # clear out subject and topic lists and selected values
        self.__subjectDropDown.clean()
        self.__topicDropDown.clean()
        self.__question_reset()
        self.__selected_subject_id = None
        self.__selected_topic_id = None
        
        self.__selected_restapi_url = e.control.value
        self.__subjectsandtopics = self.__restapi.getSubjectsAndTopics(self.__selected_restapi_url)
        self.__buildSubjectDropDown()
        # also let's get the question types for the selected env
        self.QuestionType = Enum('QuestionType', self.__restapi.getQuestionTypes(self.__selected_restapi_url))

    def __subject_select(self, e):
        self.__selected_subject_id = e.control.value
        self.__buildTopicDropDown()
        # self.__question_reset()

    def __topic_select(self, e):
        self.__selected_topic_id = e.control.value
        # self.__question_reset()

    def __add_question_image(self, e):
        img = ImageGrab.grabclipboard()
        if img is not None:
            self.__questionContainer.content.src_base64 = theApp.GetImageString(img)
            self.__questionContainer.update()
            theApp.ClearClipboard()
        else:
            self.OpenAlert("No Question image found on clipboard.")

    def __add_from_url(self, whatoadd : AddFromUrl):
        if whatoadd == AddFromUrl.OnlyQuestion or whatoadd == AddFromUrl.BothQuestionAndChoices:
            self.__questionContainer.clean()
            self.__questionContainer.content = ft.TextField(value=getTextFromSoup(self.__qc.question))
            self.__questionContainer.update()
        if whatoadd == AddFromUrl.OnlyChoices or whatoadd == AddFromUrl.BothQuestionAndChoices:
            self.__choices.controls.clear()
            for choice,is_right in self.__qc.choices.items():
                self.__choices.controls.append(ft.Checkbox(label=chr(self.__choice_counter),value=is_right))
                self.__choice_counter += 1
                choiceContainer : ft.Container = ft.Container(
                    content=ft.TextField(value=getTextFromSoup(choice)),
                    on_click=self.__choice_select,
                    width=120,
                    
                )
                self.__choices.controls.append(choiceContainer)
        self.update()
        theApp.ClearClipboard()
    
    # this is required if ONLY a question is found / displayed
    def __add_question(self, e):
        self.__add_qonly_details_prompt.open = False
        self.page.update()
        self.__add_from_url(AddFromUrl.OnlyQuestion)

    
    def __add_question_only(self, e):
        self.__add_qandc_details_prompt.open = False
        self.page.update()
        self.__add_from_url(AddFromUrl.OnlyQuestion)

    def __add_choices_only(self, e):
        self.__add_qandc_details_prompt.open = False
        self.page.update()
        self.__add_from_url(AddFromUrl.OnlyChoices)

    def __add_question_and_choices(self, e):
        self.__add_qandc_details_prompt.open = False
        self.page.update()
        self.__add_from_url(AddFromUrl.BothQuestionAndChoices)

    def __close_details_prompt(self, e):
        self.__add_qandc_details_prompt.open = False
        self.page.update()      

    def __open_details_prompt(self, e):
        url = getClipboardData()
        if url:
            self.__qc = getQandC(url)
            if self.__qc:
                promptText : str = getTextFromSoup(self.__qc.question)
                for choice,is_right in self.__qc.choices.items():
                    if is_right:
                        promptText += f"\n(Correct) {getTextFromSoup(choice)}"
                    else:
                        promptText += f"\n{getTextFromSoup(choice)}"
                if len(self.__qc.choices.items()) == 0:
                    self.__add_qonly_details_prompt.content.value = promptText
                    self.__add_qonly_details_prompt.open = True
                    self.page.dialog = self.__add_qonly_details_prompt
                    self.page.update()
                    pass
                else:
                    self.__add_qandc_details_prompt.content.value = promptText
                    self.__add_qandc_details_prompt.open = True
                    self.page.dialog = self.__add_qandc_details_prompt
                    self.page.update()
            else:
                self.OpenAlert(f"Doesn't seem to be a supported URL\n{url}")
        else:
            self.OpenAlert("Nothing found on clipboard")

    def __add_answer(self, e):
        img = ImageGrab.grabclipboard()
        if img is not None:
            self.__answerContainer.content.src_base64 = theApp.GetImageString(img)
            self.__answerContainer.update()
            theApp.ClearClipboard()
        else:
            self.OpenAlert("No Answer image found on clipboard.")

    def __choice_select(self, e):
        img = ImageGrab.grabclipboard()
        if img is not None:
            e.control.content=ft.Image(src_base64=theApp.GetImageString(img),fit=ft.ImageFit.FIT_HEIGHT,width=150)
            e.control.update()
            theApp.ClearClipboard()

    def __add_choice(self, e):
        img = ImageGrab.grabclipboard()
        if img is not None:
            self.__choices.controls.append(ft.Checkbox(label=chr(self.__choice_counter)))
            self.__choice_counter += 1
            choiceContainer : ft.Container = ft.Container(
                content=ft.Image(src_base64=theApp.GetImageString(img),fit=ft.ImageFit.FIT_HEIGHT,width=150),
                on_long_press=self.__choice_select
            )
            self.__choices.controls.append(choiceContainer)
            self.update()
            theApp.ClearClipboard()
        else:
            self.OpenAlert(f"No choice \"{chr(self.__choice_counter)}\" image found on clipboard.")


    def build(self):
        # application's root control (i.e. "view") containing all other controls
        return ft.Column(
            controls=[self.__dropdowns,self.__menu,self.__questionRow, self.__questionContainer,self.__answer_url,self.__choices,self.__answerContainer]
        )

    @staticmethod
    def ClearClipboard():
        if windll.user32.OpenClipboard(None):
            windll.user32.EmptyClipboard()
            windll.user32.CloseClipboard()

    @staticmethod
    def GetImageString(pilImg):
        buff = BytesIO()
        pilImg.save(buff, format="PNG")
        return base64.b64encode(buff.getvalue()).decode("utf-8")




def main(page: ft.Page):
    page.title = "traPCM App"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add(theApp())

ft.app(target=main)