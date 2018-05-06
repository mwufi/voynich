from bs4 import BeautifulSoup
import pandas as pd
import re
import itertools

DIR = 'data/'

# --------------- add in the image function ----------------
from IPython.display import Image
def display(folio):
    return Image('image/{}.jpg'.format(folio))

# --------------- for working with the data/takeshi.txt file ----------------
def process(line):
    line = line.strip()
    line = re.sub('-','.',line)
    line = re.sub('[\!<>\*\=\%]', '', line)
    header, line = line.split(' ', maxsplit=1)
    header = re.sub('[;\.]', ' ', header).split()
    line = line.replace('.',' ')
    return header, line.strip()

def pdFromFile(filename):
    with open(DIR + filename) as f:
        lines = f.readlines()

        df = []
        for line in lines:
            header, text = process(line)
            df.append({
                'folio': header[0],
                'paragraph': header[1],
                'line': header[2],
                'text': text,
            })
        
    return pd.DataFrame(df)

    
def VoynichOrdering(folio_name):
    """
    only used as an argument to sort()
    """
    page, part = re.match('f(\d+)(.+)', folio_name).groups()
    page = int(page)
    return page, part


class Voynich:
    """
    contains a dataFrame of all the folios (w/ line and paragraph numbers)
    with utility methods to get words and lines from a single folio
    """
    
    def __init__(self):
        self.data = pdFromFile('takeshi.txt')
        self.data['words'] = [len(x) for x in self.data.text.str.split()]
        self.folios = sorted(set(self.data.folio), key=VoynichOrdering)
        
    def getWords(self, number):
        return ' '.join(self.getLines(number))
    
    def getLines(self, number):
        lines = list(self.data[self.data.folio == number].text)
        return lines
    

# ------------------------ for working with data/*.xml files -------------------
import os
from pathlib import Path
class Folio:
    
    voynich = Voynich()
    
    def __init__(self, name):
        self.name = name
        
        self.data = None
        
        self.filename = Path(os.path.join(DIR, name + '.xml'))
        if self.filename.exists():
            self.readData()
        else:
            print('no file exist')
    
    def readData(self):
         with open(self.filename,"r") as infile:
            contents = infile.read()

            # build pandas dict
            soup = BeautifulSoup(contents,'xml')
            titles = soup.find_all('word')

            def parse(t):
                a = dict()
                for prop in ['x', 'y', 'width', 'height']:
                    a[prop] = int(t[prop])
                a['word'] = t.get_text()
                return a

            data = [parse(t) for t in titles]
            self.data = pd.DataFrame(data)
            
            self.wordcount = int(soup.find('folio')['wordCount'])
        
    
    @property
    def lines(self):
        return Folio.voynich.getLines(self.name)
            
    @property
    def text(self):
        if self.data is not None:
            return ' '.join(self.data.word)
