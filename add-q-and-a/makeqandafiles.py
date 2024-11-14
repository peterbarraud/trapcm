from typing import Any
import flet as ft
from flet_core.control import Control, OptionalNumber
from flet_core.ref import Ref
from flet_core.types import AnimationValue, OffsetValue, ResponsiveNumber, RotateValue, ScaleValue
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


@dataclass
class ImageDim:
    Width : int = 700
    Height : int = 800




class theApp(ft.UserControl):
    def __init__(self, page : ft.Page):
        super().__init__()

        self.__imageDim = ImageDim()
        self.__restapi = RestApi()

        self.__selected_restapi_url : str = None
        self.__selected_restapi_url : str = None
        self.__selected_subject_id : str = None
        self.__selected_source_id : str = None
        self.__imgToSave = None

        self.__QandA_file_number_is_focus = True
        

        self.__questionContainer : ft.Container = ft.Container(content=ft.Image(src_base64=self.__restapi.QuestionPlacehoderImg,
                                                                                fit=ft.ImageFit.CONTAIN,
                                                                                width=self.__imageDim.Width,
                                                                                height=self.__imageDim.Height),
                                                               on_click=self.__add_question_image)
        self.__QandA_folder_number : ft.TextField = ft.TextField(label="Folder name",width=200)
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

        self.__topicNumber : ft.TextField = ft.TextField(label="Topic#",width=100)
        page.on_keyboard_event = self.__on_keyboard
        
        self.__menu : ft.Row = ft.Row([self.__QandA_group,self.__QandA_folder_number,self.__topicNumber,self.__QandA_file_number])
        self.__dropdowns : ft.Row = ft.Row()
        self.__environmentDropDown : ft.Dropdown = ft.Dropdown(label="Environment",on_change=self.__env_select)
        self.__subjectDropDown : ft.Dropdown = ft.Dropdown(label="Subject",on_change=self.__subject_select)
        self.__sourcesDropDown : ft.Dropdown = ft.Dropdown(label="Source",on_change=self.__source_select)
        self.__dropdowns.controls = [self.__environmentDropDown, self.__subjectDropDown, self.__sourcesDropDown]
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
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def __close_overwriteprompt_no(self, e):
        self.__overwriteprompt.open = False
        self.page.update()

    def __close_overwriteprompt_yes(self, e):
        self.__overwriteprompt.open = False
        self.page.update()
        self.saveImgFile()

    def __open_overwriteprompt(self):
        self.__overwriteprompt.open = True
        self.page.dialog = self.__overwriteprompt
        self.page.update()



    def __close_namesuspectprompt_no(self, e):
        self.__namesuspectprompt.open = False
        self.page.update()

    def __close_namesuspectprompt_yes(self, e):
        self.__namesuspectprompt.open = False
        self.page.update()
        self.saveImgFile()

    def __open_namesuspectprompt(self):
        self.__namesuspectprompt.open = True
        self.page.dialog = self.__namesuspectprompt
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
        self.__sourcesDropDown.options = options
        self.__sourcesDropDown.update()


    def __buildSubjectDropDown(self):
        options : list = []
        for subject in self.__subjectsandtopics:
            options.append(ft.dropdown.Option(text=subject['title'],key=subject['id']))
        self.__subjectDropDown.options = options
        self.__subjectDropDown.update()

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
            if self.__QandA_folder_number.value:
                allGood = True
            else:
                self.OpenAlert("You haven't specified an QandA folder number")
                allGood = False
        if allGood:
            if self.__topicNumber.value:
                if self.__topicNumber.value.isnumeric():
                    allGood = True
                else:
                    self.OpenAlert("Topic number must be a number")    
                    allGood = False
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
                        self.__open_overwriteprompt()
                    else:
                        (suspect_filename, max_file_number) = self.__is_suspect_filename(folderForSave, file_name)
                        if suspect_filename:
                            # these print statements are REQUIRED
                            # Please DO NOT delete
                            print(f"File name being saved: {file_name}")
                            print(f"Current max file number: {max_file_number}")
                            print("*"*50)
                            self.__open_namesuspectprompt()
                        else:
                            self.saveImgFile()
                else:
                    self.OpenAlert(f"Folder doesn't exist: {parentFolder}")

    def __getQandAFolderLocation(self):
        for src_opt in self.__sourcesDropDown.options:
            if src_opt.key == self.__selected_source_id:
                for sub_opt in self.__subjectDropDown.options:
                    if sub_opt.key == self.__selected_subject_id:
                        qanda_folder_name = f"{self.__QandA_group.value}-files"
                        return f"{self.__restapi.QandAFilesRoot}/{src_opt.text.lower()}/{sub_opt.text.lower()}/{self.__QandA_folder_number.value}/{qanda_folder_name}/topic{self.__topicNumber.value}/"

    # we're going to create the folder if it doesn't exist
    # but only the answer-files/question-files or topic# folder
    # anything folder level above that, and we're erroring out
    # first check if topic# folder exists
    def __tryMakingFolderForSave(self, folderForSave):
        (allGood,parent) = (False,None)
        if folderexists(folderForSave):
            allGood = True
        else:
            if not folderexists(folderForSave):
                # then check the answer-files/question-files folder
                qanda_path = Path(folderForSave)
                if folderexists(qanda_path.parent):
                    # then create the topic# folder
                    makedirs(folderForSave)
                    allGood = True
                else:
                    # now check one level higher (that's the chapter path)
                    if folderexists(qanda_path.parent.parent):
                        # makedirs(qanda_path)
                        makedirs(folderForSave)
                        allGood = True
                    else:
                        (allGood,parent) = (False,qanda_path.parent.parent)
        return (allGood,parent)

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
        # clear out subject and topic lists and selected values
        self.__subjectDropDown.clean()
        self.__sourcesDropDown.clean()
        self.__selected_subject_id = None
        
        self.__selected_restapi_url = e.control.value
        try:
            self.__subjectsandtopics = self.__restapi.getSubjectsAndTopics(self.__selected_restapi_url)
            self.__buildSubjectDropDown()
            # also let's get the question types for the selected env
            self.QuestionType = Enum('QuestionType', self.__restapi.getQuestionTypes(self.__selected_restapi_url))
            self.__buildSourcesDropDown()
        except:
            self.OpenAlert("Couldn't hit this server")

    def __subject_select(self, e):
        self.__selected_subject_id = e.control.value


    def __source_select(self, e):
        self.__selected_source_id = e.control.value

    def __reset_image(self, _):
        self.__questionContainer.content = ft.Image(src_base64=self.__restapi.QuestionPlacehoderImg,fit=ft.ImageFit.CONTAIN,width=self.__imageDim.Width,height=self.__imageDim.Height)
        self.__questionContainer.update()

    def __undo_append_image(self, _):
        folderForSave : str = self.__getQandAFolderLocation()
        (allGood, parentFolder) = self.__tryMakingFolderForSave(folderForSave)
        if allGood:
            self.__imgToSave = Image.open(f'{folderForSave}tmp1.png')
            self.__questionContainer.content.src_base64 = theApp.getImageString(self.__imgToSave)
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
                merged_img = theApp.resize_on_vertical([cv2.imread(f'{folderForSave}tmp1.png'),
                                                        cv2.imread(f'{folderForSave}tmp2.png')])
                # we will have to write this back to disc
                cv2.imwrite(f'{folderForSave}tmp-final.png', merged_img)
                self.__imgToSave = Image.open(f'{folderForSave}tmp-final.png')
                self.__questionContainer.content.src_base64 = theApp.getImageString(self.__imgToSave)
                self.__questionContainer.update()
                self.__QandA_file_number.focus()
                theApp.ClearClipboard()
                self.__info_box_update("Image appended")
            else:
                self.OpenAlert(f"Folder doesn't exist: {parentFolder}")
        else:
            self.OpenAlert("No image found on clipboard.")

    def __add_question_image(self, _):
        self.__imgToSave = ImageGrab.grabclipboard()
        if self.__imgToSave is not None:
            self.__questionContainer.content.src_base64 = theApp.getImageString(self.__imgToSave)
            self.__questionContainer.update()
            self.__QandA_file_number.focus()
            theApp.ClearClipboard()
            self.__info_box_update("Init image added",False)
            
        else:
            self.OpenAlert("No image found on clipboard.")

    def build(self):
        # application's root control (i.e. "view") containing all other controls
        appendOptionsRow : ft.Row = ft.Row([ft.ElevatedButton(text="A(p)pend to image",on_click=self.__append_image),
                                            ft.ElevatedButton(text="(U)ndo image",on_click=self.__undo_append_image),
                                            ft.ElevatedButton(text="Reset Image",on_click=self.__reset_image)])
        return ft.Column(
            controls=[self.__dropdowns,self.__menu,appendOptionsRow,
                      ft.ElevatedButton(text="Save",on_click=self.__save),
                      self.__InfoBox,
                      self.__questionContainer]
        )

    @staticmethod
    def ClearClipboard():
        if windll.user32.OpenClipboard(None):
            windll.user32.EmptyClipboard()
            windll.user32.CloseClipboard()



    @staticmethod
    def getImageString(imageValue : Any):
        if isinstance(imageValue, list):
            with open(imageValue[0], 'rb') as f:
                return base64.b64encode(f.read()).decode("utf-8")
        else:
            buff = BytesIO()
            imageValue.save(buff, format="PNG")
            return base64.b64encode(buff.getvalue()).decode("utf-8")

    # obsolete method
    @staticmethod
    def getImageStringFromFile(filePath):
        with open(filePath, 'rb') as f:
            return base64.b64encode(f.read()).decode("utf-8")

    @staticmethod
    def getImageFromFile(filePath):
        with open(filePath, 'rb') as f:
            return f.read()

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
    page.title = "Make QandA Files App"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add(theApp(page))

ft.app(target=main)