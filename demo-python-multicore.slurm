#!/bin/bash
#SBATCH -n 1
#SBATCH --mem=256000
#SBATCH -t 05:00:00
#SBATCH -o log.out
#SBATCH -p standard
#SBATCH -A sds_sdad

module load anaconda/2020.11-py3.8

pip install --user pandas
pip install --user google-cloud-bigquery
pip install --user pyarrow
python oss_capstone_2021_pypi_meta_downloads_big_query.py 

