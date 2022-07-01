import datetime

import botocore.exceptions
from dateutil.tz import tzutc

key_name = "test-key"
instance_name = "test-instance"
security_group = "test-security-group"
instance_id = "test-instance-id"
exp_exc = Exception()
key_file_name = "/some/path/file.pem"

describe_key_pairs_ret_one_key = {
    "KeyPairs": [
        {
            "CreateTime": datetime.datetime(2022, 6, 10, 22, 8, 3, tzinfo=tzutc()),
            "KeyFingerprint": "f3:2c:c5:9f:b4:41:0d:fe:32:2b:f8:3b:e6:91:f4:91:e3:84:7e:95",
            "KeyName": key_name,
            "KeyPairId": "key-0d8222dcf124df420",
            "KeyType": "rsa",
            "Tags": [{"Key": "Deployment", "Value": "Sequencer"}],
        }
    ],
    "ResponseMetadata": {
        "HTTPHeaders": {
            "cache-control": "no-cache, no-store",
            "content-length": "741",
            "content-type": "text/xml;charset=UTF-8",
            "date": "Fri, 10 Jun 2022 22:27:50 GMT",
            "server": "AmazonEC2",
            "strict-transport-security": "max-age=31536000; " "includeSubDomains",
            "x-amzn-requestid": "c099f5da-57f9-4b5b-9933-b6f95fa55b04",
        },
        "HTTPStatusCode": 200,
        "RequestId": "c099f5da-57f9-4b5b-9933-b6f95fa55b04",
        "RetryAttempts": 0,
    },
}

describe_key_pairs_ret_no_keys = {
    "KeyPairs": [],
    "ResponseMetadata": {
        "HTTPHeaders": {
            "cache-control": "no-cache, no-store",
            "content-length": "221",
            "content-type": "text/xml;charset=UTF-8",
            "date": "Wed, 15 Jun 2022 21:43:30 GMT",
            "server": "AmazonEC2",
            "strict-transport-security": "max-age=31536000; " "includeSubDomains",
            "x-amzn-requestid": "95f8c7c9-6bd4-45f3-8908-bd96f9dd919c",
        },
        "HTTPStatusCode": 200,
        "RequestId": "95f8c7c9-6bd4-45f3-8908-bd96f9dd919c",
        "RetryAttempts": 0,
    },
}

describe_key_pair_exc_key_not_found = botocore.exceptions.ClientError(
    {
        "Error": {
            "Code": "InvalidKeyPair.NotFound",
            "Message": "The key pair 'test-key' does not exist",
        },
        "ResponseMetadata": {
            "HTTPHeaders": {
                "cache-control": "no-cache, no-store",
                "connection": "close",
                "content-type": "text/xml;charset=UTF-8",
                "date": "Fri, 17 Jun 2022 17:10:28 GMT",
                "server": "AmazonEC2",
                "strict-transport-security": "max-age=31536000; " "includeSubDomains",
                "transfer-encoding": "chunked",
                "vary": "accept-encoding",
                "x-amzn-requestid": "51dff490-4bcd-4852-abbb-556b17030447",
            },
            "HTTPStatusCode": 400,
            "RequestId": "51dff490-4bcd-4852-abbb-556b17030447",
            "RetryAttempts": 0,
        },
    },
    "DescribeKeyPair",
)

create_key_pair_res_success = {
    "KeyFingerprint": "3c:b4:a0:cc:96:07:8a:0b:df:c4:be:12:a6:47:f4:eb:a4:89:c6:8d",
    "KeyMaterial": "-----BEGIN RSA PRIVATE KEY-----\n"
    "MIIEowIBAAKCAQEAie85nrBVeHwGh+U7JofCHgw0QO2KvsXrQRvlkUtwVKqk5ww2\n"
    "0JiR5woUTHOthlytsoKnI316j8G8Fc25N45MeACRodMzPoXx2RXJaVQYtTFy4Jk2\n"
    "X0cTmh6DY+rTAjI98s+kU3YrrxBKRbc9WLY1ug0GxZHd/WwvsrIcWZAw8+8qy4OA\n"
    "8iZJgKC4UQ1StoWOsOW8T/F5iOvfia0GdRt95HolDuVvNR0qD9OOhX9xoeNgJrQl\n"
    "129vEhhTtMkN51gYTY+rjZh36akoLmWTtruSLxgzIMfuRsuhI0b/dYlBVCGTTsBk\n"
    "w3GzsyefHSvMaQ4ccny/2g3qSNfC4kckU/HFDQIDAQABAoIBAD1JzpB0SYX/ledM\n"
    "M7wrFlXDlnRDGCMsThvgCWFF4+O67wq6oqCNKkc+c0aFH9VT2No4s4tRdePqcWg+\n"
    "wM2urMuldRAyh9KAMbYDuDrU4yWfkyu46C/tpQgWBsuey6NuL5h0Ks/q8f4Xfuj7\n"
    "Qobob3b70sZ2yeyQ5aDBA1fIeffo5PbheVyLKvXlxKx1UQ4PGD8Wr4N/K3tGHKdH\n"
    "86X6obmbqdwfP701bgmFXG6ik9rcyycGVR/vYi8cEghbzikPyO6lEER3kZ3h18iE\n"
    "6Nypu1shuGkW7M2VA1LWSys+UrLsx+M+AsZo0w14toEN7nFahCZnSSf1a2OONipo\n"
    "752qKQECgYEA1dsS+LduxacGvKnpN0d2zclEX+UnTrVQM8waM4ENQeF4CgnqcL1H\n"
    "lwzvICUl3JMU8XktSVVCdiM5tZ4NOc+s5P6IlbMp1+ls0FsKJq9XDI88K++mor9r\n"
    "pwn813k6byKAkn62ZkwmjzbMFZhRw8TNztLAHta9kHjrG09x5LhlsGcCgYEApR30\n"
    "4/To9g5Xo7iiuPFOjrSUksNGqOf9XAJ0xHvOlrMi/UWaicCCfIPY2EH56XnXqbig\n"
    "NsG2zMeAFZw9CYAOWQTq9osIB+Z28r25g81HDb1sdD+fsiumKHKGGDfdL7iqnRXB\n"
    "FF63gfgIy2b+MAhSZl823aTNphx/1uZkfgCYZmsCgYBE9AUS8rohurAeZr6Ol1lE\n"
    "EvAb51wcMbPxb47HKoYmxtcYjYfs3+rUVlRHzhJ+I2JuVX73lSj/xG3YFGT5Te/W\n"
    "SgeqFQGZ32a5a5FDVefAYfKpy/SzpvrD+iFvLGRd7wb7tSWEqGsKZEW7dMhwUeV2\n"
    "GVfe2ah3i7VqsdvsPlRzYwKBgE726pzyDU9PQJ5tuHRWAsnAlqUxemNgvwv3qLwm\n"
    "sX/kn8EcPnHOfRjrPRL/SnNb78WdJBHLxo5cgmbTV2VptnLgJTZO+0I793rTPRtJ\n"
    "Wse5ZVqa6tachVQmoPaIEOG3oPCK7NG/Eme3pQ0RblKuSCnpMyYAoNDmJEUz3a9c\n"
    "vYWNAoGBAKGM+6kgNCp6VXGaR3SJJy8fgiRYg2uxuzVdtIvYSXRNIPJWP2aNWkde\n"
    "FMGOXUTecOn/zAo5+oJTmBJgiQRCVh2+czEbSygLN4bKBZYW7md9VUXNOm1zDNBX\n"
    "uk4FCr7KhAqjITK9qbeq605+ZDWX5gnzx8GbJrNg+z8MweGhBpY4\n"
    "-----END RSA PRIVATE KEY-----",
    "KeyName": "test-key",
    "KeyPairId": "key-0aa95b83e9d35aea0",
    "ResponseMetadata": {
        "HTTPHeaders": {
            "cache-control": "no-cache, no-store",
            "content-length": "2085",
            "content-type": "text/xml;charset=UTF-8",
            "date": "Wed, 15 Jun 2022 22:13:38 GMT",
            "server": "AmazonEC2",
            "strict-transport-security": "max-age=31536000; " "includeSubDomains",
            "vary": "accept-encoding",
            "x-amzn-requestid": "52b179da-c4c9-4d17-9719-3dddcd098825",
        },
        "HTTPStatusCode": 200,
        "RequestId": "52b179da-c4c9-4d17-9719-3dddcd098825",
        "RetryAttempts": 0,
    },
}

create_key_pair_exception = botocore.exceptions.ClientError(
    {
        "Error": {
            "Code": "InvalidKeyPair.Duplicate",
            "Message": "The keypair 'test-key' already exists.",
        },
        "ResponseMetadata": {
            "HTTPHeaders": {
                "cache-control": "no-cache, " "no-store",
                "connection": "close",
                "content-type": "text/xml;charset=UTF-8",
                "date": "Wed, 15 Jun 2022 " "23:16:19 GMT",
                "server": "AmazonEC2",
                "strict-transport-security": "max-age=31536000; " "includeSubDomains",
                "transfer-encoding": "chunked",
                "vary": "accept-encoding",
                "x-amzn-requestid": "3ce34749-beb1-45dd-b0b2-f74532c303a9",
            },
            "HTTPStatusCode": 400,
            "RequestId": "3ce34749-beb1-45dd-b0b2-f74532c303a9",
            "RetryAttempts": 0,
        },
    },
    "CreateKeyPair",
)

describe_instances_ret_one_instance = {
    "Reservations": [
        {
            "Groups": [],
            "Instances": [
                {
                    "AmiLaunchIndex": 0,
                    "Architecture": "x86_64",
                    "BlockDeviceMappings": [
                        {
                            "DeviceName": "/dev/xvda",
                            "Ebs": {
                                "AttachTime": datetime.datetime(
                                    2022, 6, 17, 22, 29, 21, tzinfo=tzutc()
                                ),
                                "DeleteOnTermination": True,
                                "Status": "attaching",
                                "VolumeId": "vol-09bc192718d391e04",
                            },
                        }
                    ],
                    "CapacityReservationSpecification": {"CapacityReservationPreference": "open"},
                    "ClientToken": "82cd14d0-a043-4689-8ba5-e3c83e787dc9",
                    "CpuOptions": {"CoreCount": 2, "ThreadsPerCore": 2},
                    "EbsOptimized": False,
                    "EnaSupport": True,
                    "EnclaveOptions": {"Enabled": True},
                    "HibernationOptions": {"Configured": False},
                    "Hypervisor": "xen",
                    "ImageId": "ami-08e4e35cccc6189f4",
                    "InstanceId": instance_id,
                    "InstanceType": "c5a.xlarge",
                    "KeyName": key_name,
                    "LaunchTime": datetime.datetime(2022, 6, 17, 22, 29, 20, tzinfo=tzutc()),
                    "MaintenanceOptions": {"AutoRecovery": "default"},
                    "MetadataOptions": {
                        "HttpEndpoint": "enabled",
                        "HttpProtocolIpv6": "disabled",
                        "HttpPutResponseHopLimit": 1,
                        "HttpTokens": "optional",
                        "InstanceMetadataTags": "disabled",
                        "State": "pending",
                    },
                    "Monitoring": {"State": "disabled"},
                    "NetworkInterfaces": [
                        {
                            "Association": {
                                "IpOwnerId": "amazon",
                                "PublicDnsName": "ec2-3-235-31-42.compute-1.amazonaws.com",
                                "PublicIp": "3.235.31.42",
                            },
                            "Attachment": {
                                "AttachTime": datetime.datetime(
                                    2022, 6, 17, 22, 29, 20, tzinfo=tzutc()
                                ),
                                "AttachmentId": "eni-attach-0a516ae4f2e444428",
                                "DeleteOnTermination": True,
                                "DeviceIndex": 0,
                                "NetworkCardIndex": 0,
                                "Status": "attaching",
                            },
                            "Description": "",
                            "Groups": [
                                {
                                    "GroupId": "sg-0e20fb2c07aa618f0",
                                    "GroupName": "zpr-lts",
                                }
                            ],
                            "InterfaceType": "interface",
                            "Ipv6Addresses": [],
                            "MacAddress": "16:aa:78:5d:a4:e7",
                            "NetworkInterfaceId": "eni-07f17649d4afd24c6",
                            "OwnerId": "233808678534",
                            "PrivateDnsName": "ip-172-31-51-34.ec2.internal",
                            "PrivateIpAddress": "172.31.51.34",
                            "PrivateIpAddresses": [
                                {
                                    "Association": {
                                        "IpOwnerId": "amazon",
                                        "PublicDnsName": "ec2-3-235-31-42.compute-1.amazonaws.com",
                                        "PublicIp": "3.235.31.42",
                                    },
                                    "Primary": True,
                                    "PrivateDnsName": "ip-172-31-51-34.ec2.internal",
                                    "PrivateIpAddress": "172.31.51.34",
                                }
                            ],
                            "SourceDestCheck": True,
                            "Status": "in-use",
                            "SubnetId": "subnet-d95b9cd7",
                            "VpcId": "vpc-a76039dd",
                        }
                    ],
                    "Placement": {
                        "AvailabilityZone": "us-east-1f",
                        "GroupName": "",
                        "Tenancy": "default",
                    },
                    "PlatformDetails": "Linux/UNIX",
                    "PrivateDnsName": "ip-172-31-51-34.ec2.internal",
                    "PrivateDnsNameOptions": {
                        "EnableResourceNameDnsAAAARecord": False,
                        "EnableResourceNameDnsARecord": False,
                        "HostnameType": "ip-name",
                    },
                    "PrivateIpAddress": "172.31.51.34",
                    "ProductCodes": [],
                    "PublicDnsName": "ec2-3-235-31-42.compute-1.amazonaws.com",
                    "PublicIpAddress": "3.235.31.42",
                    "RootDeviceName": "/dev/xvda",
                    "RootDeviceType": "ebs",
                    "SecurityGroups": [{"GroupId": security_group, "GroupName": "some-name"}],
                    "SourceDestCheck": True,
                    "State": {"Code": 0, "Name": "pending"},
                    "StateTransitionReason": "",
                    "SubnetId": "subnet-d95b9cd7",
                    "Tags": [
                        {"Key": "Deployment", "Value": "Sequencer"},
                        {"Key": "Name", "Value": instance_name},
                    ],
                    "UsageOperation": "RunInstances",
                    "UsageOperationUpdateTime": datetime.datetime(
                        2022, 6, 17, 22, 29, 20, tzinfo=tzutc()
                    ),
                    "VirtualizationType": "hvm",
                    "VpcId": "vpc-a76039dd",
                }
            ],
            "OwnerId": "233808678534",
            "ReservationId": "r-08ae3905085844e09",
        }
    ],
    "ResponseMetadata": {
        "HTTPHeaders": {
            "cache-control": "no-cache, no-store",
            "content-type": "text/xml;charset=UTF-8",
            "date": "Fri, 17 Jun 2022 22:29:23 GMT",
            "server": "AmazonEC2",
            "strict-transport-security": "max-age=31536000; " "includeSubDomains",
            "transfer-encoding": "chunked",
            "vary": "accept-encoding",
            "x-amzn-requestid": "af3ee9a9-1e82-4118-a051-50d321460977",
        },
        "HTTPStatusCode": 200,
        "RequestId": "af3ee9a9-1e82-4118-a051-50d321460977",
        "RetryAttempts": 0,
    },
}

describe_instances_ret_no_instances = {
    "Reservations": [],
    "ResponseMetadata": {
        "HTTPHeaders": {
            "cache-control": "no-cache, no-store",
            "content-length": "230",
            "content-type": "text/xml;charset=UTF-8",
            "date": "Fri, 17 Jun 2022 23:24:13 GMT",
            "server": "AmazonEC2",
            "strict-transport-security": "max-age=31536000; " "includeSubDomains",
            "x-amzn-requestid": "09206071-57e1-466d-a1e4-9f182b54e0b4",
        },
        "HTTPStatusCode": 200,
        "RequestId": "09206071-57e1-466d-a1e4-9f182b54e0b4",
        "RetryAttempts": 0,
    },
}

run_instances_res_success = {
    "Groups": [],
    "Instances": [
        {
            "AmiLaunchIndex": 0,
            "Architecture": "x86_64",
            "BlockDeviceMappings": [],
            "CapacityReservationSpecification": {"CapacityReservationPreference": "open"},
            "ClientToken": "4c3546ab-cb44-40fb-9572-8cacbde16c8d",
            "CpuOptions": {"CoreCount": 2, "ThreadsPerCore": 2},
            "EbsOptimized": False,
            "EnaSupport": True,
            "EnclaveOptions": {"Enabled": True},
            "Hypervisor": "xen",
            "ImageId": "ami-08e4e35cccc6189f4",
            "InstanceId": "test-instance-id",
            "InstanceType": "c5a.xlarge",
            "KeyName": "test-key",
            "LaunchTime": datetime.datetime(2022, 7, 1, 19, 30, 24, tzinfo=tzutc()),
            "MaintenanceOptions": {"AutoRecovery": "default"},
            "MetadataOptions": {
                "HttpEndpoint": "enabled",
                "HttpProtocolIpv6": "disabled",
                "HttpPutResponseHopLimit": 1,
                "HttpTokens": "optional",
                "InstanceMetadataTags": "disabled",
                "State": "pending",
            },
            "Monitoring": {"State": "disabled"},
            "NetworkInterfaces": [
                {
                    "Attachment": {
                        "AttachTime": datetime.datetime(2022, 7, 1, 19, 30, 24, tzinfo=tzutc()),
                        "AttachmentId": "eni-attach-06e6c48db81d58d32",
                        "DeleteOnTermination": True,
                        "DeviceIndex": 0,
                        "NetworkCardIndex": 0,
                        "Status": "attaching",
                    },
                    "Description": "",
                    "Groups": [{"GroupId": "sg-0e20fb2c07aa618f0", "GroupName": "zpr-lts"}],
                    "InterfaceType": "interface",
                    "Ipv6Addresses": [],
                    "MacAddress": "16:53:61:fc:d7:7d",
                    "NetworkInterfaceId": "eni-0de2e8b867c19387d",
                    "OwnerId": "233808678534",
                    "PrivateDnsName": "ip-172-31-52-69.ec2.internal",
                    "PrivateIpAddress": "172.31.52.69",
                    "PrivateIpAddresses": [
                        {
                            "Primary": True,
                            "PrivateDnsName": "ip-172-31-52-69.ec2.internal",
                            "PrivateIpAddress": "172.31.52.69",
                        }
                    ],
                    "SourceDestCheck": True,
                    "Status": "in-use",
                    "SubnetId": "subnet-d95b9cd7",
                    "VpcId": "vpc-a76039dd",
                }
            ],
            "Placement": {
                "AvailabilityZone": "us-east-1f",
                "GroupName": "",
                "Tenancy": "default",
            },
            "PrivateDnsName": "ip-172-31-52-69.ec2.internal",
            "PrivateDnsNameOptions": {
                "EnableResourceNameDnsAAAARecord": False,
                "EnableResourceNameDnsARecord": False,
                "HostnameType": "ip-name",
            },
            "PrivateIpAddress": "172.31.52.69",
            "ProductCodes": [],
            "PublicDnsName": "",
            "RootDeviceName": "/dev/xvda",
            "RootDeviceType": "ebs",
            "SecurityGroups": [{"GroupId": "sg-0e20fb2c07aa618f0", "GroupName": "zpr-lts"}],
            "SourceDestCheck": True,
            "State": {"Code": 0, "Name": "pending"},
            "StateReason": {"Code": "pending", "Message": "pending"},
            "StateTransitionReason": "",
            "SubnetId": "subnet-d95b9cd7",
            "Tags": [
                {"Key": "Deployment", "Value": "Sequencer"},
                {"Key": "Name", "Value": "test-instance"},
            ],
            "VirtualizationType": "hvm",
            "VpcId": "vpc-a76039dd",
        }
    ],
    "OwnerId": "233808678534",
    "ReservationId": "r-072d60e6b656dba83",
    "ResponseMetadata": {
        "HTTPHeaders": {
            "cache-control": "no-cache, no-store",
            "content-length": "5777",
            "content-type": "text/xml;charset=UTF-8",
            "date": "Fri, 01 Jul 2022 19:30:23 GMT",
            "server": "AmazonEC2",
            "strict-transport-security": "max-age=31536000; " "includeSubDomains",
            "vary": "accept-encoding",
            "x-amzn-requestid": "7c545adc-516c-47f0-995c-5a77e80d2f2e",
        },
        "HTTPStatusCode": 200,
        "RequestId": "7c545adc-516c-47f0-995c-5a77e80d2f2e",
        "RetryAttempts": 0,
    },
}

describe_instances_ret_two_instances = {
    "Reservations": [
        {
            "Groups": [],
            "Instances": [
                {
                    "AmiLaunchIndex": 0,
                    "Architecture": "x86_64",
                    "BlockDeviceMappings": [
                        {
                            "DeviceName": "/dev/xvda",
                            "Ebs": {
                                "AttachTime": datetime.datetime(
                                    2022, 6, 17, 22, 29, 21, tzinfo=tzutc()
                                ),
                                "DeleteOnTermination": True,
                                "Status": "attaching",
                                "VolumeId": "vol-09bc192718d391e04",
                            },
                        }
                    ],
                    "CapacityReservationSpecification": {"CapacityReservationPreference": "open"},
                    "ClientToken": "82cd14d0-a043-4689-8ba5-e3c83e787dc9",
                    "CpuOptions": {"CoreCount": 2, "ThreadsPerCore": 2},
                    "EbsOptimized": False,
                    "EnaSupport": True,
                    "EnclaveOptions": {"Enabled": True},
                    "HibernationOptions": {"Configured": False},
                    "Hypervisor": "xen",
                    "ImageId": "ami-08e4e35cccc6189f4",
                    "InstanceId": instance_id,
                    "InstanceType": "c5a.xlarge",
                    "KeyName": key_name,
                    "LaunchTime": datetime.datetime(2022, 6, 17, 22, 29, 20, tzinfo=tzutc()),
                    "MaintenanceOptions": {"AutoRecovery": "default"},
                    "MetadataOptions": {
                        "HttpEndpoint": "enabled",
                        "HttpProtocolIpv6": "disabled",
                        "HttpPutResponseHopLimit": 1,
                        "HttpTokens": "optional",
                        "InstanceMetadataTags": "disabled",
                        "State": "pending",
                    },
                    "Monitoring": {"State": "disabled"},
                    "NetworkInterfaces": [
                        {
                            "Association": {
                                "IpOwnerId": "amazon",
                                "PublicDnsName": "ec2-3-235-31-42.compute-1.amazonaws.com",
                                "PublicIp": "3.235.31.42",
                            },
                            "Attachment": {
                                "AttachTime": datetime.datetime(
                                    2022, 6, 17, 22, 29, 20, tzinfo=tzutc()
                                ),
                                "AttachmentId": "eni-attach-0a516ae4f2e444428",
                                "DeleteOnTermination": True,
                                "DeviceIndex": 0,
                                "NetworkCardIndex": 0,
                                "Status": "attaching",
                            },
                            "Description": "",
                            "Groups": [
                                {
                                    "GroupId": "sg-0e20fb2c07aa618f0",
                                    "GroupName": "zpr-lts",
                                }
                            ],
                            "InterfaceType": "interface",
                            "Ipv6Addresses": [],
                            "MacAddress": "16:aa:78:5d:a4:e7",
                            "NetworkInterfaceId": "eni-07f17649d4afd24c6",
                            "OwnerId": "233808678534",
                            "PrivateDnsName": "ip-172-31-51-34.ec2.internal",
                            "PrivateIpAddress": "172.31.51.34",
                            "PrivateIpAddresses": [
                                {
                                    "Association": {
                                        "IpOwnerId": "amazon",
                                        "PublicDnsName": "ec2-3-235-31-42.compute-1.amazonaws.com",
                                        "PublicIp": "3.235.31.42",
                                    },
                                    "Primary": True,
                                    "PrivateDnsName": "ip-172-31-51-34.ec2.internal",
                                    "PrivateIpAddress": "172.31.51.34",
                                }
                            ],
                            "SourceDestCheck": True,
                            "Status": "in-use",
                            "SubnetId": "subnet-d95b9cd7",
                            "VpcId": "vpc-a76039dd",
                        }
                    ],
                    "Placement": {
                        "AvailabilityZone": "us-east-1f",
                        "GroupName": "",
                        "Tenancy": "default",
                    },
                    "PlatformDetails": "Linux/UNIX",
                    "PrivateDnsName": "ip-172-31-51-34.ec2.internal",
                    "PrivateDnsNameOptions": {
                        "EnableResourceNameDnsAAAARecord": False,
                        "EnableResourceNameDnsARecord": False,
                        "HostnameType": "ip-name",
                    },
                    "PrivateIpAddress": "172.31.51.34",
                    "ProductCodes": [],
                    "PublicDnsName": "ec2-3-235-31-42.compute-1.amazonaws.com",
                    "PublicIpAddress": "3.235.31.42",
                    "RootDeviceName": "/dev/xvda",
                    "RootDeviceType": "ebs",
                    "SecurityGroups": [{"GroupId": security_group, "GroupName": "some-name"}],
                    "SourceDestCheck": True,
                    "State": {"Code": 0, "Name": "pending"},
                    "StateTransitionReason": "",
                    "SubnetId": "subnet-d95b9cd7",
                    "Tags": [
                        {"Key": "Deployment", "Value": "Sequencer"},
                        {"Key": "Name", "Value": instance_name},
                    ],
                    "UsageOperation": "RunInstances",
                    "UsageOperationUpdateTime": datetime.datetime(
                        2022, 6, 17, 22, 29, 20, tzinfo=tzutc()
                    ),
                    "VirtualizationType": "hvm",
                    "VpcId": "vpc-a76039dd",
                },
                {
                    "AmiLaunchIndex": 0,
                    "Architecture": "x86_64",
                    "BlockDeviceMappings": [
                        {
                            "DeviceName": "/dev/xvda",
                            "Ebs": {
                                "AttachTime": datetime.datetime(
                                    2022, 6, 17, 22, 29, 21, tzinfo=tzutc()
                                ),
                                "DeleteOnTermination": True,
                                "Status": "attaching",
                                "VolumeId": "vol-09bc192718d391e04",
                            },
                        }
                    ],
                    "CapacityReservationSpecification": {"CapacityReservationPreference": "open"},
                    "ClientToken": "82cd14d0-a043-4689-8ba5-e3c83e787dc9",
                    "CpuOptions": {"CoreCount": 2, "ThreadsPerCore": 2},
                    "EbsOptimized": False,
                    "EnaSupport": True,
                    "EnclaveOptions": {"Enabled": True},
                    "HibernationOptions": {"Configured": False},
                    "Hypervisor": "xen",
                    "ImageId": "ami-08e4e35cccc6189f4",
                    "InstanceId": instance_id,
                    "InstanceType": "c5a.xlarge",
                    "KeyName": key_name,
                    "LaunchTime": datetime.datetime(2022, 6, 17, 22, 29, 20, tzinfo=tzutc()),
                    "MaintenanceOptions": {"AutoRecovery": "default"},
                    "MetadataOptions": {
                        "HttpEndpoint": "enabled",
                        "HttpProtocolIpv6": "disabled",
                        "HttpPutResponseHopLimit": 1,
                        "HttpTokens": "optional",
                        "InstanceMetadataTags": "disabled",
                        "State": "pending",
                    },
                    "Monitoring": {"State": "disabled"},
                    "NetworkInterfaces": [
                        {
                            "Association": {
                                "IpOwnerId": "amazon",
                                "PublicDnsName": "ec2-3-235-31-42.compute-1.amazonaws.com",
                                "PublicIp": "3.235.31.42",
                            },
                            "Attachment": {
                                "AttachTime": datetime.datetime(
                                    2022, 6, 17, 22, 29, 20, tzinfo=tzutc()
                                ),
                                "AttachmentId": "eni-attach-0a516ae4f2e444428",
                                "DeleteOnTermination": True,
                                "DeviceIndex": 0,
                                "NetworkCardIndex": 0,
                                "Status": "attaching",
                            },
                            "Description": "",
                            "Groups": [
                                {
                                    "GroupId": "sg-0e20fb2c07aa618f0",
                                    "GroupName": "zpr-lts",
                                }
                            ],
                            "InterfaceType": "interface",
                            "Ipv6Addresses": [],
                            "MacAddress": "16:aa:78:5d:a4:e7",
                            "NetworkInterfaceId": "eni-07f17649d4afd24c6",
                            "OwnerId": "233808678534",
                            "PrivateDnsName": "ip-172-31-51-34.ec2.internal",
                            "PrivateIpAddress": "172.31.51.34",
                            "PrivateIpAddresses": [
                                {
                                    "Association": {
                                        "IpOwnerId": "amazon",
                                        "PublicDnsName": "ec2-3-235-31-42.compute-1.amazonaws.com",
                                        "PublicIp": "3.235.31.42",
                                    },
                                    "Primary": True,
                                    "PrivateDnsName": "ip-172-31-51-34.ec2.internal",
                                    "PrivateIpAddress": "172.31.51.34",
                                }
                            ],
                            "SourceDestCheck": True,
                            "Status": "in-use",
                            "SubnetId": "subnet-d95b9cd7",
                            "VpcId": "vpc-a76039dd",
                        }
                    ],
                    "Placement": {
                        "AvailabilityZone": "us-east-1f",
                        "GroupName": "",
                        "Tenancy": "default",
                    },
                    "PlatformDetails": "Linux/UNIX",
                    "PrivateDnsName": "ip-172-31-51-34.ec2.internal",
                    "PrivateDnsNameOptions": {
                        "EnableResourceNameDnsAAAARecord": False,
                        "EnableResourceNameDnsARecord": False,
                        "HostnameType": "ip-name",
                    },
                    "PrivateIpAddress": "172.31.51.34",
                    "ProductCodes": [],
                    "PublicDnsName": "ec2-3-235-31-42.compute-1.amazonaws.com",
                    "PublicIpAddress": "3.235.31.42",
                    "RootDeviceName": "/dev/xvda",
                    "RootDeviceType": "ebs",
                    "SecurityGroups": [{"GroupId": security_group, "GroupName": "some-name"}],
                    "SourceDestCheck": True,
                    "State": {"Code": 0, "Name": "pending"},
                    "StateTransitionReason": "",
                    "SubnetId": "subnet-d95b9cd7",
                    "Tags": [
                        {"Key": "Deployment", "Value": "Sequencer"},
                        {"Key": "Name", "Value": instance_name},
                    ],
                    "UsageOperation": "RunInstances",
                    "UsageOperationUpdateTime": datetime.datetime(
                        2022, 6, 17, 22, 29, 20, tzinfo=tzutc()
                    ),
                    "VirtualizationType": "hvm",
                    "VpcId": "vpc-a76039dd",
                },
            ],
            "OwnerId": "233808678534",
            "ReservationId": "r-08ae3905085844e09",
        }
    ],
    "ResponseMetadata": {
        "HTTPHeaders": {
            "cache-control": "no-cache, no-store",
            "content-type": "text/xml;charset=UTF-8",
            "date": "Fri, 17 Jun 2022 22:29:23 GMT",
            "server": "AmazonEC2",
            "strict-transport-security": "max-age=31536000; " "includeSubDomains",
            "transfer-encoding": "chunked",
            "vary": "accept-encoding",
            "x-amzn-requestid": "af3ee9a9-1e82-4118-a051-50d321460977",
        },
        "HTTPStatusCode": 200,
        "RequestId": "af3ee9a9-1e82-4118-a051-50d321460977",
        "RetryAttempts": 0,
    },
}

list_instances_ret_one_instance = [
    {
        "InstanceId": instance_id,
        "KeyName": key_name,
        "PublicIpAddress": "3.235.31.42",
        "Tags": [
            {"Key": "Deployment", "Value": "Sequencer"},
            {"Key": "Name", "Value": "test-instance"},
        ],
    }
]
