from typing import Any
import flet as ft
# from flet_core.control import Control, OptionalNumber
# from flet_core.ref import Ref
# from flet_core.types import AnimationValue, OffsetValue, ResponsiveNumber, RotateValue, ScaleValue
from ctypes import windll
from PIL import ImageGrab, Image
import base64
import cv2
from io import BytesIO
from enum import Enum
from os.path import isfile, exists as folderexists
from os import listdir, makedirs
from dataclasses import dataclass
from pathlib import Path

from libs.restapi import RestApi
from libs.statics import Statics


@dataclass
class ImageDim:
    Width : int = 700
    Height : int = 800




class theApp():
    def __init__(self, page : ft.Page):

        self.__imageDim = ImageDim()
        self.__restapi = RestApi()

        self.__selected_restapi_url : str = None
        self.__selected_restapi_url : str = None
        self.__selected_subject_id : str = None
        self.__selected_source_id : str = None
        self.__imgToSave = None
        self.page = page

        self.__QandA_file_number_is_focus = True
        

        self.__questionContainer : ft.Container = ft.Container(content=ft.Image(src_base64=self.__restapi.QuestionPlacehoderImg,
                                                                                fit=ft.ImageFit.CONTAIN,
                                                                                width=self.__imageDim.Width,
                                                                                height=self.__imageDim.Height),
                                                               on_click=self.__add_question_image)
        self.__QandA_file_number : ft.TextField = ft.TextField(label="Img number",
                                                               on_submit=self.__on_QandA_image_enter,width=100,
                                                               on_focus=self.__QandA_file_number_focus,
                                                               on_blur=self.__QandA_file_number_blur)
        
        self.__QandA_file_number_is_focus = False

        self.__QandA_group : ft.RadioGroup = ft.RadioGroup(content=ft.Column([
                                                                ft.Radio(value="question", label="Question files"),
                                                                ft.Radio(value="answer", label="Answer files")]))
        topicItems : list = []
        for i in range(0,20):
            ft.dropdown.Option(i)
            topicItems.append(ft.dropdown.Option(i))

        self.__examNumber : ft.TextField = ft.TextField(label="Exam",width=100)
        page.on_keyboard_event = self.__on_keyboard
        
        self.__menu : ft.Row = ft.Row([self.__QandA_group,self.__examNumber,self.__QandA_file_number])
        self.__dropdowns : ft.Row = ft.Row()

        self.__envDropDownDropDown : ft.Dropdown = ft.Dropdown(label="Env",on_change=self.__env_select,width=110)
        self.__subjectDropDown : ft.Dropdown = ft.Dropdown(label="Subject",on_change=self.__subject_select,width=130)
        self.__topicDropDown : ft.Dropdown = ft.Dropdown(label="Topic",on_change=self.__topic_select)
        self.__sourceDropDown : ft.Dropdown = ft.Dropdown(label="Source",on_change=self.__source_select,width=150)


        self.__dropdowns.controls = [self.__envDropDownDropDown]
        self.__InfoBox : ft.Text = ft.Text("Information box")


        self.__buildEnvDropDown()

        self.__overwriteprompt = ft.AlertDialog(
            modal=True,
            title=ft.Text("Please confirm"),
            content=ft.Text("The file of this name already exists. Do you want to overwrite??"),
            actions=[
                ft.TextButton("Yes", on_click=self.__close_overwriteprompt_yes),
                ft.TextButton("No", on_click=self.__close_overwriteprompt_no),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )

        self.__namesuspectprompt = ft.AlertDialog(
            modal=True,
            title=ft.Text("Please confirm"),
            content=ft.Text("The file you're saving is not in sequence (See command prompt for details). Are you sure you want to save it with this number."),
            actions=[
                ft.TextButton("Yes", on_click=self.__close_namesuspectprompt_yes),
                ft.TextButton("No", on_click=self.__close_namesuspectprompt_no),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )

    def __on_keyboard(self, e: ft.KeyboardEvent):
        if e.ctrl:
            if e.key == 'S':
                self.__on_QandA_image_enter(self.__QandA_file_number)
            elif e.key == "D":
                self.__add_question_image(None)
            elif e.key == "P" or e.key == "F":
                self.__append_image(None)
            elif e.key == "U":
                self.__undo_append_image(None)
        if self.__QandA_file_number_is_focus and e.key == "Escape":
            self.__QandA_file_number.value = None
            self.__QandA_file_number.update()

    def OpenAlert(self, title):
        dlg : ft.AlertDialog = ft.AlertDialog(title=ft.Text(title))
        self.page.open(dlg)

    def __close_overwriteprompt_no(self, e):
        self.__overwriteprompt.open = False
        self.page.update()

    def __close_overwriteprompt_yes(self, e):
        self.__overwriteprompt.open = False
        self.page.update()
        self.saveImgFile()

    def __close_namesuspectprompt_no(self, e):
        self.__namesuspectprompt.open = False
        self.page.update()

    def __close_namesuspectprompt_yes(self, e):
        self.__namesuspectprompt.open = False
        self.page.update()
        self.saveImgFile()

    def __buildEnvDropDown(self):
        envs = self.__restapi.PCMEnvs
        options : list = []
        for i, v in envs.items():
            options.append(ft.dropdown.Option(key=v,text=i))
        self.__envDropDownDropDown.options = options

    def __buildSourcesDropDown(self):
        self.__sourceDropDown.options.clear()
        for source in self.__restapi.getQuestionSources(self.__selected_restapi_url):
            self.__sourceDropDown.options.append(ft.dropdown.Option(text=source['title'],key=source['id']))
        self.__sourceDropDown.visible = True
        self.__dropdowns.controls.append(self.__sourceDropDown)
        self.__dropdowns.update()

    def __buildSubjectDropDown(self):
        self.__subjectDropDown.options.clear()
        self.__subjectsandtopics = self.__restapi.getSubjectsAndTopics(self.__selected_restapi_url,self.SourceTitle)
        for subject in self.__subjectsandtopics:
            self.__subjectDropDown.options.append(ft.dropdown.Option(text=subject['title'],key=subject['id']))
        self.__subjectDropDown.visible = True
        # self.__dropdowns.controls.append(self.__subjectDropDown)
        self.__dropdowns.update()

    def __buildTopicDropDown(self):
        self.__topicDropDown.options.clear()
        for subject in self.__subjectsandtopics:
            if subject['id'] == self.__selected_subject_id:
                for topic in subject['topics']:
                    if (topic_title := Statics.GetTopicTitle(topic)) is not None:
                        self.__topicDropDown.options.append(ft.dropdown.Option(text=topic_title,key=topic['id']))
                break
        self.__topicDropDown.visible = True
        self.__dropdowns.controls.append(self.__topicDropDown)
        self.__dropdowns.update()


    def __QandA_file_number_focus(self, e):
        self.__QandA_file_number_is_focus = True

    def __QandA_file_number_blur(self, e):
        self.__QandA_file_number_is_focus = False

    def __is_suspect_filename(self, folderForSave : str, fileName : str):
        file_number_list = [int(x[0:-4]) for x in listdir(folderForSave) if x.endswith("png") if (x[0:-4]).isnumeric()]
        max_file_number : int = max(file_number_list) if file_number_list else 0
        if int(fileName) - 1 != max_file_number:
            return (True,max_file_number)
        return (False,0)
    
    def __save(self, e):
        self.__on_QandA_image_enter(self.__QandA_file_number)


    def __on_QandA_image_enter(self, e):
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
            if self.__selected_source_id:
                allGood = True
            else:
                self.OpenAlert("You haven't selected a Question Source")
                allGood = False
        if allGood:
            if self.__examNumber.value:
                    allGood = True
            else:
                self.OpenAlert("You haven't specified an QandA folder number")
                allGood = False
        if allGood:
            if self.__QandA_file_number.value:
                allGood = True
            else:
                self.OpenAlert("You haven't specified an QandA file number")
                allGood = False
        if allGood:
            if self.__imgToSave:
                allGood = True
            else:
                self.OpenAlert("You probably haven't added an image from your clipboard")
                allGood = False
        if allGood:
            file_name : str = e.value if isinstance(e, ft.TextField) else e.control.value
            if file_name.isnumeric():
                folderForSave : str = self.__getQandAFolderLocation()
                (allGood, parentFolder) = self.__tryMakingFolderForSave(folderForSave)
                if allGood:
                    self.__QandA_file_location = f"{folderForSave}{file_name}.png"
                    if isfile(self.__QandA_file_location):
                        self.page.open(self.__overwriteprompt)
                    else:
                        (suspect_filename, max_file_number) = self.__is_suspect_filename(folderForSave, file_name)
                        if suspect_filename:
                            # these print statements are REQUIRED
                            # Please DO NOT delete
                            print(f"File name being saved: {file_name}")
                            print(f"Current max file number: {max_file_number}")
                            print("*"*50)
                            self.page.open(self.__namesuspectprompt)
                        else:
                            self.saveImgFile()
                else:
                    self.OpenAlert(f"Folder doesn't exist: {parentFolder}")

    def __getQandAFolderLocation(self):
        return f"{self.__restapi.QandAFilesRoot}/{self.SourceTitle.lower()}/{self.__examNumber.value.lower()}/{self.SubjectTitle.lower()}/{Statics.MakeFolderNameNice(self.TopicTitle)}/{self.__QandA_group.value}-files/"
        
        # topic_folder_name = 
        # self.SourceTitle    
        
        
        # for src_opt in self.__sourceDropDown.options:
        #     if src_opt.key == self.__selected_source_id:
        #         for sub_opt in self.__subjectDropDown.options:
        #             if sub_opt.key == self.__selected_subject_id:
        #                 qanda_folder_name = f"{self.__QandA_group.value}-files"
        #                 topic_folder_name = Statics.MakeFolderNameNice(self.TopicTitle)
        #                 return f"{self.__restapi.QandAFilesRoot}/{src_opt.text.lower()}/{sub_opt.text.lower()}/{topic_folder_name}/{self.__examNumber.value}/{qanda_folder_name}/"

    # we're going to create the folder if it doesn't exist
    # but only the answer-files/question-files or topic# folder
    # anything folder level above that, and we're erroring out
    # first check if topic# folder exists
    def __tryMakingFolderForSave(self, folderForSave):
        if not folderexists(folderForSave):
            makedirs(folderForSave)
        return True, folderForSave
        # (allGood,parent) = (False,None)
        # if folderexists(folderForSave):
        #     allGood = True
        # else:
        #     if not folderexists(folderForSave):
        #         # then check the answer-files/question-files folder
        #         qanda_path = Path(folderForSave)
        #         if folderexists(qanda_path.parent):
        #             # then create the topic# folder
        #             makedirs(folderForSave)
        #             allGood = True
        #         else:
        #             # now check one level higher (that's the chapter path)
        #             if folderexists(qanda_path.parent.parent):
        #                 # makedirs(qanda_path)
        #                 makedirs(folderForSave)
        #                 allGood = True
        #             else:
        #                 (allGood,parent) = (False,qanda_path.parent.parent)
        # return (allGood,parent)

    def saveImgFile(self):
        if self.__questionContainer.content.src_base64 != self.__restapi.QuestionPlacehoderImg:
            self.__imgToSave.save(self.__QandA_file_location)
            self.__questionContainer.content = ft.Image(src_base64=self.__restapi.QuestionPlacehoderImg, fit=ft.ImageFit.CONTAIN,width=self.__imageDim.Width,height=self.__imageDim.Height)
            self.__QandA_file_number.value = str(int(self.__QandA_file_number.value) + 1)
            self.__QandA_file_number.update()
            self.__questionContainer.update()
            self.__info_box_update(f"Saved file: {self.__QandA_file_location}")
        else:
            self.OpenAlert("No QandA file image selected")
            

    def __info_box_update(self, txt, appendTxt=True):
        if appendTxt:
            self.__InfoBox.value += f"\n{txt}"
        else:
            self.__InfoBox.value = txt
        self.__InfoBox.update()

    def __env_select(self, e):
        # self.__examDropDown.visible = False
        self.__subjectDropDown.visible = False
        self.__topicDropDown.visible = False
        self.__sourceDropDown.visible = False
        self.__selected_subject_id = None
        # self.__selected_topic_id = None
        self.__selected_restapi_url = e.control.value
        try:
            # also let's get the question types for the selected env
            self.QuestionType = Enum('QuestionType', self.__restapi.getQuestionTypes(self.__selected_restapi_url))
            self.__buildSourcesDropDown()
        except Exception as err:
            self.OpenAlert(f"{err}")

    def __source_select(self, e):
        self.__selected_source_id = e.control.value
        for opt in e.control.options:
            if opt.key == e.control.value:
                self.SourceTitle = opt.text
                break
        self.__subjectDropDown.options.clear()
        self.__buildSubjectDropDown()
        self.__subjectDropDown.visible = True
        # self.__dropdowns.controls.append(self.__examDropDown)
        self.__dropdowns.controls.append(self.__subjectDropDown)
        self.__dropdowns.update()

    def __subject_select(self, e):
        self.__selected_subject_id = e.control.value
        for opt in e.control.options:
            if opt.key == e.control.value:
                self.SubjectTitle = opt.text
                self.__buildTopicDropDown()
                break


    def __topic_select(self, e):
        # self.__selected_topic_id = e.control.value
        for opt in e.control.options:
            if opt.key == e.control.value:
                self.TopicTitle = opt.text
                break        
        # for subject in self.__subjectsandtopics:
        #     if subject['id'] == self.__selected_subject_id:
        #         for topic in subject['topics']:
        #             if topic['id'] == self.__selected_topic_id:
        #                 if topic['test_name'] == 'jee':
        #                     self.__is_advanced_q_checkbox.visible = True
        #                     self.__is_advanced_q_checkbox.update()
        #                 elif topic['test_name'] == 'cbse':
        #                     self.__is_advanced_q_checkbox.visible = False
        #                     self.__is_advanced_q_checkbox.update()
        #                 else:
        #                     raise Exception(f"Topic: {self.__selected_topic_id} seems not to have a test_name - JEE or CBSE")


    def __reset_image(self, _):
        self.__questionContainer.content = ft.Image(src_base64=self.__restapi.QuestionPlacehoderImg,fit=ft.ImageFit.CONTAIN,width=self.__imageDim.Width,height=self.__imageDim.Height)
        self.__questionContainer.update()

    def __undo_append_image(self, _):
        folderForSave : str = self.__getQandAFolderLocation()
        (allGood, parentFolder) = self.__tryMakingFolderForSave(folderForSave)
        if allGood:
            self.__imgToSave = Image.open(f'{folderForSave}tmp1.png')
            self.__questionContainer.content.src_base64 = Statics.GetImageString(self.__imgToSave)
            self.__questionContainer.update()
            self.__info_box_update("Undone image append")
        else:
            self.OpenAlert(f"Folder doesn't exist: {parentFolder}")

    def __append_image(self, _):
        fromClipboard = ImageGrab.grabclipboard()
        if fromClipboard:
            folderForSave : str = self.__getQandAFolderLocation()
            (allGood, parentFolder) = self.__tryMakingFolderForSave(folderForSave)
            if allGood:
                # first save the current image to disc
                self.__imgToSave.save(f'{folderForSave}tmp1.png')
                # then save the clipboard image (to be appended)
                fromClipboard.save(f'{folderForSave}tmp2.png')
                # we are using another lib (cv2), so we need to read these back
                merged_img = Statics.ResizeOnVertical([cv2.imread(f'{folderForSave}tmp1.png'),
                                                        cv2.imread(f'{folderForSave}tmp2.png')])
                # we will have to write this back to disc
                cv2.imwrite(f'{folderForSave}tmp-final.png', merged_img)
                self.__imgToSave = Image.open(f'{folderForSave}tmp-final.png')
                self.__questionContainer.content.src_base64 = Statics.GetImageString(self.__imgToSave)
                self.__questionContainer.update()
                self.__QandA_file_number.focus()
                Statics.ClearClipboard()
                self.__info_box_update("Image appended")
            else:
                self.OpenAlert(f"Folder doesn't exist: {parentFolder}")
        else:
            self.OpenAlert("No image found on clipboard.")

    def __add_question_image(self, _):
        self.__imgToSave = ImageGrab.grabclipboard()
        if self.__imgToSave is not None:
            self.__questionContainer.content.src_base64 = Statics.GetImageString(self.__imgToSave)
            self.__questionContainer.update()
            self.__QandA_file_number.focus()
            Statics.ClearClipboard()
            self.__info_box_update("Init image added",False)
            
        else:
            self.OpenAlert("No image found on clipboard.")

    def build(self):
        # application's root control (i.e. "view") containing all other controls
        appendOptionsRow : ft.Row = ft.Row([ft.ElevatedButton(text="A(p)pend to image",on_click=self.__append_image),
                                            ft.ElevatedButton(text="(U)ndo image",on_click=self.__undo_append_image),
                                            ft.ElevatedButton(text="Reset Image",on_click=self.__reset_image)])
        self.__main_container = ft.Column(controls=[self.__dropdowns,self.__menu,appendOptionsRow,
                                                    ft.ElevatedButton(text="Save",on_click=self.__save),
                                                    self.__InfoBox, self.__questionContainer])
        self.page.add(self.__main_container)

def main(page: ft.Page):
    page.title = "Make QandA Files"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    theTrapApp = theApp(page)
    theTrapApp.build()


ft.app(target=main)

# def main(page: ft.Page):
#     page.title = "Make QandA Files App"
#     page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
#     page.add(theApp(page))

# ft.app(target=main)