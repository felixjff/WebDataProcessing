#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entity Linking class
"""

from warcio.archiveiterator import ArchiveIterator
import html5lib
from bs4 import BeautifulSoup
import re
import time
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
import nltk
import csv

class EntityLinking(object):
    def __init__(self):
        self.web_content = None
        self.candidates = None
        self.result = None
        self.tagger = None
        
    def remove_tags(element):
        '''
            Defines which tags are excluded from the HTML file
        '''
        if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
            return False
        elif re.match('<!--.*-->', element):
            return False
        return True
    
    def parse_warc(self, file, record_attribute):
         '''
            parses compressed warc file by extracting html content and removing unnecessary elements
         '''
         html_pages_array = []
         try:
             with open(file, 'rb') as stream:
                 for record in ArchiveIterator(stream):
                     # if the record type is a response (which is the case for html page)
                     if record.rec_type == 'response':
                         # check if the response is http
                         if record.http_headers != None:
                             # Get the WARC-RECORD-ID
                             record_id = record.rec_headers.get_header(record_attribute)
                             # Clean up the HTML using BeautifulSoup
                             html = record.content_stream().read()
                             soup = BeautifulSoup(html, "html5lib")
                             data = soup.findAll(text=True)#.encode()
                             result = filter(self.remove_tags, data)
                             result2 = ' '.join(result)
                             result2 = ' '.join(result2.split())
                             # Build up the resulting list.
                             result2 = result2.encode('ascii', errors="ignore").decode('ascii') # Removing all strange characters like emojis
                             if result2 != '' and isinstance(result2, str):
                                 html_pages_array.append([record_id, result2])
         except Exception:
             print("Something went wrong with the archive entry")
    
    
         return html_pages_array
    
    def initialize_tagger(self, tagger):
        if tagger == 'StanfordNERTagger':
            # 3 class model for recognizing locations, persons, and organizations
            self.tagger = StanfordNERTagger('./tools/stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz',
                                            './tools/stanford-ner/stanford-ner.jar',
                                            encoding='utf-8')
        if tagger == 'nlkt':
            nltk.download('maxent_ne_chunker')
            nltk.download('words')
            nltk.download('averaged_perceptron_tagger')
            self.tagger = tagger
        
    def tokenize(self, text):
        return word_tokenize(text)
    
    def categorize(self, tokenized_text):
        # Named entity recognition
        if self.tagger != 'nlkt':
            return self.tagger.tag(tokenized_text)
        else:
            return nltk.pos_tag(tokenized_text)
    
    def nlkt_entities(self, record, tagged_text):
        entity_list = []
        for tupple in tagged_text:
            if tupple[1] == 'NNP':
                entity_list.append((record, tupple[0], tupple[1]))
    
    def st_entities(self, record, tagged_text):
        entity_list = []
        for tupple in tagged_text:
            if tupple[1] != 'O':
                entity_list.append((record, tupple[0], tupple[1]))
        
    def store_entities(self, output):
        with open('data/sample-output' +input[0][12:-1]+ '.csv', 'w', newline='') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL, delimiter=';')
            wr.writerow(output)
    