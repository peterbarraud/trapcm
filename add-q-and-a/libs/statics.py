from ctypes import windll
import base64
from PIL import BmpImagePlugin, PngImagePlugin
from io import BytesIO
from os.path import isfile
import cv2
from re import sub as resub

class Statics:
    @staticmethod
    def ClearClipboard():
        if windll.user32.OpenClipboard(None):
            windll.user32.EmptyClipboard()
            windll.user32.CloseClipboard()

    @staticmethod
    def GetImageString(imageValue):
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
    def ResizeOnVertical(img_list, interpolation  
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


    # obsolete method
    @staticmethod
    def GetImageStringFromFile(filePath):
        with open(filePath, 'rb') as f:
            return base64.b64encode(f.read()).decode("utf-8")

    @staticmethod
    def getImageFromFile(filePath):
        with open(filePath, 'rb') as f:
            return f.read()

    @staticmethod
    def GetTopicTitle(topic):
        topic_title : str = topic['title']
        if topic['show_topic'] == '1':
            topic_title += " (V)"
        else:
            topic_title += " (H)"
        return topic_title
    
    @staticmethod
    def MakeFolderNameNice(topic_name : str):
        topic_folder_name = topic_name.lower()
        topic_folder_name = resub(r'\s*(,|&)\s*','_',topic_folder_name)
        topic_folder_name = resub(r'\s*\((H|h|V|v)\)\s*$','',topic_folder_name)
        topic_folder_name = resub(r'\s*(\s*\(\s*|\s*\)\s*)\s*','_',topic_folder_name)
        topic_folder_name = topic_folder_name.replace(' ','_')
        topic_folder_name = topic_folder_name.strip("_")
        return topic_folder_name

    @staticmethod
    def MakeClipboadIntoFractions(clipboardConentArray : list):
        # first check there are 
        # first making sure all entries are integers
        if len(clipboardConentArray) == len([a for a in clipboardConentArray if a.lstrip('-+').isdigit()]):
            # then add the pairs to numerator/demoninator
            new_text_parts : list = []
            for i in range(4):
                new_text_parts.append(f"{clipboardConentArray.pop(0)}/{clipboardConentArray.pop(0)}")
            return new_text_parts
        else:
            return clipboardConentArray
