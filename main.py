#!/usr/bin/env python3

#  Yury Kuznetsov (WFLM)
#  10.12.2019  20:45


FAN_GPIO = 4
PWM_FREQUENCY_HZ = 20


import pigpio
from simple_pid import PID


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


class FanControl:
    def __init__(self, ip=None, port=None):
        if port and ip:
            self.pi = pigpio.pi(ip, port)
        else:
            self.pi = pigpio.pi()

        self.pi.set_mode(FAN_GPIO, pigpio.OUTPUT)
        self.pi.set_PWM_frequency(FAN_GPIO, PWM_FREQUENCY_HZ)
        self.pi.set_PWM_range(FAN_GPIO, 100)

        self._duty = 0

    @property
    def duty(self):
        return self._duty

    @duty.setter
    def duty(self, value):
        if value < 0:
            self._duty = 0
        elif value > 100:
            self._duty = 100
        else:
            self._duty = value
        self.pi.set_PWM_dutycycle(FAN_GPIO, PWM_FREQUENCY_HZ)

    def __del__(self):
        self.pi.stop()
