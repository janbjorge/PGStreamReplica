from __future__ import annotations
import asyncio
import struct
import re
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from typing import Generator


@dataclass
class TableOperation:
    schema: str
    table: str
    operation: str
    when: datetime

    @staticmethod
    def from_x_log_data(
        obj: XLogData,
        pattern=re.compile(rb"table (\w+)\.(\w+): (\w+):"),
        dt_base=datetime(year=2000, month=1, day=1, tzinfo=timezone.utc),
    ) -> TableOperation | None:
        if match := pattern.search(obj.data):
            schema, table, operation = match.groups()
            return TableOperation(
                schema=schema.decode(),
                table=table.decode(),
                operation=operation.decode(),
                when=dt_base + timedelta(microseconds=obj.clock),
            )
        return None


@dataclass
class XLogData:
    # https://www.postgresql.org/docs/16/protocol-replication.html#PROTOCOL-REPLICATION-XLOGDATA
    type: str
    start: int
    stop: int
    clock: int
    data: bytes

    @staticmethod
    def from_bytes(raw: bytes) -> XLogData:
        cqqq_len = 1 + 3 * 8
        type, start, stop, clock = struct.unpack("!cqqq", raw[:cqqq_len])
        return XLogData(
            type=type.decode(),
            start=start,
            stop=stop,
            clock=clock,
            data=raw[cqqq_len:],
        )


@dataclass
class XPrimaryKeepaliveMessage:
    # https://www.postgresql.org/docs/16/protocol-replication.html#PROTOCOL-REPLICATION-PRIMARY-KEEPALIVE-MESSAGE
    type: str
    wal_end: int
    clock: int
    high_urgency: int

    @staticmethod
    def from_bytes(raw: bytes) -> XPrimaryKeepaliveMessage:
        type, wal_end, clock, high_urgency = struct.unpack("!cqqb", raw)
        return XPrimaryKeepaliveMessage(
            type=type,
            wal_end=wal_end,
            clock=clock,
            high_urgency=high_urgency,
        )


@dataclass
class Header:
    type: str
    length: int

    @staticmethod
    def from_bytes(raw: bytes) -> Header:
        type, length = struct.unpack("!cI", raw)
        return Header(
            type=type.decode(),
            length=length,
        )


@dataclass
class ParameterStatus:
    # https://www.postgresql.org/docs/16/protocol-message-formats.html#PROTOCOL-MESSAGE-FORMATS-QUERY
    name: str
    value: str

    @staticmethod
    def from_bytes(raw: bytes) -> ParameterStatus:
        # Skip header first 5, ignore null termination.
        name, value = raw[:-1].split(b"\x00", maxsplit=2)
        return ParameterStatus(
            name=name.decode(),
            value=value.decode(),
        )


@dataclass
class ErrorResponse:
    # https://www.postgresql.org/docs/16/protocol-message-formats.html#PROTOCOL-MESSAGE-FORMATS-ERRORRESPONSE
    severity: str
    message: str

    @staticmethod
    def from_bytes(raw: bytes) -> ErrorResponse:
        # Looks flaky, works for now.
        lookup = {x[:1]: x[1:] for x in raw.split(b"\x00")}
        return ErrorResponse(
            severity=lookup[b"V"].decode(),
            message=lookup[b"M"].decode(),
        )


@dataclass
class CopyData:
    data: bytes

    @staticmethod
    def from_bytes(raw: bytes) -> CopyData:
        return CopyData(data=raw)

    def parse(self) -> XLogData | XPrimaryKeepaliveMessage:
        match chr(self.data[0]):
            case "k":
                return XPrimaryKeepaliveMessage.from_bytes(self.data)
            case "w":
                return XLogData.from_bytes(self.data)
            case _:
                raise NotImplementedError(self.data)


def create_standby_status_update(
    wal_receive_lsn: int,
    wal_flush_lsn: int,
    wal_apply_lsn: int,
    wal_time_lsn: int,
    reply_requested: int = 0,
) -> bytes:
    # https://www.postgresql.org/docs/16/protocol-replication.html#PROTOCOL-REPLICATION-STANDBY-STATUS-UPDATE
    # Define the message type for a Standby Status Update
    return struct.pack(
        "!cQQQQB",
        b"r",
        wal_receive_lsn,
        wal_flush_lsn,
        wal_apply_lsn,
        wal_time_lsn,
        reply_requested,
    )


def create_copy_data(data: bytes) -> bytes:
    # https://www.postgresql.org/docs/16/protocol-message-formats.html#PROTOCOL-MESSAGE-FORMATS-COPYDATA
    return b"d" + bytearray((len(data) + 4).to_bytes(4, "big")) + data


def parse(
    sequence: bytes,
) -> Generator[
    CopyData | ParameterStatus | ErrorResponse,
    None,
    None,
]:
    while sequence:
        header = Header.from_bytes(sequence[:5])

        # Drop header
        to_parse = sequence[5 : header.length + 1]

        sequence = sequence[header.length + 1 :]

        match header.type:
            case "d":
                yield CopyData.from_bytes(to_parse)
            case "S":
                yield ParameterStatus.from_bytes(to_parse)
            case "E":
                yield ErrorResponse.from_bytes(to_parse)
            case "K":
                ...
            case "R":
                ...
            case "W":
                ...
            case "Z":
                ...
            case _:
                raise NotImplementedError(header)


def create_startup_packet(
    user: str = "testuser",
    database: str = "testdb",
) -> bytes:
    # https://www.postgresql.org/docs/16/protocol-message-formats.html#PROTOCOL-MESSAGE-FORMATS-STARTUPMESSAGE
    # Start with protocol version number: 3.0
    packet = bytearray([0x00, 0x03, 0x00, 0x00])

    # Add parameter pairs, each pair followed by null terminator
    parameters = [
        ("user", user),
        ("database", database),
        ("replication", "database"),
        # You can add more parameters here as needed
    ]
    for param, value in parameters:
        packet.extend(f"{param}\x00{value}\x00".encode("utf-8"))

    # Add a final null byte to indicate the end of parameter entries
    packet.append(0x00)

    # Prepend length of the packet including the length field itself
    length = len(packet) + 4  # 4 bytes for the length field
    packet = bytearray(length.to_bytes(4, "big")) + packet

    return bytes(packet)


def query(string: str) -> bytes:
    # https://www.postgresql.org/docs/16/protocol-message-formats.html#PROTOCOL-MESSAGE-FORMATS-QUERY
    return (
        b"Q"
        + (len(string) + 5).to_bytes(4, byteorder="big")
        + string.encode("utf-8")
        + b"\x00"
    )


async def listen(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    buffsize: int = 4096,
) -> None:
    # Register
    writer.write(create_startup_packet())
    await writer.drain()
    for x in parse(await reader.read(buffsize)):
        print(x)

    # Start logical on slot 'test', created in `init_db.sh`.
    start_replication_command = query("START_REPLICATION SLOT test LOGICAL 0/0")
    writer.write(start_replication_command)
    await writer.drain()
    for x in parse(await reader.read(buffsize)):
        print(x)

    while True:
        if recved := (await reader.read(buffsize)):
            for x in (x for x in parse(recved) if isinstance(x, CopyData)):
                event = x.parse()

                if isinstance(event, XLogData) and (
                    to := TableOperation.from_x_log_data(event)
                ):
                    print(to)

                # Only need to keep the connection up.
                if isinstance(event, XPrimaryKeepaliveMessage):
                    writer.write(
                        create_copy_data(
                            create_standby_status_update(
                                event.wal_end,
                                event.wal_end,
                                event.wal_end,
                                event.clock,
                            )
                        )
                    )
                    await writer.drain()


async def main(addr: str = "127.0.0.1", port: int = 5432) -> None:
    reader, writer = await asyncio.open_connection(addr, port)
    try:
        await listen(reader, writer)
    finally:
        await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
