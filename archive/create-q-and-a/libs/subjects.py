from libs.database import Database

def get_subject(db : Database):
    subjects = db.Subjects
    while 1:
        print("Pick a subject. Or press x to exit:")
        for i, sub in subjects.items():
            print(f"{sub.ID} for {sub.Title}")
        ui = input()    #ui for user input
        if ui == 'x' or ui == 'X':
            return None
        else:
            if ui.isnumeric() and int(ui) in subjects:
                return subjects[int(ui)]
            else:
                print("Yoda: Invalid subject you have picked")
