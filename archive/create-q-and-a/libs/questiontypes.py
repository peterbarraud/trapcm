from libs.database import Database

def get_question_type(db: Database):
    q_types = db.QuestionTypes
    print("Pick a Question type:")
    for i, sub in q_types.items():
        print(f"{sub.ID} for {sub.Title}")
    q_types_id = int(input())
    if q_types_id not in q_types:
        raise Exception("You haven't picked a valid topic. Run again")
    return q_types[q_types_id]
