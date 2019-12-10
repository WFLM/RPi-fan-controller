#!/usr/bin/env python3

#  Yury Kuznetsov (WFLM)
#  10.12.2019  20:45


class CPUTemperatureSensor:
    def __init__(self):
        cpu_temp_sensor_file_path = "/sys/class/thermal/thermal_zone0/temp"
        self.temp_descriptor = open(cpu_temp_sensor_file_path, mode="rb")

    def get_temp(self):
        self.temp_descriptor.seek(0)
        cpu_temperature = self.temp_descriptor.read(6)
        cpu_temperature = float(cpu_temperature) / 1000
        return cpu_temperature

    def __del__(self):
        self.temp_descriptor.close()
