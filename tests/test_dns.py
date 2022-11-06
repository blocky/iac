from unittest.mock import Mock, patch

from pytest import mark, raises

import iac


@mark.parametrize("host, want_domain, want_subdomain", [
    ("a.b.c", "b.c", "a"),
    ("a.b.c.d.e.f", "e.f", "a.b.c.d"),
])
def test_parse_host__happy_path(host, want_domain, want_subdomain):
    got_domain, got_subdomain = iac.dns.parse_host(host)
    assert want_domain == got_domain
    assert want_subdomain == got_subdomain



@mark.parametrize("host", ["invalid", "not.enough"])
def test_parse_host__malformed(host):
    with raises(iac.IACException) as exc_info:
        iac.dns.parse_host(host)

    assert exc_info.value.error_code == iac.IACErrorCode.INVALID_HOST


def test_hosted_zone__from_aws_hosted_zone__happy_path(aws_parrot):
    response = aws_parrot.list_hosted_zones_by_name__one_zone
    zone = iac.dns.HostedZone.from_aws_hosted_zone(response["HostedZones"][0])
    assert zone == aws_parrot.hosted_zone


def test_resource_record__from_aws__happy_path(aws_parrot):
    response = aws_parrot.list_resource_record_sets
    zone = iac.dns.ResourceRecord.from_aws(response["ResourceRecordSets"][0])
    assert zone == aws_parrot.resource_record



def test_dns_manager__create_a_record__happy_path(aws_parrot):
    pass


def test_dns_manager__create_a_record__fail_to_parse_host(aws_parrot):
    dns = Mock()

    with raises(iac.IACException) as exc_info:
        iac.DNSManager(dns).create_a_record("invalid-host", "ip-addres")

    assert exc_info.value.error_code == iac.IACErrorCode.INVALID_HOST
    dns.assert_not_called()


def test_dns_manager__create_a_record__unexpected_hosted_zones(aws_parrot):
    dns = Mock()
    dns.list_hosted_zones_by_name.return_value = \
        aws_parrot.list_hosted_zones_by_name__zero_zones

    with raises(iac.IACException) as exc_info:
        iac.DNSManager(dns).create_a_record("abc.bky.sh", "ip-addres")

    assert exc_info.value.error_code == iac.IACErrorCode.INVALID_HOST
    assert str(exc_info.value).startswith("Error getting host id")
    dns.list_hosted_zones_by_name.assert_called_once()
