from iac import iac


def main():
    # pylint: disable = no-value-for-parameter
    iac.iac_cmd(obj={}, auto_envvar_prefix="SEQUENCER_IAC")


if __name__ == "__main__":
    main()
