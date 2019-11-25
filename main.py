#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entity recognition
"""

from EntityLinkingClass import EntityLinking

record_attribute = 'WARC-TREC-ID'

entity_linking = EntityLinking()

parsed_warc = entity_linking.parse_warc('data/recomp.warc.gz', record_attribute)

entity_linking.initialize_tagger('StanfordNERTagger')
for r in parsed_warc:
    tokenized_record = entity_linking.tokenize(r[1])
    categorized_record = entity_linking.categorize(tokenized_record)
    entities = entity_linking.extract_entities(r[0], categorized_record)
    entity_linking.store_entities(entities)