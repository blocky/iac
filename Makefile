key_file = "~/.ssh.dlm/bky-aws_dlm-dev.pem"
instance_name = "dlm-terraform-test"
key_pair_name = "dlm-dev"

up:
	./bin/up.sh $(instance_name) $(key_pair_name) $(key_file)

down:
	./bin/down.sh $(instance_name) $(key_pair_name)

.PHONY: up down
