# PGStreamReplica

## Overview
PGStreamReplica is a simple Python client for exploring PostgreSQL's Streaming Replication Protocol, focusing on learning and experimenting with WAL (Write-Ahead Logging).

## Features
- Streams WAL data from PostgreSQL.
- Parses replication messages like `XLogData` and `XPrimaryKeepaliveMessage`.

## Quick Start
**Prerequisites:** Python 3.10+, PostgreSQL with streaming replication configured (demo docker inc.)

**Setup:**
1. Clone the repo: `git clone https://github.com/janbjorge/PGStreamReplica.git`
2. Build and run toy database: `docker build --build-arg="POSTGRES_VERSION=16" -t pgn db && docker run --rm --name pgn -p 5432:5432 pgn`
3. Run the script: `python3 client.py`


## Exmaple output.
The below output is given as a result of updating the sysconf table (in a second terminal).

```bash
PGStreamReplica git:(main) ✗ python3 client.py
<socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 59319), raddr=('127.0.0.1', 5432)>
ParameterStatus(name='in_hot_standby', value='off')
ParameterStatus(name='integer_datetimes', value='on')
ParameterStatus(name='TimeZone', value='Etc/UTC')
ParameterStatus(name='IntervalStyle', value='postgres')
ParameterStatus(name='is_superuser', value='on')
ParameterStatus(name='application_name', value='')
ParameterStatus(name='default_transaction_read_only', value='off')
ParameterStatus(name='scram_iterations', value='4096')
ParameterStatus(name='DateStyle', value='ISO, MDY')
ParameterStatus(name='standard_conforming_strings', value='on')
ParameterStatus(name='session_authorization', value='testuser')
ParameterStatus(name='client_encoding', value='UTF8')
ParameterStatus(name='server_version', value='16.2 (Debian 16.2-1.pgdg120+2)')
ParameterStatus(name='server_encoding', value='UTF8')
XPrimaryKeepaliveMessage(type=b'k', wal_end=30669832, clock=766441270414640, high_urgency=0)
XLogData(type='w', start=30669952, stop=30669952, clock=766441270418457, data=b'BEGIN 735')
XLogData(type='w', start=30669952, stop=30669952, clock=766441270418786, data=b"table public.sysconf: UPDATE: key[character varying]:'updated_at' value[text]:'2024-04-14T22:20:49+02:00'")
XLogData(type='w', start=30670432, stop=30670432, clock=766441270418806, data=b'COMMIT 735')
XPrimaryKeepaliveMessage(type=b'k', wal_end=30949240, clock=766441270421737, high_urgency=0)
XLogData(type='w', start=30949240, stop=30949240, clock=766441272871213, data=b'BEGIN 747')
XLogData(type='w', start=30949240, stop=30949240, clock=766441272871262, data=b"table public.sysconf: UPDATE: key[character varying]:'updated_at' value[text]:'2024-04-14T22:21:12+02:00'")
XLogData(type='w', start=30949416, stop=30949416, clock=766441272871279, data=b'COMMIT 747')
XPrimaryKeepaliveMessage(type=b'k', wal_end=30949416, clock=766441272871299, high_urgency=0)
XLogData(type='w', start=30949416, stop=30949416, clock=766441273593453, data=b'BEGIN 748')
XLogData(type='w', start=30949416, stop=30949416, clock=766441273593514, data=b"table public.sysconf: UPDATE: key[character varying]:'updated_at' value[text]:'2024-04-14T22:21:13+02:00'")
XLogData(type='w', start=30949568, stop=30949568, clock=766441273593527, data=b'COMMIT 748')
XPrimaryKeepaliveMessage(type=b'k', wal_end=30949568, clock=766441273593549, high_urgency=0)
XPrimaryKeepaliveMessage(type=b'k', wal_end=30949624, clock=766441280108936, high_urgency=0)
```

## Contributing
Feel free to fork the project and submit pull requests.

## License
MIT License
