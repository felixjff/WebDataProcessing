#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entity recognition
"""

from EntityParsingClass import EntityParsing

record_attribute = 'WARC-TREC-ID'

entity_parsing = EntityParsing()

parsed_warc = entity_parsing.parse_warc('data/recomp.warc.gz', record_attribute)

entity_parsing.initialize_tagger('StanfordNERTagger')
for r in parsed_warc:
    tokenized_record = entity_parsing.tokenize(r[1])
    categorized_record = entity_parsing.categorize(tokenized_record)
    entities = entity_parsing.extract_entities(r[0], categorized_record)
    entity_parsing.store_entities(entities)
print()