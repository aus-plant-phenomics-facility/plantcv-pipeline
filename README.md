# plantcv-pipeline
PlantCV Docker pipeline scratch space

# Pre-reqs
* Docker
* Nextflow

# Build Docker Image
* `git clone https://github.com/aus-plant-phenomics-facility/plantcv.git` (note: differences here are including paramiko and psycopg2 in the containter to be able to communicate with LemnaTec database and image store.)
* `docker build plantcv -t="appf/plantcv"`

# install Nextflow.io
* `curl -s https://get.nextflow.io | bash`
* https://www.nextflow.io/docs/latest/getstarted.html

# Run
* `cd plantcv-pipeline`
* `nextflow script.nf -resume --image_limit 10`

##Optional:

# Citation
* Fahlgren N, Feldman M, Gehan MA, Wilson MS, Shyu C, Bryant DW, Hill ST, McEntee CJ, Warnasooriya SN, Kumar I, Ficor T, Turnipseed S, Gilbert KB, Brutnell TP, Carrington JC, Mockler TC, Baxter I. (2015) A versatile phenotyping system and analytics platform reveals diverse temporal responses to water availability in Setaria. Molecular Plant 8: 1520-1535. http://doi.org/10.1016/j.molp.2015.06.005
