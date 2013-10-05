
def escapeHTMLQuotes(term):

    return term.replace('"', '&quot;').replace("'",'&#39;')

class Article():

    title = ""
    summary = ""
    url = ""
    date = None
    image = ""
    imageWidth = 0
    imageHeight = 0
    topic = ""

    def __init__(self, title = "", summary = "", url = "", date = None, topic = ""):

        self.title = escapeHTMLQuotes(title)
        self.summary = escapeHTMLQuotes(summary)
        self.url = url
        self.date = date
        self.topic = escapeHTMLQuotes(topic)

class Item():

    article = Article()
    fbpeople = [] 