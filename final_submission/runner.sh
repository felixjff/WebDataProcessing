#!/bin/bash

export PYTHONPATH=/home/jurbani/trident/build-python
echo "----- SETUP: install python modules"
# NLP preprocessing modules
python3 -m pip install warcio --upgrade --user
python3 -m pip install html5lib --upgrade --user
python3 -m pip install bs4 --upgrade --user
python3 -m pip install spacy --upgrade --user
python3 -m spacy download --user en_core_web_sm
python3 -m pip install nltk --upgrade --user
python3 -m pip install lxml --upgrade --user
# Entity recognition modules
python3 -m pip install pyjarowinkler --upgrade --user
python3 -m pip install distance --upgrade --user
# Other modules
python3 -m pip install python-csv --upgrade --user
python3 -m pip install numpy --upgrade --user
echo "----- SETUP DONE    "

rm -f intermediate-output.tsv

python3 main.py $1
~                  