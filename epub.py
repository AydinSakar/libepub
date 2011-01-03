#!/usr/bin/env python

# A module to read, write, transform, and generally handle epub format
# thanks to http://www.jedisaber.com/eBooks/tutorial.asp for a primer on epub format

import zipfile
from lxml import etree

CONTAINER_PATH = "META-INF/container.xml"

class Book:
    
    def __init__(self, path):
        self.archive = zipfile.ZipFile(path, 'r') # read-only for now
        
        # Path to the OPF file which points to book content
        self.opf_path = self._get_opf_path()
        self._parse_opf()
        
        #get OPF_path directory
        self.opf_dir = self.opf_path.split("/")[0]

        # The content of this book, divided into chapters
        self.chapters = []
        for chapter_id in self.spine:
            path = self.opf_dir + '/' + self.manifest[chapter_id]['href']
            chapter = Chapter(chapter_id, self.archive.open(path))
            self.chapters.append(chapter)
        
    def _get_opf_path(self):
        """Get the path to the OPF file for this epub"""
        # at the bare minimum, all proper epub files contain this file
        container = self.archive.open(CONTAINER_PATH)
        
        # need to parse xml to get the location
        doc = etree.parse(container)
        root = doc.getroot()
        
        # construct appropriate namespace mapping
        PREFIX = "a" # arbitrary
        ns = root.nsmap
        ns[PREFIX] = ns[None]
        ns.pop(None)
        
        # Read the location
        query = "/%(PREFIX)s:container/%(PREFIX)s:rootfiles/%(PREFIX)s:rootfile" % {"PREFIX" : PREFIX}
        location_node = doc.xpath(query, namespaces=ns)[0]
        opf_path = location_node.get('full-path')
        return opf_path
        
    def _parse_opf(self):
        """Parse and store the metadata info on this epub"""
        opf = self.archive.open(self.opf_path, "r")
        tree = etree.parse(opf)
        root = tree.getroot()

         # construct appropriate namespace mapping
        PREFIX = "a" # arbitrary
        ns = root.nsmap
        ns[PREFIX] = ns[None]
        ns.pop(None)

        self.book_id = root.get('unique-identifier')
        
        base_query = "/%(P)s:package/%(P)s:" % {"P" : PREFIX}
        # parse Metadata
        metadata_root = root.xpath(base_query + 'metadata', namespaces=ns)[0]
        self._parse_metadata(metadata_root)

        # parse Manifest
        manifest_root = root.xpath(base_query + 'manifest', namespaces=ns)[0]
        self._parse_manifest(manifest_root)

        # parse Spine
        spine_root = root.xpath(base_query + 'spine', namespaces=ns)[0]
        self._parse_spine(spine_root)

    def _parse_metadata(self, root):
        """Parse and store the info in the given metadata root"""
        self.metadata = {}
        for data in root:
            tag_name = data.tag.split('}')[-1]
            self.metadata[tag_name] = data.text

    def _parse_manifest(self, root):
        """Parse and store the item declarations in given manifest root"""
        self.manifest = {}
        for item in root:
            item_info = dict( [key, item.get(key)] for key in item.keys() )
            item_id = item_info['id']
            self.manifest[item_id] = item_info

    def _parse_spine(self, root):
        """Parse and store the order in the given spine root"""
        self.spine = [itemref.get('idref') for itemref in root]

    def __str__(self):
        return str([str(chp) for chp in self.chapters])

class Chapter:
    
    def __init__(self, chapter_id, chapter_file):
        self.id = chapter_id
        self.content = chapter_file.read()

    def __str__(self):
        html = etree.HTML(self.content)
        return html.find(".//title").text


if __name__ == "__main__":
    b = Book('sample.epub')
    print b
