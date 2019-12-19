#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entity Recognition class
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
                        soup = BeautifulSoup(html, "lxml")
                        data = [t for t in soup.find_all(text=True) if t.parent.name not in ['style', 'script', '[document]', 'head']]
                        result = "".join(data)
                        result = result.encode('ascii', errors="ignore").decode('ascii') # Removing all strange characters like emojis
                        result = " ".join(result.split())
                        if len(result) > 0:
                            html_pages_array.append([record_id, str(result)])
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
    
    def is_tweet_element(self, text):
        if text in ['RT', 'tweet', 'AddThis', 'Button', 'BEGIN', 'Share', '|', 'END', 'A', 'Reply']:
            return True
        if 'RT' in text:
            return True
        if '@' in text:
            return True
        if '#' in text:
            return True
        return False
    
    def is_lexical(self, text):
        non_lexical = ["=", "/", "<", ">", ".", '^', '!', '[', ']', '$', '#', '%', '*', '(', ')', '+', '_', '~']
        for i in non_lexical:
            if i in text:
                return False
        return True
    
    def is_word(self, text):
        return len(text) >= 3
    
    def get_context(self, string, mention, n) :
        lh, _, rh = string.partition(mention)
        return ' '.join(lh.split()[-n:]+[mention]+rh.split()[:n])
    
    def extract_entities(self, record_id, tagged_text, original_text, spacy_ents = True):
        entity_list = []
        if self.tagger == 'spacy':
            # By default use the statistical model trained by spacy and the entities thereof.
            if spacy_ents:
                entities = tagged_text.ents
                for e in entities:
                    if self.is_word(str(e)) and not self.is_tweet_element(str(e)) and e.label_ not in ['DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL', 'CARDINAL']:
                        entity_list.append((record_id, e, e.label_, self.get_context(original_text, str(e), 3)))
            else:
                for tupple in tagged_text:
                    if tupple.tag_ == 'NNP':
                        if not self.is_tweet_element(tupple.text) and self.is_lexical(tupple.text) and self.is_word(tupple.text):
                            entity_list.append((record_id, tupple.text, tupple.tag_))
        else:
            for tupple in tagged_text:
                entity_list.append((record_id, tupple[0], tupple[1]))
        return entity_list
        
    def store_entities(self, output):
        with open('intermediate-output.tsv', 'a', newline='') as myfile:
            for e in output:
                try:
                    myfile.write(str(e[0]) + "\t" + str(e[1]) + "\t" + str(e[2]) + "\t{" + str(e[3]) + "}\n")
                except Exception as e:
                    print(e)