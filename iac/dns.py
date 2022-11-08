from typing import TypeVar
from dataclasses import dataclass

import botocore.client

from iac.exception import IACError, IACErrorCode


def parse_domain_name(name: str, require_subdomain=True) -> (str, str):
    if len(name) > 0 and name[-1] == ".":
        raise IACError(
            IACErrorCode.INVALID_DOMAIN_NAME,
            f"Invalid domain name '{name}', trailing stop should be omitted",
        )

    tokens = name.split(".")

    if len(tokens) < 2:
        raise IACError(
            IACErrorCode.INVALID_DOMAIN_NAME,
            f"Invalid domain name '{name}'",
        )

    domain = ".".join(tokens[-2:])
    subdomain = ".".join(tokens[:-2]) if len(tokens) > 2 else None

    if subdomain is None and require_subdomain:
        raise IACError(
            IACErrorCode.INVALID_DOMAIN_NAME,
            f"Subdomain required but received '{name}'",
        )

    return domain, subdomain


HostedZoneSelf = TypeVar("HostedZoneSelf", bound="HostedZone")


@dataclass(frozen=True)
class HostedZone:
    hz_id: str
    fqdn: str

    @staticmethod
    def from_aws(zone: dict) -> HostedZoneSelf:
        # id is in form of /hostedzone/{HostedZoneId}
        hz_id = zone["Id"].replace("/hostedzone/", "")

        # aws provides fqdn with the trailing stop formalization.  To keep
        # things consistent in our code, we remove trailing stops
        fqdn = zone["Name"][:-1]

        return HostedZone(hz_id=hz_id, fqdn=fqdn)


ResourceRecordSelf = TypeVar("ResourceRecordSelf", bound="ResourceRecord")


@dataclass(frozen=True)
class ResourceRecord:
    fqdn: str
    ip: str
    record_type: str

    @staticmethod
    def from_aws(data: dict) -> ResourceRecordSelf:
        return ResourceRecord(
            # aws provides fqdn with the trailing stop formalization.  To keep
            # things consistent in our code, we remove trailing stops
            fqdn=data["Name"][:-1],
            ip=data["ResourceRecords"][0]["Value"],
            record_type=data["Type"],
        )

    @staticmethod
    def to_dict(record: ResourceRecordSelf) -> dict:
        return record.__dict__


class DNSManager:
    def __init__(self, client: botocore.client.BaseClient):
        self._client = client

    def describe_hosted_zone(self, fqdn: str) -> HostedZone:
        domain, _ = parse_domain_name(fqdn, require_subdomain=False)

        response = self._client.list_hosted_zones_by_name(
            DNSName=domain,
            MaxItems="1",
        )

        hosted_zones = response["HostedZones"]
        if len(hosted_zones) != 1:
            raise IACError(
                IACErrorCode.INVALID_DOMAIN_NAME,
                f"Error getting host id from route 53 for '{fqdn}': '{response}'",
            )

        zone = HostedZone.from_aws(hosted_zones[0])
        if zone.fqdn != domain:
            raise IACError(
                IACErrorCode.DOMAIN_NAME_NOT_FOUND,
                f"Error getting host id from route 53 for '{fqdn}'",
            )

        return zone

    def change_a_record(self, operation: str, fqdn: str, ip_address: str) -> dict:
        if operation not in {"CREATE", "DELETE"}:
            raise IACError(
                IACErrorCode.INVALID_DNS_A_RECORD_OPERAION,
                f"Invalid operation on an A record operation '{operation}'",
            )

        zone = self.describe_hosted_zone(fqdn)

        return self._client.change_resource_record_sets(
            HostedZoneId=zone.hz_id,
            ChangeBatch={
                "Changes": [
                    {
                        "Action": operation,
                        "ResourceRecordSet": {
                            "Name": fqdn,
                            "Type": "A",
                            "TTL": 300,
                            "ResourceRecords": [{"Value": ip_address}],
                        },
                    }
                ]
            },
        )

    def create_a_record(self, fqdn: str, ip_address: str) -> None:
        self.change_a_record("CREATE", fqdn, ip_address)

    def delete_a_record(self, fqdn: str, ip_address: str) -> None:
        self.change_a_record("DELETE", fqdn, ip_address)

    def list_a_records(self, fqdn: str, max_items=1000) -> [ResourceRecord]:
        zone = self.describe_hosted_zone(fqdn)
        response = self._client.list_resource_record_sets(
            HostedZoneId=zone.hz_id,
            StartRecordName=fqdn,
            StartRecordType="A",
            MaxItems=str(max_items),
        )

        if response["IsTruncated"]:
            raise IACError(
                IACErrorCode.UNEXPECTED_NUMBER_OF_RECORDS,
                f"Number of recordes excced {max_items}",
            )

        return list(ResourceRecord.from_aws(r) for r in response["ResourceRecordSets"])

    def describe_a_record(self, fqdn: str) -> ResourceRecord:
        zone = self.describe_hosted_zone(fqdn)
        response = self._client.list_resource_record_sets(
            HostedZoneId=zone.hz_id,
            StartRecordName=fqdn,
            StartRecordType="A",
            MaxItems="1",
        )

        record_sets = response["ResourceRecordSets"]
        if len(record_sets) != 1:
            raise IACError(
                IACErrorCode.UNEXPECTED_NUMBER_OF_RECORDS,
                f"Expected 1 record for '{fqdn}' received {len(record_sets)}",
            )

        record = ResourceRecord.from_aws(record_sets[0])
        if fqdn != record.fqdn:
            raise IACError(
                IACErrorCode.DNS_RECORD_NOT_FOUND,
                f"Did not find DNS Record for '{fqdn}'",
            )

        return record
