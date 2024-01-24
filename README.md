# must-inverter-monitor

Monitor a MUST inverter and send the stats to InfluxDB.

Tested on a PV-1800.

Original code from [andremiller/must-inverter-python-monitor](https://github.com/andremiller/must-inverter-python-monitor)

## Requirements

- Python
- InfluxDB

## Installation

Install python dependencies

```
pip install -r requirements.txt
```

Create a .env file

```
cp .env .env.sample
```