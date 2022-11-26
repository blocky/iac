from typing import TypeVar

import fabric

from ned.key import KeyFile
from ned.instance import Instance


RemoteCMDRunnerSelf = TypeVar("RemoteCMDRunnerSelf", bound="RemoteCMDRunner")

RunResult = fabric.runners.Result
TransferResult = fabric.transfer.Result
Connection = fabric.Connection


def run_result_to_dict(result: RunResult) -> dict:
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "status": result.exited,
    }


class RemoteCMDRunner:
    @classmethod
    def from_instance_and_key_file(
        cls,
        instance: Instance,
        key_file: KeyFile,
    ) -> RemoteCMDRunnerSelf:
        fabric_connection = fabric.Connection(
            host=instance.public_dns_name,
            user=key_file.username,
            connect_kwargs={
                "key_filename": key_file.path,
            },
        )
        return cls(conn=fabric_connection)

    def __init__(self, conn: Connection):
        self._conn = conn

    def copy(self, path: str) -> TransferResult:
        return self._conn.put(path)

    def run(self, cmd: str) -> RunResult:
        return self._conn.run(cmd, hide=True)
