from re import match as rematch
from libs.clipboardtext import *

def main(folder_path, sql_file_name):
    student_id = 2
    c = 0
    studentattempted_raw_data = 'insert into studentattempted (question_id,student_id,doubttype) values\n'
    for l in [x.strip() for x in getClipboardData().split("\n") if rematch(r'^\s*([\d]+?)\s*$',x)]:
        unanswered_question_id = l.replace('(','').replace('),','')
        studentattempted_raw_data += f'({unanswered_question_id},{student_id},"ar"),\n'
        c += 1
    studentattempted_raw_data = studentattempted_raw_data.strip().rstrip(',')
    studentattempted_raw_data += ';'

    setClipboardData(studentattempted_raw_data)
    print(f"Done for {c} rows")


if __name__ == "__main__":

    main(r'C:\Users\Peter\Documents\student-attempted-archival','student-att-qs.sql')
    
