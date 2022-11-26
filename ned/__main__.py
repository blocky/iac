from iac import iac


def main():
    # pylint: disable = no-value-for-parameter
    iac.iac_cmd(**iac.IAC_CMD_KWARGS)


if __name__ == "__main__":
    main()
