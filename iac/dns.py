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
    def from_aws(zone: dict) -> HostedZoneSelf:
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

    @staticmethod
    def to_dict(record: ResourceRecordSelf) -> dict:
        return record.__dict__

    def matches(self, host: str) -> bool:
        return host == self.fqdn or host == self.fqdn[:-1]


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

        return HostedZone.from_aws(hosted_zones[0])


    def change_a_record(self, op: str, host: str, ip: str) -> dict:
        if op not in {"CREATE", "DELETE"}:
            raise IACError(
                IACErrorCode.INVALID_DNS_A_RECORD_OPERAION,
                f"Invalid operation on an A record operation '{op}'",
            )

        zone = self._hosted_zone(host)

        return self._client.change_resource_record_sets(
            HostedZoneId=zone.hz_id,
            ChangeBatch={
                "Changes": [{
                    "Action": op,
                    'ResourceRecordSet': {
                        'Name': host,
                        'Type': "A",
                        "TTL": 300,
                        'ResourceRecords': [{ 'Value': ip }],
                    }
                }]
            }
        )


    def create_a_record(self, host: str, ip: str) -> None:
        self.change_a_record('CREATE', host, ip)

    def delete_a_record(self, host: str, ip: str) -> None:
        self.change_a_record('DELETE', host, ip)

    def fetch_a_record(self, host: str) -> None:
        zone = self._hosted_zone(host)
        response = self._client.list_resource_record_sets(
                HostedZoneId=zone.hz_id,
                StartRecordName=host,
                StartRecordType='A',
                MaxItems='1',
            )

        record_sets = response['ResourceRecordSets']
        if len(record_sets) != 1:
            raise IACError(
                IACErrorCode.UNEXPECTED_NUMBER_OF_RECORDS,
                f"Expected 1 record for '{host}' received {len(record_sets)}",
            )

        record = ResourceRecord.from_aws(record_sets[0])
        if not record.matches(host):
            raise IACError(
                IACErrorCode.DNS_RECORD_NOT_FOUND,
                f"Did not find DNS Record for '{host}'",
            )

        return record
