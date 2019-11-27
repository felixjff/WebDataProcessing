# Install spacy:
pip install -U spacy
python -m spacy download en_core_web_sm

# Recompress warc file:
warcio recompress path/to/file path/to/new_file