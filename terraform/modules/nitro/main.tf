provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "nitro" {
  ami               = "ami-0dfcb1ef8550277af"
  instance_type     = "c5a.xlarge"
  key_name          = var.key_pair_name
  security_groups   = [aws_security_group.nitro.name]


  tags = {
    Name = var.instance_name
  }

  enclave_options {
    enabled = true
  }
}

resource "aws_security_group" "nitro" {
  name = "${var.instance_name}-security-group"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }
}

