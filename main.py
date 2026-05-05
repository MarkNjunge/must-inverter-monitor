import minimalmodbus
import time
import requests
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(
            filename="logs/must_inverter_monitor.log",
            maxBytes=1_000_000,
            backupCount=10,
        ),
    ],
)

SERPORT = os.getenv("SERPORT", "/dev/ttyUSB0")
SERTIMEOUT = float(os.getenv("SERTIMEOUT", "0.5"))
SERBAUD = int(os.getenv("SERBAUD", "19200"))

INTERVAL = int(os.getenv("INTERVAL", "1"))
INFINITE = os.getenv("INFINITE", "true").lower() == "true"

INFLUX_ENABLED = os.getenv("INFLUX_ENABLED", "true").lower() == "true"
INFLUX_HOST = os.getenv("INFLUX_HOST")
INFLUX_ORGID = os.getenv("INFLUX_ORGID")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")

# Registers to retrieve data for
register_map = {
    # Block 25xxx (Main Stats)
    25201: [
        "workState",
        "Work state",
        1,
        "map",
        {
            0: "PowerOn",
            1: "SelfTest",
            2: "OffGrid",
            3: "Grid-Tie",
            4: "Bypass",
            5: "Stop",
            6: "Grid Charging",
        },
    ],
    25205: ["batteryVoltage", "Battery voltage", 0.1, "V"],
    25206: ["inverterVoltage", "Inverter voltage", 0.1, "V"],
    25207: ["gridVoltage", "Grid voltage", 0.1, "V"],
    25208: ["busVoltage", "BUS voltage", 0.1, "V"],
    25209: ["controlCurrent", "Control current", 0.1, "A"],
    25210: ["inverterCurrent", "Inverter current", 0.1, "A"],
    25211: ["gridCurrent", "Grid current", 0.1, "A"],
    25212: ["loadCurrent", "Load current", 0.1, "A"],
    25213: ["inverterPower", "Inverter power(P)", 1, "W"],
    25214: ["gridPower", "Grid power(P)", 1, "W"],
    25215: ["loadPower", "Load power(P)", 1, "W"],
    25216: ["loadPercent", "Load percent", 1, "%"],
    25217: ["inverterComplexPower", "Inverter complex power(S)", 1, "VA"],
    25218: ["gridComplexPower", "Grid complex power(S)", 1, "VA"],
    25219: ["loadComplexPower", "Load complex power(S)", 1, "VA"],
    25221: ["inverterReactivePower", "Inverter reactive power(Q)", 1, "var"],
    25222: ["gridReactivePower", "Grid reactive power(Q)", 1, "var"],
    25223: ["loadReactivePower", "Load reactive power(Q)", 1, "var"],
    25225: ["inverterFrequency", "Inverter frequency", 0.01, "Hz"],
    25226: ["gridFrequency", "Grid frequency", 0.01, "Hz"],
    25233: ["acRadiatorTemperature", "AC radiator temperature", 1, "C"],
    25234: ["transformerTemperature", "Transformer temperature", 1, "C"],
    25235: ["dcRadiatorTemperature", "DC radiator temperature", 1, "C"],

    25237: ["InverterRelayState", "InverterRelayState", 1, "on/off"],
    25238: ["GridRelayState", "GridRelayState", 1, "on/off"],
    25239: ["LoadRelayState", "LoadRelayState", 1, "on/off"],
    25240: ["N_LineRelayState", "N_LineRelayState", 1, "on/off"],
    25241: ["DCRelayState", "DCRelayState", 1, "on/off"],
    25242: ["EarthRelayState", "EarthRelayState", 1, "on/off"],

    25245: ["AccumulatedChargerPowerM", "AccumulatedChargerPowerM", 1, "MWh"],
    25246: ["AccumulatedChargerPower", "AccumulatedChargerPower", 1, "kWh"],
    25247: ["AccumulatedDischargerPowerM", "AccumulatedDischargerPowerM", 1, "MWh"],
    25248: ["AccumulatedDischargerPower", "AccumulatedDischargerPower", 1, "kWh"],
    25249: ["AccumulatedBuyPowerM", "AccumulatedBuyPowerM", 1, "MWh"],
    25250: ["AccumulatedBuyPower", "AccumulatedBuyPower", 1, "kWh"],
    25251: ["AccumulatedSellPowerM", "AccumulatedSellPowerM", 1, "MWh"],
    25252: ["AccumulatedSellPower", "AccumulatedSellPower", 1, "kWh"],
    25253: ["AccumulatedLoadPowerM", "AccumulatedLoadPowerM", 1, "MWh"],
    25254: ["AccumulatedLoadPower", "AccumulatedLoadPower", 1, "kWh"],
    25255: ["AccumulatedSelfUsePowerM", "AccumulatedSelfUsePowerM", 1, "MWh"],
    25256: ["AccumulatedSelfUsePower", "AccumulatedSelfUsePower", 1, "kWh"],
    25257: ["AccumulatedPvSellPowerM", "AccumulatedPvSellPowerM", 1, "MWh"],
    25258: ["AccumulatedPvSellPower", "AccumulatedPvSellPower", 1, "kWh"],
    25259: ["AccumulatedGridChargerPowerM", "AccumulatedGridChargerPowerM", 1, "MWh"],
    25260: ["AccumulatedGridChargerPower", "AccumulatedGridChargerPower", 1, "kWh"],
    25261: ["InverterErrorMessage", "InverterErrorMessage", 1, ""],

    25265: ["InverterWarningMessage", "InverterWarningMessage", 1, ""],

    25273: ["batteryPower", "Battery power", 1, "W"],
    25274: ["batteryCurrent", "Battery current", 1, "A"],

    25279: ["ArrowFlag","Arrow Flag",1,""],


    # Block 20xxx (Config/Mode)
    20109: [
        "EnergyUseMode",
        "Energy use mode",
        1,
        "map",
        {
            0: "-",
            1: "SBU",
            2: "SUB",
            3: "UTI",
            4: "SOL",
        },
    ],

    20111: [
        "Grid_protect_standard",
        "Grid protect standard",
        1,
        "map",
        {
            0: "VDE4105",
            1: "UPS",
            2: "HOME",
            3: "GEN",
        },
    ],
    20112: [
        "SolarUseAim",
        "SolarUse Aim",
        1,
        "map",
        {
            0: "LBU",
            1: "BLU",
        },
    ],
    20113: ["Inv_max_discharger_cur", "Inverter max discharger current", 0.1, "A"],

    20118: ["BatStopDischargingV", "Battery stop discharging voltage", 0.1, "V"],
    20119: ["BatStopChargingV", "Battery stop charging voltage", 0.1, "V"],

    20125: ["GridMaxChargerCurSet", "Grid max charger current set", 0.1, "A"],

    20127: ["BatLowVoltage", "Battery low voltage", 0.1, "V"],
    20128: ["BatHighVoltage", "Battery high voltage", 0.1, "V"],


    # Block 15xxx (MPPT/Charger)
    15201: [
        "ChargerWorkstate",
        "Charger Workstate",
        1,
        "map",
        {
            0: "Initialization",
            1: "Selftest",
            2: "Work",
            3: "Stop",
        },
    ],
    15202: [
        "MpptState",
        "Mppt State",
        1,
        "map",
        {
            0: "Stop",
            1: "MPPT",
            2: "Current limiting",
        },
    ],
    15203: [
        "ChargingState",
        "Charging State",
        1,
        "map",
        {
            0: "Stop",
            1: "Absorb charge",
            2: "Float charge",
            3: "Equalization charge",
        },
    ],

    15205: ["PvVoltage", "Pv. Voltage", 0.1, "V"],
    15206: ["chBatteryVoltage", "Ch. Battery Voltage", 0.1, "V"],
    15207: ["chChargerCurrent", "Ch. Charger Current", 0.1, "A"],
    15208: ["ChargerPower", "Ch. Charger Power", 1, "W"],
    15209: ["RadiatorTemperature", "Ch. Radiator Temperature", 1, "C"],
    15210: ["ExternalTemperature", "Ch. External Temperature", 1, "C"],
    15211: ["BatteryRelay", "Battery Relay", 1, ""],
    15212: ["PvRelay", "Pv. Relay", 1, ""],
    15213: ["ChargerErrorMessage", "Charger Error Message", 1, ""],
    15214: ["ChargerWarningMessage", "Charger Warning Message", 1, ""],
    15215: ["BattVolGrade", "BattVolGrade", 1, "V"],
    15216: ["RatedCurrent", "Rated Current", 0.1, "A"],
    15217: ["AccumulatedPowerM", "Accumulated PowerM", 1 , "MWh"],
    15218: ["AccumulatedPower", "Accumulated Power", 1 , "kWh"],
    15219: ["AccumulatedTimeDay", "Accumulated Time day", 1 , "d"],

    # Block 1xx (External BMS)
    109: ["BMS_Battery_Voltage", "BMS Battery Voltage", 0.1 , "V"],
    110: ["BMS_Battery_Current", "BMS Battery Current", 0.1 , "A"],
    111: ["BMS_Battery_Temperature", "BMS Battery Temperature", 1 , "C"],
    112: ["BMS_Battery_Errors", "BMS Battery Error", 1 , ""],
    113: ["BMS_Battery_SOC", "BMS Battery SOC", 1 , "%"],
    114: ["BMS_Battery_SOH", "BMS Battery SOH", 1 , "%"]
}


def read_register_values(instrument: minimalmodbus.Instrument, startreg: int, count: int) -> dict[str, str | float]:
    data: dict[str, str | float] = {}
    register_id = startreg
    results = instrument.read_registers(startreg, count)
    for r in results:
        if register_id in register_map:
            r_key = register_map[register_id][0]
            r_unit = register_map[register_id][2]
            if register_map[register_id][3] == "map":
                r_value: str | float = register_map[register_id][4][r]
            else:
                r_value = round(r * r_unit, 2)
                # Convert from unsigned to signed for registers that can report negative values
                if register_id in (25213, 25273, 25274, 25214, 110):
                    if r_value > 32000:
                        r_value = r_value - 65536
            data[r_key] = r_value
        register_id += 1
    return data


def send_data_influx(stats: dict[str, str | float]) -> None:
    url = "{}/api/v2/write?orgID={}&bucket={}".format(
        INFLUX_HOST, INFLUX_ORGID, INFLUX_BUCKET
    )
    fields = ",".join(
        f'{k}="{v}"' if isinstance(v, str) else f"{k}={v}"
        for k, v in stats.items()
    )
    data = f"inverter {fields} {time.time_ns()}"
    logging.info(data)
    r = requests.post(
        url,
        data=data,
        headers={
            "content-type": "text/plain",
            "Authorization": "Token " + INFLUX_TOKEN,
        },
    )
    logging.info(f"influx status_code={r.status_code} text={r.text}")

def run_loop():
    instrument = minimalmodbus.Instrument(SERPORT, 4)
    instrument.serial.timeout = SERTIMEOUT
    instrument.serial.baudrate = SERBAUD
    instrument.serial.close_port_after_each_call = True # Help reset bus for some USB-RS485 converters

    try:
        # 1. Read Main Stats
        chunk1 = read_register_values(instrument, 25201, 75)
        time.sleep(0.1)

        # 2. Read Config/Mode
        chunk2 = read_register_values(instrument, 20109, 20)
        time.sleep(0.1)

        # 3. Read MPPT/Charger
        chunk3 = read_register_values(instrument, 15201, 19)
        time.sleep(0.1)

        # 4. Read BMS
        chunk4 = read_register_values(instrument, 109, 6)
        time.sleep(0.1)

        stats = {**chunk1, **chunk2, **chunk3, **chunk4}
        logging.info(stats)

        if INFLUX_ENABLED:
            send_data_influx(stats)

    except minimalmodbus.NoResponseError:
        logging.error("Inverter failed to respond to a request chunk.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    run_loop()

    while INFINITE:
        time.sleep(INTERVAL)
        run_loop()
