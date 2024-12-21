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

SERPORT = os.getenv("SERPORT")
SERTIMEOUT = float(os.getenv("SERTIMEOUT"))
SERBAUD = int(os.getenv("SERBAUD"))

INTERVAL = int(os.getenv("INTERVAL"))

INFLUX_HOST = os.getenv("INFLUX_HOST")
INFLUX_ORGID = os.getenv("INFLUX_ORGID")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")

# Registers to retrieve data for
register_map = {
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

# Get data from External BMS
  109: ["BMS_Battery_Voltage", "BMS Battery Voltage", 0.1 , "V"],
  110: ["BMS_Battery_Current", "BMS Battery Current", 0.1 , "A"],
  111: ["BMS_Battery_Temperature", "BMS Battery Temperature", 1 , "C"],
  112: ["BMS_Battery_Errors", "BMS Battery Error", 1 , ""],
  113: ["BMS_Battery_SOC", "BMS Battery SOC", 1 , "%"],
  114: ["BMS_Battery_SOH", "BMS Battery SOH", 1 , "%"]

}



def read_register_values(i, startreg, count):
    stats_line = ""

    register_id = startreg
    results = i.read_registers(startreg, count)
    for r in results:
        if register_id in register_map:
            r_key = register_map[register_id][0]
            r_unit = register_map[register_id][2]

            if register_map[register_id][3] == "map":
                r_value = '"' + register_map[register_id][4][r] + '"'
            else:
                r_value = str(round(r * r_unit, 2))

            # convert from offset val fix for Inverter power owerload
            if register_id == 25213 or register_id == 25273 or register_id == 25274  or register_id == 25214 or register_id == 110 :
                if float(r_value) > 32000 :
                   r_value =- abs(float(r_value)- 65536)


            stats_line += r_key + "=" + str(r_value) + ","

        register_id += 1

    # Remove comma at the end
    stats_line = stats_line[:-1]

    return stats_line


def send_data(stats):
    url = "{}/api/v2/write?orgID={}&bucket={}".format(
        INFLUX_HOST, INFLUX_ORGID, INFLUX_BUCKET
    )
    data = "inverter " + stats + " " + str(time.time_ns())

    logging.info(data)
    r = requests.post(
        url,
        data=data,
        headers={
            "content-type": "text/plain",
            "Authorization": "Token " + INFLUX_TOKEN,
        },
    )
    logging.info(f"{r.status_code} {r.text}")


infinite = True

while infinite:
    i = minimalmodbus.Instrument(SERPORT, 4)
    i.serial.timeout = SERTIMEOUT
    i.serial.baudrate = SERBAUD
    stats_line_all = read_register_values(i, 15201, 19)
    stats_line_all += "," + read_register_values(i, 25201, 80)
    stats_line_all += "," + read_register_values(i, 20109, 19)
    stats_line_all += "," + read_register_values(i, 109, 6)
    send_data(stats_line_all)


    # infinite = False

    if infinite:
        time.sleep(INTERVAL)
