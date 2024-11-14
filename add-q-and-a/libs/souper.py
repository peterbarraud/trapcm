from bs4 import BeautifulSoup
from requests import get

def getSoup(url : str):
    return BeautifulSoup(get(url).content,features='html.parser')

def getTextFromSoup(text : str):
    soup = BeautifulSoup(markup=text,features='html.parser')
    return(soup.get_text())