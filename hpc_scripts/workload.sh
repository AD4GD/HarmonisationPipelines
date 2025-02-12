#!/bin/bash

### ACTIVATE pipelines
source activate pipelines
cd /temp
# mkdir src
# cd src
#pwd
cp -r /opt/src  ./
# ls -allhtrR ./ 

### COPY CUSTOM MAPPING
cd /temp/src/cfg/GENERIC
wget https://box.psnc.pl/f/91b5026773/?raw=1 -O spain-REC-official-custom.yaml
wget https://box.psnc.pl/f/bae4288237/?raw=1 -O spain-LD-official-custom.yaml
wget https://box.psnc.pl/f/ff5490a911/?raw=1 -O spain-EP-official-custom.yaml

### CONFIGURE VIRTUOSO
cd /temp/src
wget {url to users .env file} -O .env
cd /temp/src/cfg/
wget {url to the filled config.yaml} -O config.yaml
#### RUN PIPELINE
# sample run
cd /temp/src
time python main.py generic \
--preprocess_activity=unzip_multiple_archives \
--process=preprocess \
--process=mapping \
--process=transform \
--process=postprocess \
--process=load \
--dir_input=/temp/input/rec_ori/ \
--input_type=Shapefile \
--from_config \
--from_config_value=/temp/src/cfg/GENERIC/spain-REC-official-custom.yaml \
--base_uri=http://datos.gob.es/ \
--output=/temp/output/  \
--graph_uri=http://datos.gob.es/lpis/rec/ \
--reload_graph \
--graph_per_dump

