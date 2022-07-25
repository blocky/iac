# Sequencer

BLOCKY Sequencer implements a trusted sequencer service as describe in
the ZipperChain white paper.

## Setting up for development

Following [this
guide](https://ealizadeh.com/blog/guide-to-python-env-pkg-dependency-using-conda-poetry)
the Sequencer uses Conda for environment management, pip as the package
installer, and Poetry as the dependency manager.

Install [Miniconda3](https://docs.conda.io/en/latest/miniconda.html#linux-installers).

    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    bash Miniconda3-latest-Linux-x86_64.sh

Install [Mamba](https://github.com/mamba-org/mamba) to speed up environment building

    conda install mamba -n base -c conda-forge

From the base environment,
create and activate (update) a Python environment specified in `environment.yaml`

    mamba env update -n sequencer -f environment.yaml
    conda activate sequencer

Install all the python dependencies

    poetry install

Setup testing for a local development server

    make config

Note that this will generate some files, but those files should NOT be added to
git (they are already in the .gitignore). Check out the config for some helpful
development tools.

Make sure that everything is set up properly for development by running:

    make test

For more on testing see [testing](#testing).  When you want to clean up run:

    conda deactivate
    conda remove -n sequencer --all
    make veryclean

### Configuring iac

*Note you can skip these steps, but, you will not be able to use the `iac`
commands or successfully pass all of the live tests.

To setup, first, you will need AWS credentials in a CSV. (Creating credentials
for Amazon is well documented online or ask internally if you need a hand.)
Here, we will assume the file is called `aws--bob-dev.csv`.  Put the creds file
in the `secrets` folder

    mv <wherever-file-was> secrets/aws--bob-dev.csv

Copy the sample config over to a config that will be used on your system

    cp setup/sample.toml setup/config.toml

In the config file set the variables. I like to set these values
with some info that will help me if I am looking in the aws console. For
example, since this is the sequencer dev server for bob-dev, I would use (note
that the values do not need to be the same nor do they need to be different.):

    [iac.aws]
    cred_file = "aws--bob-dev.csv"
    instance_name = "seq-dev--bob-dev"
    key_name = "seq-dev--bob-dev"
    region = "us-east-1"
    security_group = "mwittie-testing"

A few things to note, the value for `cred_file` needs to be the name of your
credential file in the `secrets` folder. The value for `region` should be
`us-east-1`. (Other regions may work, however, this project uses a
specific instance type that is not available in all regions.) *WARNING* It is
assumed that the security group is already created and configured properly. The
value "mwittie-testing" works but card
[BKY-2779](https://blocky.atlassian.net/browse/BKY-2779) will add functionality
to set up security groups with code.


### Updating dependencies

*Warning This section is important, please read carefully.*

This project uses caches in the bitbucket pipelines to reduce the time of
setting up dependencies.  If you change the dependencies (`environment.yaml` or
`poetry.lock`), you should make sure to set up a new cache for your PR (and then
set it back to the standard cache before merging).  To update, open up the
`bitbucket-pipelines.yml` file and add a suffix to the cache.  It is recommended
to use the id of the card that you are working on to the cache definition.  For
example if we are working on card bky-XXX:

    definitions:
      caches:
        conda: /opt/conda/envs

Should change to

    definitions:
      caches:
        conda-bky-XXXX: /opt/conda/envs

Next, update the step definition to clear the cache.  For example:

    - step: &clear-cache
        name: Clear cache
        script:
          - pipe: atlassian/bitbucket-clear-cache:3.1.1
            variables:
              BITBUCKET_USERNAME: $BITBUCKET_USER_NAME
              BITBUCKET_APP_PASSWORD: $BITBUCKET_APP_PASSWORD
              CACHES: [ "conda" ]

Should change to

    - step: &clear-cache
        name: Clear cache
        script:
          - pipe: atlassian/bitbucket-clear-cache:3.1.1
            variables:
              BITBUCKET_USERNAME: $BITBUCKET_USER_NAME
              BITBUCKET_APP_PASSWORD: $BITBUCKET_APP_PASSWORD
              CACHES: [ "conda-bky-XXX" ]


Finally, update any step definition that could uses the cache. For example:

    - step: &install
        name: Install
        caches:
          - conda
        script:
          ...

Should change to

    - step: &install
        name: Install
        caches:
          - conda-bky-XXX
        script:
          ...

Now you are ready to make your updates to the environment.  *Warning*, bitbucket
pipelines will only check the cache update conditions on the change set of the
current commit.  So, make sure to push after each commit in which the files that
encode the dependencies are updated!!

*Reminder* Once you are ready to merge your PR, rename the cache back to
`conda`.

**As an aside**.  If this process becomes problematic, we could use githooks to
automate the creation of the `bitbucket-pipelines.yml` such that every branch
receives its own cache.  Currently, we believe that the added complexity of such
a system is overkill.


## Setting up EC2 Nitro infrastructure

The `iac` command provides the infrastructure as code (IAC) to set up and tear down EC2 Nitro infrastructure.
To familiarize yourself with the command run

    python -m iac --help

The workflow to create an EC2 instance described in the `setup/config.toml` file is

    python -m iac key create
    python -m iac instance create

to see installed infrastructure

    python -m iac key list
    python -m iac instance list

and to tear down the infrastructure

    python -m iac key delete
    python -m iac instance terminate


## Running

To run the Sequencer gateway

    make run

You can access the gateway at http://127.0.0.1:5000/

## Testing <a name="testing"></a>

To run Sequencer unit tests

    make test

You can also execute live Sequencer tests

    make test-live

To check the quality of the code

    make lint
