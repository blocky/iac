variable "instance_name" {
  description = "The name of the instance"
  type        = string
}

variable "key_pair_name" {
  description = "The name of the key pair in AWS. This key pair must exist in the region you are deploying to."
  type        = string
}
