#!/bin/bash

export PYTHONPATH=/home/jurbani/trident/build-python

# NLP preprocessing modules
python3 -m pip install warcio --upgrade --user --quiet
python3 -m pip install html5lib --upgrade --user --quiet
python3 -m pip install bs4 --upgrade --user --quiet
python3 -m pip install spacy --upgrade --user --quiet
python3 -m spacy download --user en_core_web_sm --quiet
python3 -m pip install nltk --upgrade --user --quiet
python3 -m pip install lxml --upgrade --user --quiet
# Entity recognition modules
python3 -m pip install pyjarowinkler --upgrade --user --quiet
python3 -m pip install distance --upgrade --user --quiet
# Other modules
python3 -m pip install python-csv --upgrade --user --quiet
python3 -m pip install numpy --upgrade --user --quiet

rm -f intermediate-output.tsv
rm -f final-output.tsv

python3 main.py $1