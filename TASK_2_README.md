# Task 2 Missingness - Health Data Detectives

## Overview
This project assesses the effects of different levels and types of missingness in step count data on the performance of a model to classify patients into one of three clusters representing recovery trajectory after a knee replacement operation.

## Requirements

An `environment.yml` file has been created for you; to install virtual environment from the file, run `conda env create -f environment.yml`. Alternatively you could manually download the following package: 

Python >= 3.8
NumPy
Pandas
Matplotlib
PyTorch
Seaborn
SKLearn


## Contents

`real_data_svgplmc_experiment.py`: source code file; do not run
`HRFH_analysis.py`: main analysis Python script

`data/HRFH_experiment/`: default data storage directory

## Run 
The script must be run under the same Conda virtual environment (see above) or another environment with same/similar package configuration. 
After the environment is activated (ie. `conda activate hrfh-task2`), run `python HRFH_analysis.py` for a demo with 250 training patient trajectories, and 3 test patient trajectories of the same patient but different levels of missingness. 
To run the script on your own data, modify parameters specified in `params.yaml` and run `python HRFH_analysis.py --params params.yaml`. Please read comments inside the example `params.yaml` for what each parameter stands for. 

## Output
The model will produce under `HRFH_extval_outputs` a new directory containing the analysis result, including a plot visualisation of the latent embedding generated from the GPLMC, and a simple heatmap showing the result of a simple MLP classifier being fitted on the test data and training data. 

The model will also output `W_train.csv` and `W_test.csv` which are latent embeddings corresponding to train and test patients from the GPLMC model. The user can use these files for any subsequent downstream analysis task as they see fit. 
