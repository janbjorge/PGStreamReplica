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
<socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 64386), raddr=('127.0.0.1', 5432)>
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
TableOperation(schema='public', table='sysconf', operation='UPDATE', when=datetime.datetime(2024, 4, 17, 20, 6, 38, 758228, tzinfo=datetime.timezone.utc))
TableOperation(schema='public', table='sysconf', operation='UPDATE', when=datetime.datetime(2024, 4, 17, 20, 6, 39, 735584, tzinfo=datetime.timezone.utc))
```

## Contributing
Feel free to fork the project and submit pull requests.

## License
MIT License
