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

To get started, fork and clone the repo.

Next, you will want to crate a configuration for the infrastructure that
you would like to run.  To do so, create a file `terraform/main.tf` that
describes your development infrastructure.  For example,
my `main.tf` looks like this:

```hcl
module "nitro_dev" {
  source = "./modules/nitro"
  instance_name = "dlm-terraform-test"
  key_pair_name = "dlm-dev"
}

output "nitro_dev_instance_ip" {
  description = "The public IP address of the instance"
  value       = module.nitro_dev.instance_public_ip
}
```

For the "key_pair_name", you will need to have a key pair already created in
AWS and the private key on your local machine.  Below, we will refer to the
location of this key on your local machine as `<path-to-your-pem-file>`.

You will likely want to create an output with the ip address of the
instance that is created so that you can use it later in ansible playbooks.

Let's create the infrastructure.

```bash
cd terraform
terraform init
terraform plan -out tfplan
terraform apply tfplan
```

Upon successful completion of the `apply` you will see the ip address of the
instance that was created. You can copy it for later or put it into an
environment variable like so:

```bash
ip=$(terraform output nitro_dev_instance_ip)
```

Also, if you hop over to the aws console, you will see that your instance is
deployed. You can also get the ip address from the console. Either way, let's
clean up the plan we used and move on to the next step.

```bash
rm tfplan
cd ..
```

Let's use our `init-nitro` playbook to minimally set up a system.

```bash
ansible-playbook \
    -i ansible/inventories/dev.yml \
    -e ip=$ip \
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



