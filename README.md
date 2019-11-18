# plantcv-pipeline
PlantCV Nextflow pipeline using containers. This will connect to a LemnaTec database and image store and run a plantCV pipeline on those images.

# Pre-reqs
* Docker
* Nextflow

# Build modified PlantCV Docker Image
* `git clone https://github.com/aus-plant-phenomics-facility/plantcv.git` (note: differences here are including paramiko and psycopg2 in the containter to be able to communicate with LemnaTec database and image store. The base has also changed to ensure python3)
* `docker build plantcv -t="appf/plantcv"`

# install Nextflow.io
* Instructions here: https://www.nextflow.io/docs/latest/getstarted.html
* `curl -s https://get.nextflow.io | bash`

# Configuration
Check the nextflow.config file for configuration. There are broadly three things:
  * Database Access
  * Image file (server) access
  * LemnaTec specifics (query, measurement labels etc.)

# Usage & Notes on Usage
`nextflow script.nf` run the script with default values.

Anything specified as a nextflow parameter can be modified with a command line argument
* Pass parameters to Workflow with double -- (e.g. --limit, --image_access_method)

Parameters of the Nextflow engine itself can be modified
* Pass instructions to Nextflow with a single - (e.g. -resume, -process.echo)

# Disclaimers/Next Steps
* Query Snapshots and Fetch Image steps can be easily replaced or altered to work with non-LemnaTec image sets. The former creates a job file for each image and the latter fetches the images.

# Citation
* Fahlgren N, Feldman M, Gehan MA, Wilson MS, Shyu C, Bryant DW, Hill ST, McEntee CJ, Warnasooriya SN, Kumar I, Ficor T, Turnipseed S, Gilbert KB, Brutnell TP, Carrington JC, Mockler TC, Baxter I. (2015) A versatile phenotyping system and analytics platform reveals diverse temporal responses to water availability in Setaria. Molecular Plant 8: 1520-1535. http://doi.org/10.1016/j.molp.2015.06.005
