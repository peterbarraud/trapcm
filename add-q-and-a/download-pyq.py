from bs4 import BeautifulSoup
from urllib.request import urlretrieve, urlopen
from urllib.error import HTTPError
from requests import get
from os.path import exists as folderexists, isfile as fileexists
from os import makedirs



from libs.littlebeepbeep import beeper

def download_paper(url : str, save_dir : str) -> None:
    soup : BeautifulSoup = BeautifulSoup(get(url).text, 'html.parser')
    tables = soup.find_all('table')
    pyq_list = tables[0].tbody if len(tables) == 2 else tables[1].tbody
    solution_row_item = None
    for tr in pyq_list.find_all('tr'):
        question_paper_row_item = tr.find_all('td')[0]
        if len(tr.find_all('td')) == 2:
            solution_row_item = tr.find_all('td')[1]
        if question_paper_row_item.a:
            # print(question_paper_row_item.span.text, )
            if not fileexists(f"{save_dir}/{question_paper_row_item.span.text}.pdf"):
                urlretrieve(question_paper_row_item.a.attrs['href'], f"{save_dir}/{question_paper_row_item.span.text}.pdf")
            if solution_row_item.a:
                if not fileexists(f"{save_dir}/{question_paper_row_item.span.text}-solution.pdf"):
                    urlretrieve(solution_row_item.a.attrs['href'], f"{save_dir}/{question_paper_row_item.span.text}-solution.pdf")
                # print(solution_row_item.span.text, solution_row_item.a.attrs['href'])
            else:
                print(f"{question_paper_row_item.span.text} - solution not found")
        else:
            print(f"PYQ not found")
        # break
            


def main():
    base_dir : str = r'C:\Users\ctl\Documents\trapcm'
    for subject in ['maths','physics','chemistry']:
    # for subject in ['physics']:
        url_prefix = 'https://www.educart.co/previous-year-question-paper/cbse-class-12'
        pyq_midfix = 'previous-year-question-paper'
        for year in range(2014,2025):
        # for year in [2024]:
            url : str = f'{url_prefix}-{subject}-{pyq_midfix}-{year}'
            try:
                if urlopen(url).getcode() == 200:
                    print(url)
                    if not folderexists(f"{base_dir}/{subject}/{year}"):
                        makedirs(f"{base_dir}/{subject}/{year}")
                    download_paper(url, f"{base_dir}/{subject}/{year}")
            except HTTPError as err:
                if err.code == 404:
                    print(f"URL not found: {url}")
            finally:
                beeper(1,1000,100)
            # break
        # break
    

if __name__ == '__main__':
    main()
    beeper(5,1000,500)
