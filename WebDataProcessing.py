#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entity Linking class
"""

from warcio.archiveiterator import ArchiveIterator
import html5lib
from bs4 import BeautifulSoup
import re
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
import nltk
import spacy
import csv

class EntityRecognition(object):
    def __init__(self):
        self.web_content = None
        self.candidates = None
        self.result = None
        self.tagger = None
        self.st = None
        self.nlp = None
        
    def remove_tags(self, element):
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
                    if record.rec_type == 'response' and record.http_headers != None and record.rec_headers.get_header(record_attribute):
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
        except Exception as e: 
            print(e)
    
        return html_pages_array
    
    def initialize_tagger(self, tagger):
        self.tagger = tagger
        if tagger == 'StanfordNERTagger':
            # 3 class model for recognizing locations, persons, and organizations
            self.st = StanfordNERTagger('./tools/stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz',
                                        './tools/stanford-ner/stanford-ner.jar',
                                        encoding='utf-8')
        if tagger == 'nlkt':
            nltk.download('maxent_ne_chunker')
            nltk.download('words')
            nltk.download('averaged_perceptron_tagger')
            nltk.download('punkt')
        
        if tagger == "spacy":
            self.nlp = spacy.load("en_core_web_sm")
        
    def tokenize(self, text):
        return word_tokenize(text)
    
    def categorize(self, tokenized_text):
        # Named entity recognition
        if self.tagger == 'StanfordNERTagger':
            return self.st.tag(tokenized_text)
        elif self.tagger == "spacy":
            return self.nlp(tokenized_text)
        else:
            return nltk.pos_tag(tokenized_text)
    
    def tweet_element(self, text):
        tweet = False
        if text in ['RT', 'tweet', 'AddThis', 'Button', 'BEGIN', 'Share', '|', 'END', 'A']:
            tweet = True
        if 'RT' in text:
            tweet = True
        if '@' in text:
            tweet = True
        
        return tweet
    
    def lexical(self, text):
        lexical = True
        non_lexical = ["=", "/", "<", ">", "."]
        for i in non_lexical:
            if i in text:
                lexical = False
        return lexical
    
    def word(self, text):
        word = True
        if len(text) < 3:
            word = False
        
        return word
    
    def extract_entities(self, record_id, tagged_text, spacy_ents = False):
        entity_list = []
        if self.tagger == 'spacy':
            # By default use the statistical model trained by spacy and the entities thereof.
            if spacy_ents:
                entities = tagged_text.ents
                for e in entities:
                    if e.label_ not in ['DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL', 'CARDINAL']:
                        entity_list.append((record_id, e, e.label_))
            else:
                for tupple in tagged_text:
                    if tupple.tag_ == 'NNP':
                        if not self.tweet_element(tupple.text) and lexical and word:
                            entity_list.append((record_id, tupple.text, tupple.tag_))
        else:
            for tupple in tagged_text:
                entity_list.append((record_id, tupple[0], tupple[1]))
        return entity_list
        
    def store_entities(self, output):
        with open('data/sample-output.tsv', 'a', newline='') as myfile:
            for e in output:
                myfile.write(e[0] + "\t" + e[1] + "\t" + e[2] + "\n")



##############################################################################

import codecs, difflib, Levenshtein, distance
from ElasticSearchClass import ElasticSearch 

class EntityLinking(ElasticSearch):
    def __init__(self):    
        self.holder = None
        
    def import_entities(self):
        entities = []
        # Load file with all recognized entity surface forms and the IDs of the documents they were found on.
        with open("data/sample-output.tsv") as tsv:
            for line in csv.reader(tsv, dialect="excel-tab"):
                entities.append(line)
        
        return entities

    def similar(self, method, threshold, string1, string2):
        link = 0
        score = 0
        if method == 'Exact Matching':
            score = 1 if string1 == string2 else 0
            link = 1 if socre else 0
        elif method == 'Levenshtein':
            score = Levenshtein.ratio(string1, string2)
            link = 1 if score > threshold else 0
        elif method ==  'Sequence Matching':
            score = difflib.SequenceMatcher(None, string1, string2).ratio()
            link = 1 if score > threshold else 0
        elif method == 'Sorensen':
            score = 1 - distance.sorensen(string1, string2) 
            link = 1 if score > threshold else 0
        elif method == 'Jaccard':
            score = 1 - distance.jaccard(string1, string2)
            link = 1 if score > threshold else 0
        
        if link:
            return link, score 
        else: 
            return None, None
    
    def local_kdb_file_linking(self, entity, file, method, threshold = None):
        # Open local KDB file
        with open("data/sample-labels-cheat.txt") as tsv:
            # Extract the candidate entities from the KDB together with their Freebase entity IDs and similarity score
            entity_candidates = []
            for line in csv.reader(tsv, dialect="excel-tab"):
                link, score = self.similar(method, entity, line[0], threshold)
                if link:
                    entity_candidates.append(line.append(score))
        # Get entity with highest score by sorting on ascending order
        entity_candidates.sort(key=lambda x: x[3])
        # Return Freebase ID
        return entity_candidates[-1][1]
    
    def search_freebase(self, query):
        return self.search(self.DOMAIN, query)
                    
                        