#!/bin/bash
#SBATCH -p standard 
#SBATCH -N 1
#SBATCH --ntasks-per-node=28
#SBATCH --time=12:00:00
#SBATCH --mem=57gb

IMG=pipelines_v2.sif
INPUT=rec-ori.tar.gz

# some debug info
hostname
date
pwd
env | grep SLURM

#SCRATCH  dir
export SCRATCH=/tmp/lustre/bolen/tmp/$SLURM_JOBID
mkdir -p $SCRATCH
ls -alh $SCRATCH

export TMP=$SCRATCH
export TMPDIR=$SCRATCH
export TEMP=$SCRATCH
export TEMPDIR=$SCRATCH


export SINGULARITY_TMPDIR=$SCRATCH/CONTAINERTMP
export SINGULARITY_CACHEDIR=$SCRATCH/CONTAINERCACHE
mkdir -p $SINGULARITY_TMPDIR
mkdir -p $SINGULARITY_CACHEDIR
ls -alh $SCRATCH


# copy files / scripts to scratch
cd $SLURM_SUBMIT_DIR
cp $SLURM_SUBMIT_DIR/$IMG $SCRATCH/
cp $SLURM_SUBMIT_DIR/workload.sh  $SCRATCH/

# cd  $SCRATCH/
cd  $SCRATCH/

# some dirs for container
mkdir  -p temp
mkdir  -p temp/input
mkdir  -p temp/output

cp $SLURM_SUBMIT_DIR/$INPUT $SCRATCH/temp/input/
cd temp/input/
tar -zxvf $INPUT

cd $SCRATCH/
# check $SCRATCH 
echo " SCRATCH : $SCRATCH looks like that :" 
pwd
ls -alh

# some TMP inside container mumbo-jumbo
export SINGULARITYENV_TMPDIR="/temp"
export SINGULARITYENV_TEMPDIR="/temp"
export SINGULARITYENV_TMP="/temp"

# cp workload to /temp insinde container 
cp workload.sh ./temp/
echo "launch container ..."
singularity exec  -B $SCRATCH/temp:/temp:rw pipelines_v2.sif ls -alllhR /temp
singularity exec  -B $SCRATCH/temp:/temp:rw  pipelines_v2.sif /temp/workload.sh

echo "after workload ..."

# copy output somwhere ... ?
# cp -r RDF_DIR $SLUMR_SUBMIT_DIR/

# clean all the mess :
cd $SLURM_SUBMIT_DIR
# rm -rf $SCRATCH

