# NED

NED is short for Newman's Environment for Development and is a nod to the
great computer programmer Dennis Nedry.

This project is a tool for helping with setting up development and test
environments for Newman specifically on AWS and maybe other cloud providers
in the future.

## Getting started

This tool is intended to help you manage your own development environment(s)
and not be used for managing standing infrastructure.  As such, you will
probably want to fork this repo, make it your own, and maybe contribute some
tools back if they are more generally useful.

It uses:
- [terraform](https://www.terraform.io/) (tested with v 1.9.3)
- [ansible](https://www.ansible.com/) (tested with v 2.10.8)

To get started, fork and clone the repo.

Next, you will want to create a configuration for the infrastructure that
you would like to run.  To do so, create a file `terraform/main.tf` that
describes your development infrastructure.  A good starting point
for a `main.tf` is:

```hcl
terraform {
  required_version = ">= 1.7.0"
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "5.58.0"
    }
  }
}

provider "aws" {
  # Note: Not all nitro-enabled instance types or amis are available in all regions. For now, use `us-east-1` to ensure compatibility with the module.
  region = "us-east-1"
}

# You can change the name of the module to be unique if you include multiple instances of this module in your main.tf file.
module "nitro_dev" {
  source = "./modules/nitro"

  # Change the following to your own values
  instance_name = "an-instance-name"
  key_pair_name = "your-key-pair-name"
}

output "nitro_dev_instance_ip" {
  description = "The public IP address of the instance"
  value = module.nitro_dev.instance_public_ip
}
```

For the "key_pair_name", you will need to have a key pair already created in
AWS and the private key on your local machine.  Below, we will refer to the
location of this key on your local machine as `<path-to-your-pem-file>`.

You will likely want to create an output with the ip address of the
instance that is created so that you can use it later in Ansible playbooks.

Let's create the infrastructure.

```bash
cd terraform
terraform init
terraform validate
terraform apply
```

Upon successful completion of the `apply` you will see the ip address of the
instance that was created. You can copy it for later or put it into an
environment variable like so:

```bash
instance_ip=$(terraform output -raw nitro_dev_instance_ip)
```

Also, if you hop over to the aws console, you will see that your instance is
deployed. You can also get the ip address from the console. Either way, let's
move on to the next step.

```bash
cd ..
```

Let's use our `init-nitro` playbook to minimally set up a system.

```bash
ansible-playbook \
    -i ansible/inventories/dev.yml \
    -e ip=$instance_ip \
    --key-file <path-to-your-pem-file> \
    ./ansible/playbooks/init-nitro.yml
```

Personally, I like to use the nix package manager in my development
environments.  If you would like to use nix, you can run the following playbook.

```bash
ansible-playbook \
    -i ansible/inventories/dev.yml \
    -e ip=$ip \
    --key-file <path-to-your-pem-file> \
    ./ansible/playbooks/init-nix.yml
```

Now, you can ssh into the instance and start hacking away on your project
with nitro.

```bash
ssh -i <path-to-your-pem-file> ec2-user@$ip
```

## Cleaning up

Once you are done, please remember to clean up your infrastructure.

```bash
cd terraform
terraform destroy
```



