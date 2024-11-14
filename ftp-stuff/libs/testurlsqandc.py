from bs4 import BeautifulSoup
from requests import get
from urllib.parse import urlparse
from re import search 
from json import loads

def __getTopprQandC(url):
    soup = BeautifulSoup(get(url).content, 'html.parser')
    qandc_soup = soup.find('div',{'class':'text_section__rmlLE'})
    with open(r'C:\Users\barraud\Documents\tech-stuff\pcm\downloaded-pics\toppr.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(soup)
    # question = qandc_soup.div.text
    # print(question)
    # for li in qandc_soup.ul:
    #     print(li.text)



    # body_str = str(qandc_soup.body)
    # question_group = search('<body>(.+?)<br/>', body_str)
    # question = question_group.groups(0)[0]
    # choice_group = search('<br/>A\.\s*(.+?)<br/>B\.\s*(.+?)<br/>C\.\s*(.+?)<br/>D\.\s*(.+?)<br/>', body_str)
    # choices = choice_group.groups(0)
def __getNextData(url):
    soup = BeautifulSoup(get(url).content, 'html.parser')
    data_tag = soup.find(id='__NEXT_DATA__')
    s = soup.find_all('script')
    return loads(data_tag.next)

def __getByJUSQandC(url):
    soup = BeautifulSoup(get(url).content, 'html.parser')
    questionBox = soup.find(id='questionBox')
    print(questionBox.text.strip())
    choicesContainer = soup.find(class_='questionoptions_options__kZnqk')
    choices : list = [choice.text for choice in choicesContainer.find_all(class_='mjx-math')]
    for choice in choices:
        print(choice)

def __getDoubtNutQandC(url):
    data_json = __getNextData(url)
    question = data_json['props']['pageProps']['ocrText']
    correct_ans = [ord(x)-64 for x in data_json['props']['pageProps']['textSolutionMathJax']['answer'].split("::")]
    choices = {}
    c = 1
    for opt, choice in data_json['props']['pageProps']['textSolutionMathJax'].items():
        if opt[:3] == 'opt':
            if c in correct_ans:
                choices[choice] = True
            else:
                choices[choice] = False
            c += 1
    print(choices)
        



def getQandC(url):
    domain = urlparse(url).netloc
    if 'doubtnut.com' in url:
        return __getDoubtNutQandC(url)
    else:
        return None

if __name__ == '__main__':
    getQandC('https://www.doubtnut.com/qna/35790239')
    

