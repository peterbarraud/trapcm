from glob import glob
from pathlib import Path
from os import mkdir, path
from shutil import move

def make_pyc_structure(folder_name : str):
    for pdf in [x for x in glob(f"{folder_name}/*pdf") if 'solution' not in x]:
        print(f"doing: {pdf}")
        new_folder : str = f"{folder_name}/{Path(pdf).stem}"
        mkdir(new_folder)
        mkdir(f"{new_folder}/answer-files")
        mkdir(f"{new_folder}/question-files")
        new_file_destination = f"{new_folder}/{Path(pdf).stem}.pdf"
        solution_file_source = f"{folder_name}/{Path(pdf).stem}-solution.pdf"
        solution_file_destination = f"{new_folder}/{Path(pdf).stem}-solution.pdf"
        move(pdf, new_file_destination)
        move(solution_file_source, solution_file_destination)

def make_correct_choices_file(raw_correct_choices_file):
    folder_name = path.dirname(raw_correct_choices_file)
    mkdir(f"{folder_name}/topic1")
    f1 = open(f"{folder_name}/topic1/correct.choices",'w')
    with open(raw_correct_choices_file, encoding='utf-8') as f:
        for l in [x.strip() for x in f if x[0] == '(' if x[1] in ['A','B','C','D'] if x[2] == ')']:
            f1.write(f"({l[1].lower()})\n")

    f1.close()

def main():
    # make_pyc_structure(r'C:\Users\barraud\Documents\daniel-studies\pyq\chemistry\2014')
    make_correct_choices_file(r'C:\Users\barraud\Documents\daniel-studies\pyq\maths\2024\65-2-3 (Set 2, Subset 3)\answer-files\correct.choices')
        # break



if __name__ == '__main__':
    main()
    