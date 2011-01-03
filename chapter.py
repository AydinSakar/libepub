from lxml import etree

class Chapter:
    
    def __init__(self, chapter_id, chapter_file):
        self.id = chapter_id
        self.content = chapter_file.read()

    def __str__(self):
        html = etree.HTML(self.content)
        return html.find(".//title").text
