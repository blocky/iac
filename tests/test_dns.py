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


def test_hosted_zone__from_aws__happy_path(aws_parrot):
    response = aws_parrot.list_hosted_zones_by_name__one_zone
    zone = iac.dns.HostedZone.from_aws(response["HostedZones"][0])
    assert zone == aws_parrot.hosted_zone


def test_resource_record__from_aws__happy_path(aws_parrot):
    response = aws_parrot.list_resource_record_sets__one_record
    zone = iac.dns.ResourceRecord.from_aws(response["ResourceRecordSets"][0])
    assert zone == aws_parrot.resource_record


@mark.parametrize("host, matches", [
    ("a.b.dlm.bky.sh.", True),
    ("a.b.dlm.bky.sh", True),
    ("x.y.z", False),
])
def test_resource_record__matches(host, matches, aws_parrot):
    assert aws_parrot.resource_record.matches(host) == matches


def test_dns_manager__change_a_record__happy_path(aws_parrot):
    dns = Mock()
    dns.list_hosted_zones_by_name.return_value = \
        aws_parrot.list_hosted_zones_by_name__one_zone
    dns.change_resource_record_sets.return_value = \
        aws_parrot.change_resource_record_sets__succeess

    iac.DNSManager(dns).create_a_record("abc.bky.sh", "ip-addres")

    dns.list_hosted_zones_by_name.assert_called_once()
    dns.change_resource_record_sets.assert_called_once()


def test_dns_manager__change_a_record__fail_to_parse_host(aws_parrot):
    dns = Mock()

    with raises(iac.IACException) as exc_info:
        iac.DNSManager(dns).change_a_record("nope", "invalid-host", "ip-addres")

    assert exc_info.value.error_code == iac.IACErrorCode.INVALID_DNS_A_RECORD_OPERAION
    dns.assert_not_called()


@mark.parametrize("op", ["CREATE", "DELETE"])
def test_dns_manager__change_a_record__fail_to_parse_host(op):
    dns = Mock()

    with raises(iac.IACException) as exc_info:
        iac.DNSManager(dns).change_a_record(op, "invalid-host", "ip-addres")

    assert exc_info.value.error_code == iac.IACErrorCode.INVALID_HOST
    dns.assert_not_called()


@mark.parametrize("op", ["CREATE", "DELETE"])
def test_dns_manager__change_a_record__unexpected_hosted_zones(op, aws_parrot):
    dns = Mock()
    dns.list_hosted_zones_by_name.return_value = \
        aws_parrot.list_hosted_zones_by_name__zero_zones

    with raises(iac.IACException) as exc_info:
        iac.DNSManager(dns).create_a_record("abc.bky.sh", "ip-addres")

    assert exc_info.value.error_code == iac.IACErrorCode.INVALID_HOST
    assert str(exc_info.value).startswith("Error getting host id")
    dns.list_hosted_zones_by_name.assert_called_once()


def test_dns_manager__describe_a_record__happy_path(aws_parrot):
    dns = Mock()
    dns.list_hosted_zones_by_name.return_value = \
        aws_parrot.list_hosted_zones_by_name__one_zone
    dns.list_resource_record_sets.return_value = \
        aws_parrot.list_resource_record_sets__one_record

    resource_record = iac.DNSManager(dns).describe_a_record("a.b.dlm.bky.sh.")

    assert aws_parrot.resource_record == resource_record


def test_dns_manager__describe_a_record__happy_path_no_trailing_stop(aws_parrot):
    dns = Mock()
    dns.list_hosted_zones_by_name.return_value = \
        aws_parrot.list_hosted_zones_by_name__one_zone
    dns.list_resource_record_sets.return_value = \
        aws_parrot.list_resource_record_sets__one_record

    resource_record = iac.DNSManager(dns).describe_a_record("a.b.dlm.bky.sh")

    assert aws_parrot.resource_record == resource_record

def test_dns_manager__describe_a_record__non_matching_record(aws_parrot):
    dns = Mock()
    dns.list_hosted_zones_by_name.return_value = \
        aws_parrot.list_hosted_zones_by_name__one_zone
    dns.list_resource_record_sets.return_value = \
        aws_parrot.list_resource_record_sets__one_record

    with raises(iac.IACException) as exc_info:
        resource_record = iac.DNSManager(dns).describe_a_record("a.b.c.dlm.bky.sh.")

    assert exc_info.value.error_code == iac.IACErrorCode.DNS_RECORD_NOT_FOUND
    dns.list_hosted_zones_by_name.assert_called_once()
    dns.list_resource_record_sets.assert_called_once()


def test_dns_manager__describe_a_record__not_one_record(aws_parrot):
    dns = Mock()
    dns.list_hosted_zones_by_name.return_value = \
        aws_parrot.list_hosted_zones_by_name__one_zone
    dns.list_resource_record_sets.return_value = \
        aws_parrot.list_resource_record_sets__not_one_record

    with raises(iac.IACException) as exc_info:
        resource_record = iac.DNSManager(dns).describe_a_record("a.b.dlm.bky.sh.")

    assert exc_info.value.error_code == iac.IACErrorCode.UNEXPECTED_NUMBER_OF_RECORDS
    dns.list_hosted_zones_by_name.assert_called_once()
    dns.list_resource_record_sets.assert_called_once()
