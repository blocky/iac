# Sequencer

BLOCKY Sequencer implements a trusted sequencer service as describe in the ZipperChain white paper.

## Installation

Following https://ealizadeh.com/blog/guide-to-python-env-pkg-dependency-using-conda-poetry the Sequencer
uses Conda for environment management, pip as the package installer, and Poetry as the dependency manager.

Install [Miniconda3](https://docs.conda.io/en/latest/miniconda.html#linux-installers). 

	wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
	bash Miniconda3-latest-Linux-x86_64.sh

Install [Mamba](https://github.com/mamba-org/mamba) to speed up environment building

	conda install mamba -n base -c conda-forge

Create and activate (update) a Python environment specified in `environment.yaml`

	mamba env update -n sequencer -f environment.yaml
	conda activate sequencer

Install all the python dependencies

	poetry install

When you want to clean up

    conda deactivate
    conda remove -n sequencer --all
	make veryclean


## Running

To run the Sequencer gateway

    make run

You can access the gateway at http://127.0.0.1:5000/ 


## Testing

To run Sequencer unit tests

    make test

You can also execute live Sequencer tests 

    make test-live

To check the quality of the code

    make lint
