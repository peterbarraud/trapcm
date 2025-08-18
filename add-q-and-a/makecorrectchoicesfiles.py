from re import search as research, findall as refindall
from os.path import isdir
from libs.statics import Statics

def main(folder_name):
    with open(r'D:\tech-stuff\trapcm\qanda-files\jee\2025-jan\maths\all-choices.txt') as f:
        lines = [l.strip() for l in f if l.strip() != '']
        i = 0
        while True:
            if len(lines) == i:
                break
            topic_title = lines[i]
            if research('^[A-Za-z]',topic_title) or '3d' in topic_title:
                print(f"Doing {topic_title}")
                topic_folder_name = f"{folder_name}/{Statics.MakeFolderNameNice(topic_title)}"
                if isdir(topic_folder_name):
                    correct_answer_file = open(f"{topic_folder_name}/correct.choices",'w')
                    i += 1
                    while not research('^[A-Za-z]',lines[i]):
                        correct_answers = lines[i]
                        m = refindall(r'([\d]{1,2}\.\s*\([\d]+?\))',correct_answers)
                        correct_answer_file.write("\n".join(m))
                        i += 1
                        if len(lines) == i:
                            break
                    correct_answer_file.close()
                else:
                    print(f"topic folder not found: {topic_folder_name}")
                    break




if __name__ == "__main__":
    # we will need to specify the folder in which the qanda files have been made for this exam
    start_folder = r'D:\tech-stuff\trapcm\qanda-files\jee\2025-jan\maths'
    main(start_folder)
    print("All DONE")