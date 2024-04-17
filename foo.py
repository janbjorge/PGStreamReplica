import re
from dataclasses import dataclass


@dataclass
class XLogData:
    type: str
    start: int
    stop: int
    clock: int
    data: bytes


log_entries = [
    XLogData(
        type="w",
        start=30651264,
        stop=30651264,
        clock=766686148145182,
        data=b"BEGIN 733",
    ),
    XLogData(
        type="w",
        start=30669056,
        stop=30669056,
        clock=766686148145300,
        data=b"COMMIT 733",
    ),
    XLogData(
        type="w",
        start=30669056,
        stop=30669056,
        clock=766686148145341,
        data=b"BEGIN 734",
    ),
    XLogData(
        type="w",
        start=30669056,
        stop=30669056,
        clock=766686148145534,
        data=b"table public.sysconf: INSERT: key[character varying]:'app_name' value[text]:'MyApplication'",
    ),
    XLogData(
        type="w",
        start=30669304,
        stop=30669304,
        clock=766686148145554,
        data=b"table public.sysconf: INSERT: key[character varying]:'app_version' value[text]:'1.0.0'",
    ),
    XLogData(
        type="w",
        start=30669456,
        stop=30669456,
        clock=766686148145567,
        data=b"table public.sysconf: INSERT: key[character varying]:'maintenance_mode' value[text]:'false'",
    ),
    XLogData(
        type="w",
        start=30669616,
        stop=30669616,
        clock=766686148145581,
        data=b"table public.sysconf: INSERT: key[character varying]:'updated_at' value[text]:'2024-02-19 23:01:54.609243+00'",
    ),
    XLogData(
        type="w",
        start=30669832,
        stop=30669832,
        clock=766686148145590,
        data=b"COMMIT 734",
    ),
    XLogData(
        type="w",
        start=30669952,
        stop=30669952,
        clock=766686148147523,
        data=b"table public.users: DELETE: id[integer]:'123'",
    ),
    XLogData(
        type="w",
        start=30990480,
        stop=30990480,
        clock=766686389135088,
        data=b"table public.sysconf: TRUNCATE: (no-flags)",
    ),
]

regex = re.compile(rb"table ([\w\.]+): (\w+):")

for log in log_entries:
    match = regex.search(log.data)
    if match:
        table, operation = match.groups()
        print(f"Table: {table.decode()}, Operation: {operation.decode()}")
