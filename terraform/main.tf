variable "nitro_dev_instance_name" {
  description = "The name of the dev instance"
  type       = string
}

variable "nitro_dev_key_pair_name" {
  description = "The name of the key pair"
  type        = string
}

module "nitro_dev" {
  source = "./modules/nitro"
  instance_name = var.nitro_dev_instance_name
  key_pair_name = var.nitro_dev_key_pair_name
}

output "nitro_dev_instance_ip" {
  description = "The public IP address of the instance"
  value       = module.nitro_dev.instance_public_ip
}

