#!/usr/bin/env bash

set -e

if [ "$#" -ne 3 ]; then
    echo "Usage: up.sh <instance_name> <key_pair_name> <key_file>"
    exit 1
fi

instance_name="$1"
key_pair_name="$2"
key_file="$3"

terraform -chdir=terraform init
terraform -chdir=terraform plan \
    -var="nitro_dev_instance_name=${instance_name}" \
    -var="nitro_dev_key_pair_name=${key_pair_name}"
terraform -chdir=terraform apply \
    -var="nitro_dev_instance_name=${instance_name}" \
    -var="nitro_dev_key_pair_name=${key_pair_name}"
ansible-playbook \
    --key-file "${key_file}" \
    -i ansible/inventories/dev.yml \
    -e ip=$(terraform -chdir=terraform output nitro_dev_instance_ip) \
    ./ansible/playbooks/init-nitro.yml


