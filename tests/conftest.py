# pylint: disable = too-many-lines
import datetime
import os.path
import pathlib

import pytest
import botocore.exceptions
from dateutil.tz import tzutc

import ned

NED_UNIT_TEST_FIXTURES_FILE_PATH = pathlib.Path(__file__).parent.joinpath("fixtures").resolve()


def pytest_addoption(parser):
    parser.addoption("--pyned", action="store", default="python -m ned")


@pytest.fixture
def pyiac(pytestconfig):
    return pytestconfig.getoption("--pyned")


class AWSCannedResponses:
    # pylint: disable = too-many-instance-attributes
    def __init__(self):
        self.instance_id = "test-instance-id"
        self.instance_name = "test-instance"
        self.instance_public_dns = "test-instance1-dns.compute-1.amazonaws.com"
        self.instance_public_ip = "34.238.190.126"
        self.key_name = "test-key"
        self.security_group = "test-security-group"

        self.other_instance_id = "test-instance2-id"
        self.other_instance_name = "test-instance2"

        self.hosted_zone = ned.dns.HostedZone(
            fqdn="bky.sh",
            hz_id="Z05346603ECE7KDEFCYS2",
        )

        self.resource_record = ned.dns.ResourceRecord(
            fqdn="a.b.dlm.bky.sh",
            ip="'18.205.236.134",
            record_type="A",
        )

    @property
    def instance(self):
        resp = self.describe_instances__one_instance
        inst = resp["Reservations"][0]["Instances"][0]
        return ned.Instance.from_aws_instance(inst)

    @property
    def other_instance(self):
        resp = self.describe_instances__many_instances
        inst = resp["Reservations"][0]["Instances"][0]
        return ned.Instance.from_aws_instance(inst)

    @property
    def describe_instances__no_instances(self):
        return {
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

    @property
    def describe_instances__one_instance(self):
        return {
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
                            "CapacityReservationSpecification": {
                                "CapacityReservationPreference": "open"
                            },
                            "ClientToken": "82cd14d0-a043-4689-8ba5-e3c83e787dc9",
                            "CpuOptions": {"CoreCount": 2, "ThreadsPerCore": 2},
                            "EbsOptimized": False,
                            "EnaSupport": True,
                            "EnclaveOptions": {"Enabled": True},
                            "HibernationOptions": {"Configured": False},
                            "Hypervisor": "xen",
                            "ImageId": "ami-08e4e35cccc6189f4",
                            "InstanceId": self.instance_id,
                            "InstanceType": "c5a.xlarge",
                            "KeyName": self.key_name,
                            "LaunchTime": datetime.datetime(
                                2022, 6, 17, 22, 29, 20, tzinfo=tzutc()
                            ),
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
                                        "PublicDnsName": self.instance_public_dns,
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
                                                "PublicDnsName": self.instance_public_dns,
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
                            "PublicDnsName": self.instance_public_dns,
                            "PublicIpAddress": self.instance_public_ip,
                            "RootDeviceName": "/dev/xvda",
                            "RootDeviceType": "ebs",
                            "SecurityGroups": [
                                {"GroupId": self.security_group, "GroupName": "some-name"}
                            ],
                            "SourceDestCheck": True,
                            "State": {"Code": 16, "Name": "running"},
                            "StateTransitionReason": "",
                            "SubnetId": "subnet-d95b9cd7",
                            "Tags": [
                                {"Key": "Deployment", "Value": "Sequencer"},
                                {"Key": "Name", "Value": self.instance_name},
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

    @property
    def describe_instances__many_instances(self):
        # pylint: disable=line-too-long
        return {
            "Reservations": [
                {
                    "Groups": [],
                    "Instances": [
                        {
                            "AmiLaunchIndex": 0,
                            "ImageId": "ami-08e4e35cccc6189f4",
                            "InstanceId": self.other_instance_id,
                            "InstanceType": "c5a.xlarge",
                            "KeyName": self.key_name,
                            "LaunchTime": datetime.datetime(
                                2022, 7, 13, 18, 21, 55, tzinfo=tzutc()
                            ),
                            "Monitoring": {"State": "disabled"},
                            "Placement": {
                                "AvailabilityZone": "us-east-1f",
                                "GroupName": "",
                                "Tenancy": "default",
                            },
                            "PrivateDnsName": "ip-172-31-56-122.ec2.internal",
                            "PrivateIpAddress": "172.31.56.122",
                            "ProductCodes": [],
                            "PublicDnsName": "ec2-3-235-225-44.compute-1.amazonaws.com",
                            "PublicIpAddress": "3.235.225.44",
                            "State": {"Code": 16, "Name": "running"},
                            "StateTransitionReason": "",
                            "SubnetId": "subnet-d95b9cd7",
                            "VpcId": "vpc-a76039dd",
                            "Architecture": "x86_64",
                            "BlockDeviceMappings": [
                                {
                                    "DeviceName": "/dev/xvda",
                                    "Ebs": {
                                        "AttachTime": datetime.datetime(
                                            2022, 7, 13, 18, 21, 55, tzinfo=tzutc()
                                        ),
                                        "DeleteOnTermination": True,
                                        "Status": "attached",
                                        "VolumeId": "vol-07a967d72d3750929",
                                    },
                                }
                            ],
                            "ClientToken": "83714446-d1ad-4fea-901f-fd2e3ab129b8",
                            "EbsOptimized": False,
                            "EnaSupport": True,
                            "Hypervisor": "xen",
                            "NetworkInterfaces": [
                                {
                                    "Association": {
                                        "IpOwnerId": "amazon",
                                        "PublicDnsName": "ec2-3-235-225-44.compute-1.amazonaws.com",
                                        "PublicIp": "3.235.225.44",
                                    },
                                    "Attachment": {
                                        "AttachTime": datetime.datetime(
                                            2022, 7, 13, 18, 21, 55, tzinfo=tzutc()
                                        ),
                                        "AttachmentId": "eni-attach-0230da5b566f890e5",
                                        "DeleteOnTermination": True,
                                        "DeviceIndex": 0,
                                        "Status": "attached",
                                        "NetworkCardIndex": 0,
                                    },
                                    "Description": "",
                                    "Groups": [
                                        {
                                            "GroupName": "mwittie-testing",
                                            "GroupId": "sg-01d5cadef8278c497",
                                        }
                                    ],
                                    "Ipv6Addresses": [],
                                    "MacAddress": "16:f1:b4:dc:b3:d7",
                                    "NetworkInterfaceId": "eni-0f1b21093392194be",
                                    "OwnerId": "233808678534",
                                    "PrivateDnsName": "ip-172-31-56-122.ec2.internal",
                                    "PrivateIpAddress": "172.31.56.122",
                                    "PrivateIpAddresses": [
                                        {
                                            "Association": {
                                                "IpOwnerId": "amazon",
                                                "PublicDnsName": "ec2-3-235-225-44.compute-1.amazonaws.com",  # noqa: E501
                                                "PublicIp": "3.235.225.44",
                                            },
                                            "Primary": True,
                                            "PrivateDnsName": "ip-172-31-56-122.ec2.internal",
                                            "PrivateIpAddress": "172.31.56.122",
                                        }
                                    ],
                                    "SourceDestCheck": True,
                                    "Status": "in-use",
                                    "SubnetId": "subnet-d95b9cd7",
                                    "VpcId": "vpc-a76039dd",
                                    "InterfaceType": "interface",
                                }
                            ],
                            "RootDeviceName": "/dev/xvda",
                            "RootDeviceType": "ebs",
                            "SecurityGroups": [
                                {"GroupName": "mwittie-testing", "GroupId": "sg-01d5cadef8278c497"}
                            ],
                            "SourceDestCheck": True,
                            "Tags": [
                                {"Key": "Deployment", "Value": "Sequencer"},
                                {"Key": "Name", "Value": self.other_instance_name},
                            ],
                            "VirtualizationType": "hvm",
                            "CpuOptions": {"CoreCount": 2, "ThreadsPerCore": 2},
                            "CapacityReservationSpecification": {
                                "CapacityReservationPreference": "open"
                            },
                            "HibernationOptions": {"Configured": False},
                            "MetadataOptions": {
                                "State": "applied",
                                "HttpTokens": "optional",
                                "HttpPutResponseHopLimit": 1,
                                "HttpEndpoint": "enabled",
                                "HttpProtocolIpv6": "disabled",
                                "InstanceMetadataTags": "disabled",
                            },
                            "EnclaveOptions": {"Enabled": True},
                            "PlatformDetails": "Linux/UNIX",
                            "UsageOperation": "RunInstances",
                            "UsageOperationUpdateTime": datetime.datetime(
                                2022, 7, 13, 18, 21, 55, tzinfo=tzutc()
                            ),
                            "PrivateDnsNameOptions": {
                                "HostnameType": "ip-name",
                                "EnableResourceNameDnsARecord": False,
                                "EnableResourceNameDnsAAAARecord": False,
                            },
                            "MaintenanceOptions": {"AutoRecovery": "default"},
                        }
                    ],
                    "OwnerId": "233808678534",
                    "ReservationId": "r-09c7a4c32ba32de6b",
                },
                {
                    "Groups": [],
                    "Instances": [
                        {
                            "AmiLaunchIndex": 0,
                            "ImageId": "ami-08e4e35cccc6189f4",
                            "InstanceId": self.instance_id,
                            "InstanceType": "c5a.xlarge",
                            "KeyName": self.key_name,
                            "LaunchTime": datetime.datetime(
                                2022, 7, 13, 18, 21, 44, tzinfo=tzutc()
                            ),
                            "Monitoring": {"State": "disabled"},
                            "Placement": {
                                "AvailabilityZone": "us-east-1f",
                                "GroupName": "",
                                "Tenancy": "default",
                            },
                            "PrivateDnsName": "ip-172-31-51-163.ec2.internal",
                            "PrivateIpAddress": "172.31.51.163",
                            "ProductCodes": [],
                            "PublicDnsName": self.instance_public_dns,
                            "PublicIpAddress": self.instance_public_ip,
                            "State": {"Code": 16, "Name": "running"},
                            "StateTransitionReason": "",
                            "SubnetId": "subnet-d95b9cd7",
                            "VpcId": "vpc-a76039dd",
                            "Architecture": "x86_64",
                            "BlockDeviceMappings": [
                                {
                                    "DeviceName": "/dev/xvda",
                                    "Ebs": {
                                        "AttachTime": datetime.datetime(
                                            2022, 7, 13, 18, 21, 45, tzinfo=tzutc()
                                        ),
                                        "DeleteOnTermination": True,
                                        "Status": "attached",
                                        "VolumeId": "vol-03e71944de050292a",
                                    },
                                }
                            ],
                            "ClientToken": "3ec98a00-4350-4e4e-b6e2-eaff5062ee9e",
                            "EbsOptimized": False,
                            "EnaSupport": True,
                            "Hypervisor": "xen",
                            "NetworkInterfaces": [
                                {
                                    "Association": {
                                        "IpOwnerId": "amazon",
                                        "PublicDnsName": self.instance_public_dns,
                                        "PublicIp": "34.238.190.126",
                                    },
                                    "Attachment": {
                                        "AttachTime": datetime.datetime(
                                            2022, 7, 13, 18, 21, 44, tzinfo=tzutc()
                                        ),
                                        "AttachmentId": "eni-attach-0ddbb0c4b264f00e7",
                                        "DeleteOnTermination": True,
                                        "DeviceIndex": 0,
                                        "Status": "attached",
                                        "NetworkCardIndex": 0,
                                    },
                                    "Description": "",
                                    "Groups": [
                                        {
                                            "GroupName": "mwittie-testing",
                                            "GroupId": "sg-01d5cadef8278c497",
                                        }
                                    ],
                                    "Ipv6Addresses": [],
                                    "MacAddress": "16:bf:8e:e7:b1:b3",
                                    "NetworkInterfaceId": "eni-0faf46ab2a81818d9",
                                    "OwnerId": "233808678534",
                                    "PrivateDnsName": "ip-172-31-51-163.ec2.internal",
                                    "PrivateIpAddress": "172.31.51.163",
                                    "PrivateIpAddresses": [
                                        {
                                            "Association": {
                                                "IpOwnerId": "amazon",
                                                "PublicDnsName": self.instance_public_dns,
                                                "PublicIp": "34.238.190.126",
                                            },
                                            "Primary": True,
                                            "PrivateDnsName": "ip-172-31-51-163.ec2.internal",
                                            "PrivateIpAddress": "172.31.51.163",
                                        }
                                    ],
                                    "SourceDestCheck": True,
                                    "Status": "in-use",
                                    "SubnetId": "subnet-d95b9cd7",
                                    "VpcId": "vpc-a76039dd",
                                    "InterfaceType": "interface",
                                }
                            ],
                            "RootDeviceName": "/dev/xvda",
                            "RootDeviceType": "ebs",
                            "SecurityGroups": [
                                {"GroupName": "mwittie-testing", "GroupId": "sg-01d5cadef8278c497"}
                            ],
                            "SourceDestCheck": True,
                            "Tags": [
                                {"Key": "Deployment", "Value": "Sequencer"},
                                {"Key": "Name", "Value": self.instance_name},
                            ],
                            "VirtualizationType": "hvm",
                            "CpuOptions": {"CoreCount": 2, "ThreadsPerCore": 2},
                            "CapacityReservationSpecification": {
                                "CapacityReservationPreference": "open"
                            },
                            "HibernationOptions": {"Configured": False},
                            "MetadataOptions": {
                                "State": "applied",
                                "HttpTokens": "optional",
                                "HttpPutResponseHopLimit": 1,
                                "HttpEndpoint": "enabled",
                                "HttpProtocolIpv6": "disabled",
                                "InstanceMetadataTags": "disabled",
                            },
                            "EnclaveOptions": {"Enabled": True},
                            "PlatformDetails": "Linux/UNIX",
                            "UsageOperation": "RunInstances",
                            "UsageOperationUpdateTime": datetime.datetime(
                                2022, 7, 13, 18, 21, 44, tzinfo=tzutc()
                            ),
                            "PrivateDnsNameOptions": {
                                "HostnameType": "ip-name",
                                "EnableResourceNameDnsARecord": False,
                                "EnableResourceNameDnsAAAARecord": False,
                            },
                            "MaintenanceOptions": {"AutoRecovery": "default"},
                        }
                    ],
                    "OwnerId": "233808678534",
                    "ReservationId": "r-0e8280415a9fdc968",
                },
            ],
            "ResponseMetadata": {
                "RequestId": "61484be5-557a-4f1f-b9be-43dd13452f68",
                "HTTPStatusCode": 200,
                "RetryAttempts": 0,
            },
        }

    @property
    def run_instances(self):
        return {
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
                    "InstanceId": self.instance_id,
                    "InstanceType": "c5a.xlarge",
                    "KeyName": self.key_name,
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
                                "AttachTime": datetime.datetime(
                                    2022, 7, 1, 19, 30, 24, tzinfo=tzutc()
                                ),
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
                    "SecurityGroups": [
                        {"GroupId": "sg-0e20fb2c07aa618f0", "GroupName": self.security_group}
                    ],
                    "SourceDestCheck": True,
                    "State": {"Code": 0, "Name": "pending"},
                    "StateReason": {"Code": "pending", "Message": "pending"},
                    "StateTransitionReason": "",
                    "SubnetId": "subnet-d95b9cd7",
                    "Tags": [
                        {"Key": "Deployment", "Value": "Sequencer"},
                        {"Key": "Name", "Value": self.instance_name},
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

    def terminate_instances_result(self, state):
        return {
            "ResponseMetadata": {
                "HTTPHeaders": {
                    "cache-control": "no-cache, no-store",
                    "content-type": "text/xml;charset=UTF-8",
                    "date": "Fri, 09 Sep 2022 00:49:30 GMT",
                    "server": "AmazonEC2",
                    "strict-transport-security": "max-age=31536000; " "includeSubDomains",
                    "transfer-encoding": "chunked",
                    "vary": "accept-encoding",
                    "x-amzn-requestid": "a7681118-c1ba-4834-82bb-4f4ad5c7fd8f",
                },
                "HTTPStatusCode": 200,
                "RequestId": "a7681118-c1ba-4834-82bb-4f4ad5c7fd8f",
                "RetryAttempts": 0,
            },
            "TerminatingInstances": [
                {
                    "CurrentState": {"Code": 32, "Name": state},
                    "InstanceId": self.instance_id,
                    "PreviousState": {"Code": 16, "Name": "running"},
                }
            ],
        }

    @property
    def describe_key_pairs__no_keys(self):
        return {
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

    @property
    def describe_key_pairs__one_key(self):
        return {
            "KeyPairs": [
                {
                    "CreateTime": datetime.datetime(2022, 6, 10, 22, 8, 3, tzinfo=tzutc()),
                    "KeyFingerprint": "f3:2c:c5:9f:b4:41:0d:fe:32:2b:f8:3b:e6:91:f4:91:e3:84:7e:95",
                    "KeyName": self.key_name,
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

    @property
    def key_not_found_error(self):
        return botocore.exceptions.ClientError(
            {
                "Error": {
                    "Code": "InvalidKeyPair.NotFound",
                    "Message": f"The key pair '{self.key_name}' does not exist",
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

    @property
    def create_key_pair(self):
        return {
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
            "KeyName": self.key_name,
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

    @property
    def create_key_pair_error(self):
        return botocore.exceptions.ClientError(
            {
                "Error": {
                    "Code": "InvalidKeyPair.Duplicate",
                    "Message": f"The keypair '{self.key_name}' already exists.",
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

    @property
    def list_hosted_zones_by_name__zero_zones(self):
        return {
            "DNSName": "boom.sh",
            "HostedZones": [],
            "IsTruncated": False,
            "MaxItems": "1",
            "ResponseMetadata": {
                "HTTPHeaders": {
                    "content-length": "233",
                    "content-type": "text/xml",
                    "date": "Sat, 05 Nov 2022 21:30:53 GMT",
                    "x-amzn-requestid": "d235ba78-91a1-43ab-8139-bc4ad1b8f357",
                },
                "HTTPStatusCode": 200,
                "RequestId": "d235ba78-91a1-43ab-8139-bc4ad1b8f357",
                "RetryAttempts": 0,
            },
        }

    @property
    def list_hosted_zones_by_name__one_zone(self):
        return {
            "DNSName": self.hosted_zone.fqdn,
            "HostedZones": [
                {
                    "CallerReference": "079df300-ed87-4459-ad5d-f9d56f1412bf",
                    "Config": {"Comment": "", "PrivateZone": False},
                    "Id": f"/hostedzone/{self.hosted_zone.hz_id}",
                    "Name": self.hosted_zone.fqdn + ".",
                    "ResourceRecordSetCount": 6,
                }
            ],
            "IsTruncated": False,
            "MaxItems": "1",
            "ResponseMetadata": {
                "HTTPHeaders": {
                    "content-length": "521",
                    "content-type": "text/xml",
                    "date": "Sat, 05 Nov 2022 21:22:30 GMT",
                    "x-amzn-requestid": "6132ec8b-9e1d-406b-9da8-db7bf0777d03",
                },
                "HTTPStatusCode": 200,
                "RequestId": "6132ec8b-9e1d-406b-9da8-db7bf0777d03",
                "RetryAttempts": 0,
            },
        }

    @property
    def change_resource_record_sets__succeess(self):
        return {
            "ChangeInfo": {
                "Id": "/change/C01794081MEKLH83PRA05",
                "Status": "PENDING",
                "SubmittedAt": datetime.datetime(2022, 11, 5, 23, 53, 30, 663000, tzinfo=tzutc()),
            },
            "ResponseMetadata": {
                "HTTPHeaders": {
                    "content-length": "283",
                    "content-type": "text/xml",
                    "date": "Sat, 05 Nov 2022 23:53:30 GMT",
                    "x-amzn-requestid": "7ca9ac33-fb8c-4b8d-b4fb-48d20abca451",
                },
                "HTTPStatusCode": 200,
                "RequestId": "7ca9ac33-fb8c-4b8d-b4fb-48d20abca451",
                "RetryAttempts": 0,
            },
        }

    @property
    def list_resource_record_sets__one_record(self):
        return {
            "IsTruncated": True,
            "MaxItems": "1",
            "NextRecordName": "mwittie.bky.sh.",
            "NextRecordType": "A",
            "ResourceRecordSets": [
                {
                    "Name": self.resource_record.fqdn + ".",
                    "ResourceRecords": [{"Value": self.resource_record.ip}],
                    "TTL": 300,
                    "Type": self.resource_record.record_type,
                }
            ],
            "ResponseMetadata": {
                "HTTPHeaders": {
                    "content-length": "509",
                    "content-type": "text/xml",
                    "date": "Sun, 06 Nov 2022 00:15:22 GMT",
                    "x-amzn-requestid": "02cf40ff-c43f-4e42-931a-1398cdd4474e",
                },
                "HTTPStatusCode": 200,
                "RequestId": "02cf40ff-c43f-4e42-931a-1398cdd4474e",
                "RetryAttempts": 0,
            },
        }

    @property
    def list_resource_record_sets__not_one_record(self):
        return {
            "IsTruncated": True,
            "MaxItems": "1",
            "NextRecordName": "mwittie.bky.sh.",
            "NextRecordType": "A",
            "ResourceRecordSets": [],
            "ResponseMetadata": {
                "HTTPHeaders": {
                    "content-length": "509",
                    "content-type": "text/xml",
                    "date": "Sun, 06 Nov 2022 00:15:22 GMT",
                    "x-amzn-requestid": "02cf40ff-c43f-4e42-931a-1398cdd4474e",
                },
                "HTTPStatusCode": 200,
                "RequestId": "02cf40ff-c43f-4e42-931a-1398cdd4474e",
                "RetryAttempts": 0,
            },
        }

    @property
    def list_resource_record_sets__many_records(self):
        return {
            "IsTruncated": False,
            "MaxItems": "300",
            "ResourceRecordSets": [
                {
                    "Name": "bky.sh.",
                    "ResourceRecords": [
                        {"Value": "ns-382.awsdns-47.com."},
                        {"Value": "ns-1037.awsdns-01.org."},
                        {"Value": "ns-866.awsdns-44.net."},
                        {"Value": "ns-1730.awsdns-24.co.uk."},
                    ],
                    "TTL": 172800,
                    "Type": "NS",
                },
                {
                    "Name": "bky.sh.",
                    "ResourceRecords": [
                        {
                            "Value": "ns-382.awsdns-47.com. "
                            "awsdns-hostmaster.amazon.com. "
                            "1 7200 900 1209600 "
                            "86400"
                        }
                    ],
                    "TTL": 900,
                    "Type": "SOA",
                },
                {
                    "Name": "mwittie.bky.sh.",
                    "ResourceRecords": [{"Value": "54.163.127.43"}],
                    "TTL": 300,
                    "Type": "A",
                },
                {
                    "Name": "sequencer-dev.bky.sh.",
                    "ResourceRecords": [{"Value": "3.87.202.142"}],
                    "TTL": 300,
                    "Type": "A",
                },
                {
                    "Name": "sequencer-mwittie.bky.sh.",
                    "ResourceRecords": [{"Value": "44.200.44.151"}],
                    "TTL": 300,
                    "Type": "A",
                },
                {
                    "Name": "demo.zpr.bky.sh.",
                    "ResourceRecords": [{"Value": "54.198.161.170"}],
                    "TTL": 300,
                    "Type": "A",
                },
            ],
            "ResponseMetadata": {
                "HTTPHeaders": {
                    "content-length": "1673",
                    "content-type": "text/xml",
                    "date": "Tue, 08 Nov 2022 20:57:49 GMT",
                    "x-amzn-requestid": "8aa6bbdc-b666-4854-a569-fd9d474b6951",
                },
                "HTTPStatusCode": 200,
                "RequestId": "8aa6bbdc-b666-4854-a569-fd9d474b6951",
                "RetryAttempts": 0,
            },
        }


@pytest.fixture
def aws_parrot():
    return AWSCannedResponses()


@pytest.fixture
def credential_file_name():
    file_name = "credentials_for_testing.csv"
    return os.path.join(NED_UNIT_TEST_FIXTURES_FILE_PATH, file_name)


@pytest.fixture
def config_file_name():
    file_name = "config_for_testing.toml"
    return os.path.join(NED_UNIT_TEST_FIXTURES_FILE_PATH, file_name)


@pytest.fixture
def config_file_with_no_creds_name():
    file_name = "config_with_no_creds.toml"
    return os.path.join(NED_UNIT_TEST_FIXTURES_FILE_PATH, file_name)


@pytest.fixture
def config_file_invalid():
    file_name = "config_invalid.toml"
    return os.path.join(NED_UNIT_TEST_FIXTURES_FILE_PATH, file_name)
