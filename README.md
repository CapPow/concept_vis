# concept_vis
CLI tool for taxonomic concept visualization

# example usage
```
# clone this repo
git clone https://github.com/CapPow/concept_vis

# create a new virtual python environment
python3 -m venv .venv

# activate the virtual environment (this command works in bash, windows would be different)
source .venv/bin/activate

# install the repo's requirements
pip install -r requirements.txt

# check the CLI's optional paramaters
python concept_vis.py --help

# run the program using the Concepts feature
python concept_vis.py "./data/TRIUC_Occurrence_Level_Concept_Variation.csv" "output.png" "Concepts"
