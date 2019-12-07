### you need to give this file permission with: chmod +x namefile.sh
echo "--- START SETUP:\n"

echo "SETUP: load gcc/6.4.0\n"
module load gcc/6.4.0

echo "SETUP: load python, install numpy, export path"
module load python/3.5.2
pip3 install numpy --upgrade --user
export PYTHONPATH=/home/jurbani/trident/build-python

echo "SETUP: setup trident import and db path"
python3 -c 'import trident'
python3 -c '#db = trident.Db("/home/jurbani/data/motherkb-trident")'

echo "--- SETUP DONE    "



echo "Starting to recognize and link all the entities in 'data/sample.warc.gz'. The results are stored in sample_predictions.tsv"
python3 starter-code.py data/sample.warc.gz > sample_predictions.tsv

echo "Comparing the links stored in sample_predictions.tsv vs. a gold standard ..."
python3 score.py data/sample.annotations.tsv sample_predictions.tsv
