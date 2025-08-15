# from bs4 import BeautifulSoup
# from requests import get
from urllib.parse import urlparse
from re import search 
from libs.qandc import QandC
from libs.souper import getSoup, getTextFromSoup
from json import loads

def __getNextData(url):
    soup = getSoup(url)
    data_tag = soup.find(id='__NEXT_DATA__')
    s = soup.find_all('script')
    return loads(data_tag.next)

def __getVedantuQandC(url):
    soup = getSoup(url)
    qandc_soup = soup.find(id='question-section-id')
    body_str = str(qandc_soup.body)
    question_group = search('<body>(.+?)<br/>', body_str)
    question = question_group.groups(0)[0]
    choice_group = search('<br/>A\.\s*(.+?)<br/>B\.\s*(.+?)<br/>C\.\s*(.+?)<br/>D\.\s*(.+?)<br/>', body_str)
    choices = choice_group.groups(0)
    return QandC(question,choices)

def __getEduRevQandC(url):
    soup = getSoup(url)
    qandc_soup = soup.find('div',{'class':'questionHeader'})
    question = qandc_soup.div.text
    choices = [li.text for li in qandc_soup.ul]
    return QandC(question,choices)

def __getByJUSQandC(url):
    soup = getSoup(url)
    questionBox = soup.find(id='questionBox')
    # print()
    choicesContainer = soup.find(class_='questionoptions_options__kZnqk')
    choices : list = [choice.text for choice in choicesContainer.find_all(class_='mjx-math')]
    return QandC(questionBox.text.strip(),choices)

def __getTopprQandC(url):
    data_json = __getNextData(url)
    question_data = data_json['props']['pageProps']['data']['prerenderData']
    for c in question_data['choices']:
        if len(getTextFromSoup(c['choice'])) > 4999:
            raise Exception(f"Choice too big. It has {c['choice']} chars. Limit is 4999")
    choices = {x['choice']:x['is_right'] for x in question_data['choices']}
    question = question_data['question']
    if len(getTextFromSoup(question)) > 4999:
        raise Exception(f'Question too big. It has {len(question)} chars. Limit is 4999')
    return QandC(question.strip(),choices)

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
    return QandC(question,choices)

def getQandC(url):
    domain = urlparse(url).netloc
    if 'vedantu.com' in url:
        return __getVedantuQandC(url)
    elif 'edurev.in' in url:
        return __getEduRevQandC(url)
    elif 'byjus.com' in url:
        return __getByJUSQandC(url)    
    elif 'doubtnut.com' in url:
        return __getDoubtNutQandC(url)
    elif 'toppr.com' in url:
        return __getTopprQandC(url=url)
    else:
        return None

if __name__ == '__main__':
    getQandC('https://edurev.in/question/1758536/Let-A-2--3--and-B---2--3--be-vertices-of-a-triangle-ABC--If-the-centroid-of-this-triangle-moves-on-t')
    

