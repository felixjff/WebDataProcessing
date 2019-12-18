this needs to be in the run.sh thingy

module load python/3.5.2
module load gcc/6.4.0
pip3 install numpy --upgrade --user
export PYTHONPATH=/home/jurbani/trident/build-python


in python3
import trident
db = trident.Db("/home/jurbani/data/motherkb-trident")
results = db.sparql("SELECT * { ?s ?p ?o .} LIMIT 10")
print(results)

# MAYBE YOU NEED PIP3
# For parsing:
pip install lxml
# Install spacy:
pip install -U spacy
python -m spacy download en_core_web_sm

# Recompress warc file:
warcio recompress path/to/file path/to/new_file

# for linking:
pip install python-Levenshtein
pip install Distance
pip install python-csv