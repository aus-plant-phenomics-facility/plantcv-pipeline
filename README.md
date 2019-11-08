# plantcv-pipeline
PlantCV Docker pipeline scratch space

# Pre-reqs
* Docker

# Build Docker Image
* `git clone https://github.com/aus-plant-phenomics-facility/plantcv.git` (note: only difference here is including paramiko and psycopg2 in the containter to be able to communicate with LemnaTec database and image store)
* `docker build plantcv -t="appf/plantcv"`

# Run
* docker run -v "$PWD":/home/joyvan/pcv -v "$HOME"/.ssh/:/home/joyvan/.ssh appf/plantcv python /home/joyvan/pcv/01-query-snapshots.py
* docker run -v "$PWD":/home/joyvan/pcv -v "$HOME"/.ssh/:/home/joyvan/.ssh appf/plantcv python /home/joyvan/pcv/02-analyse-image.py <job_number>
* docker run -v "$PWD":/home/joyvan/pcv -v "$HOME"/.ssh/:/home/joyvan/.ssh appf/plantcv python /home/joyvan/pcv/03-aggregate-results.py

##Optional:
* `./run_pcv_docker.sh` will run step 2 in a loop

# Citation
* Fahlgren N, Feldman M, Gehan MA, Wilson MS, Shyu C, Bryant DW, Hill ST, McEntee CJ, Warnasooriya SN, Kumar I, Ficor T, Turnipseed S, Gilbert KB, Brutnell TP, Carrington JC, Mockler TC, Baxter I. (2015) A versatile phenotyping system and analytics platform reveals diverse temporal responses to water availability in Setaria. Molecular Plant 8: 1520-1535. http://doi.org/10.1016/j.molp.2015.06.005