# NED

A tool for setting up nitro on AWS

## Setting up for development

Following [this
guide](https://ealizadeh.com/blog/guide-to-python-env-pkg-dependency-using-conda-poetry),
this project uses Conda for environment management, pip as the package
installer, and Poetry as the dependency manager.

Install [Miniconda3](https://docs.conda.io/en/latest/miniconda.html#linux-installers).

    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    bash Miniconda3-latest-Linux-x86_64.sh

Install [Mamba](https://github.com/mamba-org/mamba) to speed up environment building

    conda install mamba -n base -c conda-forge

From the base environment, create and activate (update) a Python environment
specified in `environment.yaml`

    mamba env update -n bky-iac -f environment.yaml
    conda activate bky-iac

Install all the python dependencies

    poetry install

Make sure that everything is set up properly for development by running:

    make test

When you want to clean up run:

    conda deactivate
    conda remove -n sequencer --all
    make veryclean

While you can run unit tests without configuring the NED, you will need to
[Configure NED](#configuring-iac) to run `make test-live` (live tests) or use the
application.

<a name="configuring-iac"></a>
###  Configuring NED


To set up, first, we will need a place to store NED secrets.  Let's put that in our
home directory.

    mkdir -p $HOME/secrets/iac

Next, you will need AWS credentials in a CSV. (Creating credentials for Amazon
is well documented online or ask internally if you need a hand.) Here, we will
assume the file is called `aws--bob-dev.csv`.  Put the creds file in your
secrets folder (but not necessarily the NED secrets folder).  For example:

    mv <wherever-file-was> $HOME/secrets/aws--bob-dev.csv

Go to the NED project root and create a config on your system.  (Note that you
may need to create some folders):

    mkdir -p $HOME/.config/bky/iac
    python -m ned config > $HOME/.config/bky/ned/config.toml

Be default, NED will look for the config file in
`$HOME/.config/bky/ned/config.toml`.
If you want to place the config in a different directory, you can set that location
through in the environment variable `BKY_NED_CONFIG_FILE`.

In the config file, set the variables. I like to set these values
with some info that will help me if I am looking in the aws console. For
example, since this is the sequencer dev server for bob-dev, I would use (note
that the values do not need to be the same nor do they need to be different.):

    # Assuming that $HOME is "/home/bob"

    [ned.aws]
    cred_file = /home/bob/secrets/aws--bob-dev.csv
    secrets_folder = /home/bob/secrets/ned/
    instance_name = "seq-dev--bob-dev"
    key_name = "seq-dev--bob-dev"
    region = "us-east-1"
    security_group = "mwittie-testing"

A few things to note, the values for `cred_file` and `secrets_foler` must be an
absolute paths. The value for `region` should be `us-east-1`. (Other regions may
work, however, this project uses a specific instance type that is not available
in all regions.) *WARNING* It is assumed that the security group is already
created and configured properly. The value "mwittie-testing" works but card
[BKY-2779](https://blocky.atlassian.net/browse/BKY-2779) will add functionality
to set up security groups with code.

## Using NED

The `iac` command provides (opinionated) tools for Nitro Enclave
Deployment (NED).  Some tools including key management, DNS, and
setup/teardown of
EC2 Nitro infrastructure.  If you only want to use the tool, you should
still setup the config and secrets as described in the previous section. You can
can install `iac` locally by running the following commands from the root
directory.

    poetry build
    pip install .

And if all goes well, familiarize yourself with the command

    ned --help

Create an EC2 instance described in the config file

    ned key create
    ned instance create

See installed infrastructure

    ned key list
    ned instance list

Tear down the infrastructure

    ned key delete
    ned instance terminate

And you can even run the project's live tests using the installed version!

    pytest --pyiac="iac" tests/live
