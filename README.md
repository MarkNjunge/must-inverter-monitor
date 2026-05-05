# must-inverter-monitor

Monitor a MUST inverter and send the stats to InfluxDB (InfluxDB OSS v2).

Tested on a PV-1800.

Original code from [andremiller/must-inverter-python-monitor](https://github.com/andremiller/must-inverter-python-monitor)

## Dependencies

- [uv](https://docs.astral.sh/uv/)
- InfluxDB (Optional)

## Installation

Install dependencies

```
uv sync
```

Create a .env file

```
cp .env.sample .env
```

## Configuration

| Variable         | Description                                                                    | Default |
|------------------|--------------------------------------------------------------------------------|---------|
| `SERPORT`        | Serial port for the inverter (e.g. `COM3` in Windows, `/dev/ttyUSB0` in Linux) | `COM3`  |
| `SERTIMEOUT`     | Serial port read timeout in seconds                                            | `0.5`   |
| `SERBAUD`        | Serial baud rate                                                               | `19200` |
| `INTERVAL`       | Seconds between each reading                                                   | `1`     |
| `INFINITE`       | Set to `false` to run once and exit                                            | `true`  |
| `INFLUX_ENABLED` | Enable sending to InfluxDB                                                     | `false` |
| `INFLUX_HOST`    | InfluxDB host URL                                                              | —       |
| `INFLUX_ORGID`   | InfluxDB organisation ID                                                       | —       |
| `INFLUX_BUCKET`  | InfluxDB bucket name                                                           | —       |
| `INFLUX_TOKEN`   | InfluxDB API token                                                             | —       |

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

## Docker

The app is compatible with docker.

> Only tested on Linux (Fedora, Rasberry Pi)

```shell
docker build -t must-inverter-monitor .

# ARM compatible
docker buildx build --platform linux/amd64,linux/arm64 -t must-inverter-monitor .
```

The [docker-compose.yml](docker-compose.yml) provides a sample, but some changes will be needed depending on your setup.

Setup the logs directory:

```shell
# Get your <user_id>
id -u

# Get your <group_id>
id -g

# Create the logs dir
mkdir -p /opt/must-inverter/logs

# Update the ownership
chown <user_id>:<group_id> /opt/must-inverter/logs
```

Get the `<group_id>` for `/dev/ttyUSB0`. This is **not** expected to be the same as your user's group. 

```shell
# Get the dialout <group_id>
getent group dialout

# If the above fails, get the id from /dev/ttyUSB0
ls -n /dev/ttyUSB0 | awk '{print $4}'
```

Update the `docker-compose.yml`:
- Replace `<user_id>` with **your** user id.
- Replace `<group_id>` with the group id for `/dev/ttyUSB0`

```yaml
# e.g
user: "1000:18"
```
