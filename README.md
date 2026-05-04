# must-inverter-monitor

Monitor a MUST inverter and send the stats to InfluxDB.

Tested on a PV-1800.

Original code from [andremiller/must-inverter-python-monitor](https://github.com/andremiller/must-inverter-python-monitor)

## Requirements

- [uv](https://docs.astral.sh/uv/)
- InfluxDB

## Installation

Install dependencies

```
uv sync
```

Create a .env file

```
cp .env.sample .env
```

## Usage

```
uv run main.py
```

### Fixing Permission

If you encounter the following error:

```
serial.serialutil.SerialException: [Errno 13] could not open port /dev/ttyUSB0: [Errno 13] Permission denied: '/dev/ttyUSB0'
```

run the following to get the group that owns the group (`dialout` in this case):

```shell
ls -al /dev/ttyUSB0
# crw-rw---- 1 root dialout 188, 0 May  4 15:03 /dev/ttyUSB0
```

Then add your user to the group:

```shell
sudo usermod -aG dialout $USER
```

Then restart your terminal or run this:
```shell
newgrp dialout
```
