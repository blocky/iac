from typing import TypeVar
from dataclasses import dataclass

import botocore.client

from iac.exception import IACError, IACErrorCode

def parse_host(host:str) -> (str, str):
    tokens = host.split('.')
    if len(tokens) < 3:
        raise IACError(
            IACErrorCode.INVALID_HOST,
            f"Invalid host '{host}'",
        )

    subdomain = '.'.join(tokens[:-2])
    domain = '.'.join(tokens[-2:])

    return domain, subdomain



HostedZoneSelf = TypeVar("HostedZoneSelf", bound="HostedZone")

@dataclass(frozen=True)
class HostedZone:
    hz_id: str
    fqdn: str

    @staticmethod
    def from_aws_hosted_zone(zone: dict) -> HostedZoneSelf:
        # id is in form of /hostedzone/{HostedZoneId}
        hz_id = zone['Id'].replace("/hostedzone/","")
        fqdn = zone['Name']

        return HostedZone(hz_id=hz_id, fqdn=fqdn)


ResourceRecordSelf = TypeVar("ResourceRecordSelf", bound="ResourceRecord")

@dataclass(frozen=True)
class ResourceRecord:
    fqdn: str
    ip: str
    record_type: str

    def from_aws(data: dict) -> ResourceRecordSelf:
        return ResourceRecord(
            fqdn=data['Name'],
            ip = data['ResourceRecords'][0]['Value'],
            record_type = data['Type'],
        )


class DNSManager:
    def __init__(self, client: botocore.client.BaseClient):
        self._client = client

    def _hosted_zone(self, host: str) -> HostedZone:
        domain, subdomain = parse_host(host)

        response = self._client.list_hosted_zones_by_name(
            DNSName=domain,
            MaxItems='1',
        )

        hosted_zones = response['HostedZones']
        if len(hosted_zones) != 1:
            raise IACError(
                IACErrorCode.INVALID_HOST,
                f"Error getting host id from route 53 for '{host}': '{response}'",
            )

        zone = HostedZone.from_aws_hosted_zone(hosted_zones[0])



#
#
#
#
#
    # response = client.change_resource_record_sets(
    #     HostedZoneId='string',
    #     ChangeBatch={
    #         'Comment': 'string',
    #         'Changes': [
    #             {
    #                 'Action': 'CREATE'|'DELETE'|'UPSERT',
    #                 'ResourceRecordSet': {
    #                     'Name': 'string',
    #                     'Type': 'SOA'|'A'|'TXT'|'NS'|'CNAME'|'MX'|'NAPTR'|'PTR'|'SRV'|'SPF'|'AAAA'|'CAA'|'DS',
    #                     'SetIdentifier': 'string',
    #                     'Weight': 123,
    #                     'Region': 'us-east-1'|'us-east-2'|'us-west-1'|'us-west-2'|'ca-central-1'|'eu-west-1'|'eu-west-2'|'eu-west-3'|'eu-central-1'|'ap-southeast-1'|'ap-southeast-2'|'ap-southeast-3'|'ap-northeast-1'|'ap-northeast-2'|'ap-northeast-3'|'eu-north-1'|'sa-east-1'|'cn-north-1'|'cn-northwest-1'|'ap-east-1'|'me-south-1'|'ap-south-1'|'af-south-1'|'eu-south-1',
    #                     'GeoLocation': {
    #                         'ContinentCode': 'string',
    #                         'CountryCode': 'string',
    #                         'SubdivisionCode': 'string'
    #                     },
    #                     'Failover': 'PRIMARY'|'SECONDARY',
    #                     'MultiValueAnswer': True|False,
    #                     'TTL': 123,
    #                     'ResourceRecords': [
    #                         {
    #                             'Value': 'string'
    #                         },
    #                     ],
    #                     'AliasTarget': {
    #                         'HostedZoneId': 'string',
    #                         'DNSName': 'string',
    #                         'EvaluateTargetHealth': True|False
    #                     },
    #                     'HealthCheckId': 'string',
    #                     'TrafficPolicyInstanceId': 'string',
    #                     'CidrRoutingConfig': {
    #                         'CollectionId': 'string',
    #                         'LocationName': 'string'
    #                     }
    #                 }
    #             },
    #         ]
    #     }
    # )
