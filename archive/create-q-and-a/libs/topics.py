from libs.database import Database
from enum import Enum

class TopicVisibility(Enum):
    Shown = 1
    Hidden = 0

def get_topic_by_subject(db : Database,subject_id):
    topics = db.TopicsBySubject(subject_id)
    if len(topics) == 0:
        print("No topics were found for this subject")
        return None
    while 1:
        print("Pick a Topic (Or press X to exit):")
        for i, topic in topics.items():
            print(f"{topic.ID} for {topic.Title}")
        ui = input()    #ui for user input
        if ui == 'x' or ui == 'X':
            return None
        else:
            if ui.isnumeric() and int(ui) in topics:
                return topics[int(ui)]
            else:
                print("Yoda: Invalid topic you have picked")

def get_topic_by_subject_by_visibility(db : Database,subject_id, topic_visibility : TopicVisibility):
    topics = db.TopicsBySubjectByVisibility(subject_id, topic_visibility=topic_visibility)
    if len(topics) == 0:
        print("No topics were found for this subject")
        return None
    while 1:
        print(f"Pick a Topic to be {topic_visibility.name} (Or press X to exit):")
        for i, topic in topics.items():
            print(f"{topic.ID} for {topic.Title}")
        ui = input()    #ui for user input
        if ui == 'x' or ui == 'X':
            return None
        else:
            if ui.isnumeric() and int(ui) in topics:
                return topics[int(ui)]
            else:
                print("Yoda: Invalid topic you have picked")

def main():
    print("This is a library that should be called from a client")
if __name__ == '__main__':
    main()
    
