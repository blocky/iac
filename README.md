# Sequencer

BLOCKY Sequencer implements a trusted sequencer service as describe in the ZipperChain white paper.

## Installation

Install [Miniconda3](https://docs.conda.io/en/latest/miniconda.html#linux-installers).

	wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
	bash Miniconda3-latest-Linux-x86_64.sh

Set up a conda environment

	conda create --name bky-seq python=3.10 pip

Activate the environment

	conda activate bky-seq

Install all the python dependencies

	pip install -r requirements.txt

Run the tests with

	make test

Make sure your code passes standard python formatting with

	make lint

When you want to clean up

	conda deactivate
	conda remove -n bky-seq --all
	make veryclean


## Running

To run the Sequencer gateway

	make flask

You can access the gateway at http://127.0.0.1:5000/


## Testing

To run Sequencer unit tests

	make test-unit

You can also execute live Sequencer tests against a running gateway

	make test-live

To check the quality of the code

	make lint
