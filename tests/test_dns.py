from unittest.mock import Mock

from pytest import mark, raises

import iac


@mark.parametrize(
    "name, want_domain, want_subdomain",
    [
        ("a.b.c", "b.c", "a"),
        ("a.b.c.d.e.f", "e.f", "a.b.c.d"),
        ("b.c", "b.c", None),
    ],
)
def test_parse_domain_name__happy_path(name, want_domain, want_subdomain):
    got_domain, got_subdomain = iac.dns.parse_domain_name(
        name,
        require_subdomain=False,
    )
    assert want_domain == got_domain
    assert want_subdomain == got_subdomain


@mark.parametrize("name", ["invalid", "not.enough", "trailing.stop.com."])
def test_parse_domain_name__malformed(name):
    with raises(iac.IACException) as exc_info:
        iac.dns.parse_domain_name(name)

    assert exc_info.value.error_code == iac.IACErrorCode.INVALID_DOMAIN_NAME


def test_hosted_zone__from_aws__happy_path(aws_parrot):
    response = aws_parrot.list_hosted_zones_by_name__one_zone
    zone = iac.dns.HostedZone.from_aws(response["HostedZones"][0])
    assert zone == aws_parrot.hosted_zone


def test_resource_record__from_aws__happy_path(aws_parrot):
    response = aws_parrot.list_resource_record_sets__one_record
    record = iac.dns.ResourceRecord.from_aws(response["ResourceRecordSets"][0])
    assert record == aws_parrot.resource_record


@mark.parametrize("name", ["a.bky.sh", "bky.sh"])
def test_dns_manager__descrive_hosted_zone__happy_path(name, aws_parrot):
    dns = Mock()
    dns.list_hosted_zones_by_name.return_value = aws_parrot.list_hosted_zones_by_name__one_zone

    zone = iac.DNSManager(dns).describe_hosted_zone(name)
    assert zone == aws_parrot.hosted_zone

    dns.list_hosted_zones_by_name.assert_called_once()


def test_dns_manager__describe_hosted_zone__fail_to_parse_host():
    dns = Mock()

    with raises(iac.IACException) as exc_info:
        iac.DNSManager(dns).describe_hosted_zone("nope")

    assert exc_info.value.error_code == iac.IACErrorCode.INVALID_DOMAIN_NAME
    dns.assert_not_called()


def test_dns_manager__describe_hosted_zone__unexpected_hosted_zones(aws_parrot):
    dns = Mock()
    dns.list_hosted_zones_by_name.return_value = aws_parrot.list_hosted_zones_by_name__zero_zones

    with raises(iac.IACException) as exc_info:
        iac.DNSManager(dns).describe_hosted_zone("abc.bky.sh")

    assert exc_info.value.error_code == iac.IACErrorCode.INVALID_DOMAIN_NAME
    assert str(exc_info.value).startswith("Error getting host id")
    dns.list_hosted_zones_by_name.assert_called_once()


def test_dns_manager__describe_hosted_zone__hosted_zone_not_found(aws_parrot):
    dns = Mock()
    dns.list_hosted_zones_by_name.return_value = aws_parrot.list_hosted_zones_by_name__one_zone

    with raises(iac.IACException) as exc_info:
        iac.DNSManager(dns).describe_hosted_zone("bbky.sh")

    assert exc_info.value.error_code == iac.IACErrorCode.DOMAIN_NAME_NOT_FOUND
    dns.list_hosted_zones_by_name.assert_called_once()


@mark.parametrize("op", ["CREATE", "DELETE"])
def test_dns_manager__change_a_record__happy_path(op, aws_parrot):
    dns = Mock()
    dns.list_hosted_zones_by_name.return_value = aws_parrot.list_hosted_zones_by_name__one_zone
    dns.change_resource_record_sets.return_value = aws_parrot.change_resource_record_sets__succeess

    iac.DNSManager(dns).change_a_record(op, "abc.bky.sh", "ip-addres")

    dns.list_hosted_zones_by_name.assert_called_once()
    dns.change_resource_record_sets.assert_called_once()


def test_dns_manager__change_a_record__invalid_op():
    dns = Mock()

    with raises(iac.IACException) as exc_info:
        iac.DNSManager(dns).change_a_record("nope", "abc.bky.sh", "ip-addres")

    assert exc_info.value.error_code == iac.IACErrorCode.INVALID_DNS_A_RECORD_OPERAION
    dns.list_hosted_zones_by_name.assert_not_called()
    dns.change_resource_record_sets.assert_not_called()


@mark.parametrize("name", ["a.b.c.bky.sh", "bky.sh"])
def test_dns_manager__list_a_records__happy_path(name, aws_parrot):
    dns = Mock()
    dns.list_hosted_zones_by_name.return_value = aws_parrot.list_hosted_zones_by_name__one_zone
    dns.list_resource_record_sets.return_value = aws_parrot.list_resource_record_sets__many_records

    records = iac.DNSManager(dns).list_a_records(name)

    assert len(records) == 6
    dns.list_hosted_zones_by_name.assert_called_once()
    dns.list_resource_record_sets.assert_called_once()


def test_dns_manager__list_a_records__truncated(aws_parrot):
    dns = Mock()
    dns.list_hosted_zones_by_name.return_value = aws_parrot.list_hosted_zones_by_name__one_zone
    dns.list_resource_record_sets.return_value = aws_parrot.list_resource_record_sets__one_record

    with raises(iac.IACException) as exc_info:
        iac.DNSManager(dns).list_a_records("bky.sh")

    assert exc_info.value.error_code == iac.IACErrorCode.UNEXPECTED_NUMBER_OF_RECORDS
    dns.list_hosted_zones_by_name.assert_called_once()
    dns.list_resource_record_sets.assert_called_once()


def test_dns_manager__describe_a_record__happy_path(aws_parrot):
    dns = Mock()
    dns.list_hosted_zones_by_name.return_value = aws_parrot.list_hosted_zones_by_name__one_zone
    dns.list_resource_record_sets.return_value = aws_parrot.list_resource_record_sets__one_record

    resource_record = iac.DNSManager(dns).describe_a_record("a.b.dlm.bky.sh")

    assert aws_parrot.resource_record == resource_record


def test_dns_manager__describe_a_record__happy_path_no_trailing_stop(aws_parrot):
    dns = Mock()
    dns.list_hosted_zones_by_name.return_value = aws_parrot.list_hosted_zones_by_name__one_zone
    dns.list_resource_record_sets.return_value = aws_parrot.list_resource_record_sets__one_record

    resource_record = iac.DNSManager(dns).describe_a_record("a.b.dlm.bky.sh")

    assert aws_parrot.resource_record == resource_record


def test_dns_manager__describe_a_record__non_matching_record(aws_parrot):
    dns = Mock()
    dns.list_hosted_zones_by_name.return_value = aws_parrot.list_hosted_zones_by_name__one_zone
    dns.list_resource_record_sets.return_value = aws_parrot.list_resource_record_sets__one_record

    with raises(iac.IACException) as exc_info:
        iac.DNSManager(dns).describe_a_record("a.b.c.dlm.bky.sh")

    assert exc_info.value.error_code == iac.IACErrorCode.DNS_RECORD_NOT_FOUND
    dns.list_hosted_zones_by_name.assert_called_once()
    dns.list_resource_record_sets.assert_called_once()


def test_dns_manager__describe_a_record__not_one_record(aws_parrot):
    dns = Mock()
    dns.list_hosted_zones_by_name.return_value = aws_parrot.list_hosted_zones_by_name__one_zone
    dns.list_resource_record_sets.return_value = (
        aws_parrot.list_resource_record_sets__not_one_record
    )

    with raises(iac.IACException) as exc_info:
        iac.DNSManager(dns).describe_a_record("a.b.dlm.bky.sh")

    assert exc_info.value.error_code == iac.IACErrorCode.UNEXPECTED_NUMBER_OF_RECORDS
    dns.list_hosted_zones_by_name.assert_called_once()
    dns.list_resource_record_sets.assert_called_once()
