from libs.statics import Statics

class DropDownBuilder:

    @staticmethod
    def EnvDropDown(appObject, ft):
        envs = appObject.__restapi.PCMEnvs
        options : list = []
        for i, v in envs.items():
            options.append(ft.dropdown.Option(key=v,text=i))
        appObject.__environmentDropDown.options = options

    @staticmethod
    def SourcesDropDown(appObject, ft):
        options : list = []
        for source in appObject.__restapi.getQuestionSources(appObject.__selected_restapi_url):
            options.append(ft.dropdown.Option(text=source['title'],key=source['id']))
        appObject.__sourceDropDown.options = options
        appObject.__sourceDropDown.update()

    @staticmethod
    def TopicDropDown(appObject, ft):
        options : list = []
        for subject in appObject.__subjectsandtopics:
            if subject['id'] == appObject.__selected_subject_id:
                for topic in subject['topics']:
                    if (topic_title := Statics.GetTopicTitle(topic)) is not None:
                        options.append(ft.dropdown.Option(text=topic_title,key=topic['id']))
                break
        appObject.__topicDropDown.options = options
        appObject.__topicDropDown.update()

    @staticmethod
    def SubjectDropDown(appObject, ft):
        options : list = []
        for subject in appObject.__subjectsandtopics:
            options.append(ft.dropdown.Option(text=subject['title'],key=subject['id']))
        appObject.__subjectDropDown.options = options
        appObject.__subjectDropDown.update()
