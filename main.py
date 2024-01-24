import minimalmodbus
import json
import time
from datetime import datetime

SERPORT = 'COM3' # '/dev/ttyUSB0'
SERTIMEOUT = 0.5
SERBAUD = 19200

INTERVAL = 1

# Registers to retrieve data for
register_map = {
    25201 : ["workState", "Work state", 1, "map", {
        0 : "PowerOn",
        1 : "SelfTest",
        2 : "OffGrid",
        3 : "Grid-Tie",
        4 : "Bypass",
        5 : "Stop",
        6 : "Grid Charging"}],
    25205 : ["batteryVolage", "Battery voltage", 0.1, "V"],
    25206 : ["inverterVoltage", "Inverter voltage", 0.1, "V"],
    25207 : ["gridVoltage", "Grid voltage", 0.1, "V"],
    25208 : ["busVoltage", "BUS voltage", 0.1, "V"],
    25209 : ["controlCurrent", "Control current", 0.1, "A"],
    25210 : ["inverterCurrent", "Inverter current", 0.1, "A"],
    25211 : ["gridCurrent", "Grid current", 0.1, "A"],
    25212 : ["loadCurrent", "Load current", 0.1, "A"],
    25213 : ["inverterPower", "Inverter power(P)", 1, "W"],
    25214 : ["gridPower", "Grid power(P)", 1, "W"],
    25215 : ["loadPower", "Load power(P)", 1, "W"],
    25216 : ["loadPercent", "Load percent", 1, "%"],
    25217 : ["inverterComplexPower", "Inverter complex power(S)", 1, "VA"],
    25218 : ["gridComplexPower", "Grid complex power(S)", 1, "VA"],
    25219 : ["loadComplexPower", "Load complex power(S)", 1, "VA"],
    25221 : ["inverterReactivePower", "Inverter reactive power(Q)", 1, "var"],
    25222 : ["gridReactivePower", "Grid reactive power(Q)", 1, "var"],
    25223 : ["loadReactivePower", "Load reactive power(Q)", 1, "var"],
    25225 : ["inverterFrequency", "Inverter frequency", 0.01, "Hz"],
    25226 : ["gridFrequency", "Grid frequency", 0.01, "Hz"],
    25233 : ["acRadiatorTemperature", "AC radiator temperature", 1, "C"],
    25234 : ["transformerTemperature", "Transformer temperature", 1, "C"],
    25235 : ["dcRadiatorTemperature", "DC radiator temperature", 1, "C"],
    25273 : ["batteryPower", "Battery power", 1, "W"],
    25274 : ["batteryCurrent", "Battery current", 1, "A"],
}

output = {}

def read_register_values(i, startreg, count):
    register_id = startreg
    results = i.read_registers(startreg, count)
    for r in results:
        if register_id in register_map:
            r_key = register_map[register_id][0]
            r_name = register_map[register_id][1]
            r_unit = register_map[register_id][2]
            r_label = register_map[register_id][3]

            if register_map[register_id][3] == "map":
                r_value = register_map[register_id][4][r]
            else:
                r_value = str(round(r * r_unit, 2)) + r_label

            output[r_key] = r_value
        
        register_id += 1

    json_object = json.dumps(output)
    print(datetime.now())
    print(json_object)

infinite = True

while infinite:
    i = minimalmodbus.Instrument(SERPORT, 4)
    i.serial.timeout=SERTIMEOUT
    i.serial.baudrate = SERBAUD
    read_register_values(i, 25201, 75)

    # infinite = False

    if infinite:
        time.sleep(INTERVAL)

