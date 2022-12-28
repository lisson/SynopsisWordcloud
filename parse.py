import xml.etree.ElementTree as ET
import jinja2
import json
import argparse
from datetime import datetime

wordCounter = ({}, {})
skipWordList = []

def Parse(XmlPath):
    mediawikiNs = "{http://www.mediawiki.org/xml/export-0.5/}"

    with open(XmlPath,  encoding="utf8") as source:

        # get an iterable
        context = ET.iterparse(source, events=("start", "end"))

        # turn it into an iterator
        context = iter(context)

        # get the root element
        event, root = context.__next__()

        for event, elem in context:
            # do something with elem
            if(elem.tag == mediawikiNs + "text"):
                ParseText(str(elem.text))
            # get rid of the elements after processing
            root.clear()

def ParseText(textBody):
    if("'''Country:''' Japan" not in textBody and "'''Country:''' South Korea" not in textBody):
        return
    start = int(textBody.find("==Plot=="))+8
    if(start < 0):
        # no plot?
        return
    end = int(textBody.find("==", start+8, -1))
    plot = textBody[start:end]

    if("'''Country:''' Japan" in textBody):
        wd = wordCounter[0]
    if("'''Country:''' South Korea" in textBody):
        wd = wordCounter[1]

    for w in plot.split(" "):
        word = w.replace('"', "").replace("\n","").replace(",","").replace(".","").lower()
        if(IsWord(word) == False):
            continue
        CountWord(word.lower().strip(), wd)

def CountWord(word, wordDictionary):
    if(word not in wordDictionary):
        wordDictionary[word] = 1
        return
    wordDictionary[word] = wordDictionary[word] + 1

def IsWord(word):
    if(len(word.strip()) <= 0):
        return False
    if(word in skipWordList):
        return False
    if(word.startswith((':', '.', '(', '[', '{','«', '»', '*',"'''"))):
        return False
    if(any(w in word for w in ("[[", "]]", "}}", "}}")) ):
        return False
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create wordcloud.html from asianwiki xml dump.')
    parser.add_argument('XmlPath', help='Asian wiki xml')
    args = parser.parse_args()
    xmlPath = args.XmlPath
    print(f'Parsing {xmlPath}')

    with open("SkipWords.txt", "r") as f:
        skipWordList = f.read().split()

    Parse(xmlPath)
    now = datetime.now() # current date and time
    date_time = now.strftime("%m-%d-%Y-%H-%M-%S")

    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "template.html"
    template = templateEnv.get_template(TEMPLATE_FILE)

    Countries = ("jp", "kr")
    i = 0
    for c in Countries:
        file = f"Country{c}-{date_time}.json"
        with open(file,"w+", encoding="utf8") as ff:
            ff.write(json.dumps(wordCounter[i]))
        outputText = template.render(words=wordCounter[i])  # this is where to put args to the template renderer
        htmlFile = f"wordcloud{c}.html"
        with open(htmlFile,"w+", encoding="utf8") as ff:
            ff.write(outputText)
        i=i+1

