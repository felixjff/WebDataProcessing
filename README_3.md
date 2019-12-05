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




AND IT WORKS BITCH
