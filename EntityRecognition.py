#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entity recognition workflow
"""

# Import entity linking class with methods
from WebDataProcessing import EntityRecognition

# Define record ID element
record_attribute = 'WARC-TREC-ID'

# Initialize entity linking object
entity_recognition = EntityRecognition()

# Parse all records in warc file by removing html tags and headers.
parsed_warc = entity_recognition.parse_warc('data/recomp.warc.gz', record_attribute)

# Initialize the tagger to be used.
entity_recognition.initialize_tagger('StanfordNERTagger')

# Loop over records and extract entities
for r in parsed_warc:
    # tokenize web page content
    tokenized_record = entity_recognition.tokenize(r[1])
    # use tagger to categorize tokens
    categorized_record = entity_recognition.categorize(tokenized_record)
    # extract entities discovered by tagger within the record
    entities = entity_recognition.extract_entities(r[0], categorized_record)
    # store entities 
    entity_recognition.store_entities(entities)