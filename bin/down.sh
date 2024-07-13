#!/usr/bin/env bash

set -e

if [ "$#" -ne 2 ]; then
    echo "Usage: up.sh <instance_name> <key_pair_name>"
    exit 1
fi

	terraform -chdir=terraform destroy \
		-var="nitro_dev_instance_name=${instance_name}" \
		-var="nitro_dev_key_pair_name=${key_pair_name}"


