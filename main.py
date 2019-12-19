#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entity recognition workflow
"""

# Import entity recognition class with methods
from EntityRecognitionClass import EntityRecognition
from EntityLinkingClass import EntityLinking
import time
import concurrent.futures
import threading
import spacy
import sys

start = time.time()
lock = threading.Lock()
afterParse = time.time()
tagger = "spacy"


# For spacy:
def extract_entities2(record):
    try:
        categorized_record = entity_recognition.categorize(record[1])
        entities = entity_recognition.extract_entities(record[0], categorized_record, record[1])
    except Exception as e:
        print(e)
    with lock:
        entity_recognition.store_entities(entities)
    
    print("extracted ",len(entities)," in ",time.time() - afterParse," seconds")
    
# For nlkt and Stanford:
def extract_entities(record):
    # tokenize web page content
    tokenized_record = entity_recognition.tokenize(record[1])
    # use tagger to categorize tokens
    with lock:
        categorized_record = entity_recognition.categorize(tokenized_record)
    # extract entities discovered by tagger within the record
    entities = entity_recognition.extract_entities(record[0], categorized_record)
    # store entities 
    with lock:
        entity_recognition.store_entities(entities)
    print("extracted ",len(entities)," in ",time.time() - afterParse," seconds")
        
# Define record ID element
record_attribute = 'WARC-TREC-ID'

# Initialize entity recognition object
entity_recognition = EntityRecognition()

# Initialize entity linking object
entity_linking = EntityLinking()

# Get command line argument
try:
    filename = sys.argv[1]
except Exception as e:
    print("Argument missing, please supply the path to the warc file!")
    
    

# Parse all records in warc file by removing html tags and headers.
parsed_warc = entity_recognition.parse_warc(filename, record_attribute)
afterParse = time.time()
print("parsed ",len(parsed_warc)," in ",time.time() - start," seconds")

# Initialize the tagger to be used.
entity_recognition.initialize_tagger(tagger) 

with concurrent.futures.ThreadPoolExecutor(max_workers=500) as executor:
    if tagger == "spacy":
        executor.map(extract_entities2, parsed_warc)
    else:
        executor.map(extract_entities, parsed_warc)

end = time.time()
print("end: ",end - start)

single_match, multiple_match, unmatched = entity_linking.get_elasticsearch_candidate_entities()





