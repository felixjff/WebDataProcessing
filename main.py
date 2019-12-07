#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entity recognition
"""

# Import entity linking class with methods
from EntityLinkingClass import EntityLinking

# Define record ID element
record_attribute = 'WARC-TREC-ID'

# Initialize entity linking object
entity_linking = EntityLinking()

# Parse all records in warc file by removing html tags and headers.
parsed_warc = entity_linking.parse_warc('data/recomp.warc.gz', record_attribute)

# Initialize the tagger to be used.
entity_linking.initialize_tagger('StanfordNERTagger')

# Loop over records and extract entities
for r in parsed_warc:
    # tokenize web page content
    tokenized_record = entity_linking.tokenize(r[1])
    # use tagger to categorize tokens
    categorized_record = entity_linking.categorize(tokenized_record)
    # extract entities discovered by tagger within the record
    entities = entity_linking.extract_entities(r[0], categorized_record)
    # store entities 
    entity_linking.store_entities(entities)